"""HTTP client for the Open-Meteo APIs used by this assignment."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

import httpx

from week3.server.config import OpenMeteoConfig
from week3.server.errors import (
    ResourceNotFoundError,
    UpstreamRateLimitError,
    UpstreamRequestError,
    UpstreamResponseFormatError,
    UpstreamTimeoutError,
)
from week3.server.models import CurrentWeather, PlaceMatch

WMO_LABELS: dict[int, str] = {
    0: "Clear sky",
    1: "Mostly clear",
    2: "Partly cloudy",
    3: "Overcast",
    45: "Fog",
    48: "Depositing rime fog",
    51: "Light drizzle",
    53: "Moderate drizzle",
    55: "Dense drizzle",
    61: "Slight rain",
    63: "Moderate rain",
    65: "Heavy rain",
    71: "Slight snow",
    73: "Moderate snow",
    75: "Heavy snow",
    95: "Thunderstorm",
    96: "Thunderstorm with slight hail",
    99: "Thunderstorm with heavy hail",
}


class OpenMeteoClient:
    """Thin client around Open-Meteo endpoints with retry-aware error handling."""

    def __init__(
        self,
        config: OpenMeteoConfig,
        logger: logging.Logger,
        client: httpx.AsyncClient | None = None,
    ) -> None:
        self._config = config
        self._logger = logger
        self._client = client

    async def search_places(self, name: str, max_results: int) -> list[PlaceMatch]:
        payload = await self._request_json(
            self._config.geocoding_url,
            params={
                "name": name,
                "count": max_results,
                "language": self._config.default_language,
            },
        )

        results = payload.get("results")
        if results in (None, []):
            raise ResourceNotFoundError(
                f"No places matched '{name}'. Try a more specific place name or different spelling."
            )
        if not isinstance(results, list):
            raise UpstreamResponseFormatError("geocoding results were not a list")

        matches: list[PlaceMatch] = []
        for item in results:
            if not isinstance(item, dict):
                raise UpstreamResponseFormatError("geocoding result item was not an object")
            try:
                matches.append(
                    PlaceMatch(
                        name=str(item["name"]),
                        country=str(item["country"]),
                        admin_region=self._optional_str(item.get("admin1")),
                        latitude=float(item["latitude"]),
                        longitude=float(item["longitude"]),
                    )
                )
            except (KeyError, TypeError, ValueError) as exc:
                raise UpstreamResponseFormatError(
                    "geocoding result was missing required fields"
                ) from exc

        return matches

    async def get_current_weather(self, latitude: float, longitude: float) -> CurrentWeather:
        payload = await self._request_json(
            self._config.forecast_url,
            params={
                "latitude": latitude,
                "longitude": longitude,
                "current": (
                    "temperature_2m,relative_humidity_2m,apparent_temperature,"
                    "weather_code,wind_speed_10m,wind_direction_10m"
                ),
                "timezone": "auto",
            },
        )

        current = payload.get("current")
        if not isinstance(current, dict):
            raise UpstreamResponseFormatError("weather payload did not include a current object")

        try:
            weather_code = self._optional_int(current.get("weather_code"))
            return CurrentWeather(
                observed_at=str(current["time"]),
                weather_code=weather_code,
                weather_label=self._weather_label(weather_code),
                temperature_c=self._optional_number(current.get("temperature_2m")),
                apparent_temperature_c=self._optional_number(current.get("apparent_temperature")),
                relative_humidity_percent=self._optional_number(
                    current.get("relative_humidity_2m")
                ),
                wind_speed_kmh=self._optional_number(current.get("wind_speed_10m")),
                wind_direction_degrees=self._optional_number(current.get("wind_direction_10m")),
            )
        except (KeyError, TypeError, ValueError) as exc:
            raise UpstreamResponseFormatError(
                "weather payload was missing required current weather fields"
            ) from exc

    async def _request_json(self, url: str, *, params: dict[str, Any]) -> dict[str, Any]:
        retry = self._config.retry

        if self._client is not None:
            return await self._request_with_retries(self._client, url, params=params)

        headers = {"User-Agent": self._config.user_agent}
        async with httpx.AsyncClient(timeout=retry.timeout_seconds, headers=headers) as client:
            return await self._request_with_retries(client, url, params=params)

    async def _request_with_retries(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        retry = self._config.retry
        backoff = retry.initial_backoff_seconds

        for attempt in range(1, retry.max_attempts + 1):
            try:
                return await self._request_with_client(client, url, params=params)
            except UpstreamRateLimitError:
                self._logger.warning(
                    "Received HTTP 429 from upstream (attempt %s/%s)",
                    attempt,
                    retry.max_attempts,
                )
                if attempt >= retry.max_attempts:
                    raise
                await asyncio.sleep(backoff)
                backoff *= retry.backoff_multiplier

        raise UpstreamRequestError("request failed after retries")

    async def _request_with_client(
        self,
        client: httpx.AsyncClient,
        url: str,
        *,
        params: dict[str, Any],
    ) -> dict[str, Any]:
        try:
            response = await client.get(url, params=params)
        except httpx.TimeoutException as exc:
            self._logger.warning("HTTP timeout during upstream request: %s", url)
            raise UpstreamTimeoutError("request timed out") from exc
        except httpx.RequestError as exc:
            self._logger.warning("HTTP transport error during upstream request: %s", exc)
            raise UpstreamRequestError("transport error") from exc

        if response.status_code == 429:
            raise UpstreamRateLimitError("upstream rate-limited request")
        if response.status_code >= 500:
            self._logger.warning("Upstream server error: HTTP %s", response.status_code)
            raise UpstreamRequestError(f"upstream server error {response.status_code}")
        if response.status_code >= 400:
            self._logger.warning("Upstream client error: HTTP %s", response.status_code)
            raise UpstreamRequestError(f"upstream client error {response.status_code}")

        try:
            payload = response.json()
        except ValueError as exc:
            raise UpstreamResponseFormatError("response was not valid JSON") from exc

        if not isinstance(payload, dict):
            raise UpstreamResponseFormatError("response root was not a JSON object")

        return payload

    @staticmethod
    def _optional_number(value: Any) -> float | int | None:
        if value is None:
            return None
        if isinstance(value, (int, float)):
            return value
        raise ValueError("value was not numeric")

    @staticmethod
    def _optional_int(value: Any) -> int | None:
        if value is None:
            return None
        if isinstance(value, bool):
            raise ValueError("boolean is not a valid integer weather code")
        return int(value)

    @staticmethod
    def _optional_str(value: Any) -> str | None:
        if value is None:
            return None
        return str(value)

    @staticmethod
    def _weather_label(code: int | None) -> str:
        if code is None:
            return "Unknown"
        return WMO_LABELS.get(code, f"Weather code {code}")
