"""Typed domain models for the Week 3 MCP server."""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class PlaceMatch:
    name: str
    country: str
    admin_region: str | None
    latitude: float
    longitude: float


@dataclass(frozen=True)
class CurrentWeather:
    observed_at: str
    weather_code: int | None
    weather_label: str
    temperature_c: float | int | None
    apparent_temperature_c: float | int | None
    relative_humidity_percent: float | int | None
    wind_speed_kmh: float | int | None
    wind_direction_degrees: float | int | None
