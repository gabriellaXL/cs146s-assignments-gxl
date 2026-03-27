"""Application service layer for MCP tools."""

from __future__ import annotations

from week3.server.formatters import format_current_weather, format_place_matches
from week3.server.openmeteo_client import OpenMeteoClient
from week3.server.validation import (
    validate_latitude,
    validate_longitude,
    validate_max_results,
    validate_place_name,
)


class WeatherService:
    """Coordinates validation, upstream calls, and stable user-facing formatting."""

    def __init__(self, client: OpenMeteoClient, max_place_results: int) -> None:
        self._client = client
        self._max_place_results = max_place_results

    async def search_places(self, name: str, max_results: int = 5) -> str:
        validated_name = validate_place_name(name)
        validated_max_results = validate_max_results(
            max_results, max_allowed=self._max_place_results
        )
        matches = await self._client.search_places(validated_name, validated_max_results)
        return format_place_matches(matches)

    async def get_current_weather(self, latitude: float, longitude: float) -> str:
        validated_latitude = validate_latitude(latitude)
        validated_longitude = validate_longitude(longitude)
        weather = await self._client.get_current_weather(validated_latitude, validated_longitude)
        return format_current_weather(weather)
