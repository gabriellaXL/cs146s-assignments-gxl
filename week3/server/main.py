"""Open-Meteo MCP server (STDIO). Logs go to stderr only — never print to stdout."""

from __future__ import annotations

import asyncio
import logging
import sys
from typing import Any

import httpx
from mcp.server.fastmcp import FastMCP

GEOCODING_URL = "https://geocoding-api.open-meteo.com/v1/search"
FORECAST_URL = "https://api.open-meteo.com/v1/forecast"
USER_AGENT = "cs146-week3-openmeteo-mcp/1.0"
HTTP_TIMEOUT = 25.0
MAX_RETRIES = 3
BACKOFF_SEC = 1.5

# WMO Weather interpretation codes (subset) — https://open-meteo.com/en/docs
WMO_LABELS: dict[int, str] = {
    0: "晴朗",
    1: "大部晴朗",
    2: "局部多云",
    3: "阴天",
    45: "雾",
    48: "沉积霜雾",
    51: "小毛毛雨",
    53: "中毛毛雨",
    55: "大毛毛雨",
    61: "小雨",
    63: "中雨",
    65: "大雨",
    71: "小雪",
    73: "中雪",
    75: "大雪",
    95: "雷暴",
    96: "雷暴伴冰雹",
    99: "强雷暴伴冰雹",
}

logger = logging.getLogger("openmeteo_mcp")
_handler = logging.StreamHandler(sys.stderr)
_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(message)s"))
logger.addHandler(_handler)
logger.setLevel(logging.INFO)
# STDIO MCP 使用 stdout 传输协议；第三方库的 INFO 日志可能干扰客户端解析
for _noisy in ("httpx", "httpcore"):
    logging.getLogger(_noisy).setLevel(logging.WARNING)


def _weather_label(code: int | None) -> str:
    if code is None:
        return "未知"
    return WMO_LABELS.get(code, f"代码 {code}")


async def _get_json(
    client: httpx.AsyncClient,
    url: str,
    *,
    params: dict[str, Any] | None = None,
) -> dict[str, Any] | None:
    """GET JSON with timeout, retries on 429, graceful failure on other errors."""
    backoff = BACKOFF_SEC
    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = await client.get(url, params=params)
            if response.status_code == 429:
                logger.warning("Rate limited, attempt %s/%s", attempt, MAX_RETRIES)
                if attempt < MAX_RETRIES:
                    await asyncio.sleep(backoff)
                    backoff *= 2
                continue
            response.raise_for_status()
            data = response.json()
            if not isinstance(data, dict):
                logger.error("Unexpected JSON root type: %s", type(data))
                return None
            return data
        except httpx.TimeoutException:
            logger.warning("HTTP timeout on %s", url)
            return None
        except httpx.HTTPStatusError as exc:
            logger.warning("HTTP error: HTTP %s", exc.response.status_code)
            return None
        except httpx.RequestError as exc:
            logger.warning("Request error: %s", exc)
            return None
    return None


mcp = FastMCP("openmeteo")


@mcp.tool()
async def search_place(name: str, max_results: int = 5) -> str:
    """按地名搜索地点，返回名称、国家与经纬度（Open-Meteo 地理编码）。

    Args:
        name: 地名关键词，例如城市名（中英文均可）。
        max_results: 最多返回几条候选，默认 5，最大 10。
    """
    name = (name or "").strip()
    if not name:
        return "错误：地名不能为空。"
    if len(name) > 200:
        return "错误：地名过长（请短于 200 字符）。"

    count = max(1, min(int(max_results), 10))

    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers=headers) as client:
        data = await _get_json(
            client,
            GEOCODING_URL,
            params={"name": name, "count": count, "language": "zh"},
        )

    if data is None:
        return "无法完成地理编码请求（网络错误、超时或服务器异常）。请稍后重试。"

    results = data.get("results")
    if not results:
        return f"未找到与「{name}」匹配的地点。请尝试其它拼写或更具体的地名。"

    lines: list[str] = []
    for i, place in enumerate(results, start=1):
        lat = place.get("latitude")
        lon = place.get("longitude")
        label = place.get("name", "?")
        admin = place.get("admin1") or ""
        country = place.get("country", "?")
        extra = f"，{admin}" if admin else ""
        lines.append(
            f"{i}. {label}（{country}{extra}）\n"
            f"   纬度: {lat}, 经度: {lon}"
        )
    return "\n\n".join(lines)


@mcp.tool()
async def current_weather(latitude: float, longitude: float) -> str:
    """查询某经纬度处的当前天气（气温、体感、湿度、风速、天气现象）。

    Args:
        latitude: 纬度，范围约 -90 到 90。
        longitude: 经度，范围约 -180 到 180。
    """
    if not (-90.0 <= latitude <= 90.0):
        return "错误：纬度必须在 -90 到 90 之间。"
    if not (-180.0 <= longitude <= 180.0):
        return "错误：经度必须在 -180 到 180 之间。"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,relative_humidity_2m,apparent_temperature,"
            "weather_code,wind_speed_10m,wind_direction_10m"
        ),
        "timezone": "auto",
    }
    headers = {"User-Agent": USER_AGENT}
    async with httpx.AsyncClient(timeout=HTTP_TIMEOUT, headers=headers) as client:
        data = await _get_json(client, FORECAST_URL, params=params)

    if data is None:
        return "无法获取天气数据（网络错误、超时或服务器异常）。请稍后重试。"

    current = data.get("current")
    if not isinstance(current, dict):
        return "天气接口返回了空结果或格式异常。"

    temp = current.get("temperature_2m")
    feels = current.get("apparent_temperature")
    rh = current.get("relative_humidity_2m")
    code = current.get("weather_code")
    wspd = current.get("wind_speed_10m")
    wdir = current.get("wind_direction_10m")
    time = current.get("time", "?")

    desc = _weather_label(int(code)) if code is not None else "未知"
    return (
        f"观测时间（当地）: {time}\n"
        f"天气: {desc}\n"
        f"气温: {temp} °C\n"
        f"体感: {feels} °C\n"
        f"相对湿度: {rh} %\n"
        f"风速: {wspd} km/h，风向: {wdir}°"
    )


def main() -> None:
    mcp.run(transport="stdio")


if __name__ == "__main__":
    main()
