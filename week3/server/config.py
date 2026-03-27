"""Central configuration for the Week 3 Open-Meteo MCP server."""

from __future__ import annotations

from dataclasses import dataclass, field


@dataclass(frozen=True)
class HttpRetryConfig:
    timeout_seconds: float = 10.0
    max_attempts: int = 3
    initial_backoff_seconds: float = 1.0
    backoff_multiplier: float = 2.0


@dataclass(frozen=True)
class OpenMeteoConfig:
    geocoding_url: str = "https://geocoding-api.open-meteo.com/v1/search"
    forecast_url: str = "https://api.open-meteo.com/v1/forecast"
    user_agent: str = "cs146s-week3-openmeteo-mcp/2.0"
    default_language: str = "en"
    max_place_results: int = 10
    retry: HttpRetryConfig = field(default_factory=HttpRetryConfig)


DEFAULT_CONFIG = OpenMeteoConfig()
