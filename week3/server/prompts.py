"""Optional MCP prompts for common tool orchestration."""

from __future__ import annotations


def register_prompts(mcp) -> None:
    @mcp.prompt(
        name="plan_weather_lookup",
        description="Generate a short plan for resolving a place name and then fetching weather.",
    )
    def plan_weather_lookup(place_name: str) -> str:
        return "\n".join(
            [
                f"To answer a weather question about '{place_name}':",
                "1. Call `search_place` with the user's place name.",
                "2. Choose the best matching location from the returned candidates.",
                "3. Call `get_current_weather` with that location's coordinates.",
                "4. Summarize the current conditions and mention the observation time.",
            ]
        )
