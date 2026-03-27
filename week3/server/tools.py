"""MCP tool registration."""

from __future__ import annotations

import logging

from week3.server.errors import OpenMeteoError, format_user_error
from week3.server.service import WeatherService


def register_tools(mcp, service: WeatherService, logger: logging.Logger) -> None:
    @mcp.tool(
        name="search_place",
        description="Resolve a city or place name into candidate coordinates using Open-Meteo.",
    )
    async def search_place(name: str, max_results: int = 5) -> str:
        try:
            return await service.search_places(name=name, max_results=max_results)
        except OpenMeteoError as exc:
            logger.info("Tool search_place failed: %s", exc)
            return format_user_error(exc)
        except Exception:
            logger.exception("Unexpected unhandled error in search_place")
            return "The server encountered an unexpected error while searching for a place."

    @mcp.tool(
        name="get_current_weather",
        description="Fetch the current weather for a latitude and longitude pair.",
    )
    async def get_current_weather(latitude: float, longitude: float) -> str:
        try:
            return await service.get_current_weather(latitude=latitude, longitude=longitude)
        except OpenMeteoError as exc:
            logger.info("Tool get_current_weather failed: %s", exc)
            return format_user_error(exc)
        except Exception:
            logger.exception("Unexpected unhandled error in get_current_weather")
            return "The server encountered an unexpected error while fetching weather."
