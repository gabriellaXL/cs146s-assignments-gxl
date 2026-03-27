"""MCP resources exposed by the Week 3 server."""

from __future__ import annotations

from week3.server.config import OpenMeteoConfig


def register_resources(mcp, config: OpenMeteoConfig) -> None:
    @mcp.resource(
        "openmeteo://server-info",
        name="server_info",
        description="Overview of available tools, upstream APIs, and runtime behavior.",
        mime_type="text/markdown",
    )
    def server_info() -> str:
        return "\n".join(
            [
                "# Open-Meteo MCP Server",
                "",
                "Available tools:",
                "- `search_place(name, max_results)` resolves a place name to coordinates.",
                "- `get_current_weather(latitude, longitude)` fetches current conditions.",
                "",
                "Upstream APIs:",
                f"- Geocoding: `{config.geocoding_url}`",
                f"- Forecast: `{config.forecast_url}`",
                "",
                "Runtime behavior:",
                f"- Timeout: {config.retry.timeout_seconds} seconds",
                f"- Retries on HTTP 429: up to {config.retry.max_attempts} attempts",
                "- Logs are written to stderr only.",
            ]
        )
