"""Stable formatting helpers for MCP tool output."""

from __future__ import annotations

from week3.server.models import CurrentWeather, PlaceMatch


def format_place_matches(matches: list[PlaceMatch]) -> str:
    blocks: list[str] = []
    for index, match in enumerate(matches, start=1):
        region_suffix = f", {match.admin_region}" if match.admin_region else ""
        blocks.append(
            "\n".join(
                [
                    f"{index}. {match.name} ({match.country}{region_suffix})",
                    f"   Coordinates: {match.latitude:.4f}, {match.longitude:.4f}",
                ]
            )
        )
    return "\n\n".join(blocks)


def format_current_weather(weather: CurrentWeather) -> str:
    return "\n".join(
        [
            f"Observed at: {weather.observed_at}",
            f"Conditions: {weather.weather_label}",
            f"Temperature: {weather.temperature_c} C",
            f"Feels like: {weather.apparent_temperature_c} C",
            f"Relative humidity: {weather.relative_humidity_percent}%",
            f"Wind: {weather.wind_speed_kmh} km/h at {weather.wind_direction_degrees} degrees",
        ]
    )
