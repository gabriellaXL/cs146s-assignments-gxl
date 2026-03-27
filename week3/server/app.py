"""Application assembly for the Week 3 MCP server."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from week3.server.config import DEFAULT_CONFIG, OpenMeteoConfig
from week3.server.logging_utils import configure_logging
from week3.server.openmeteo_client import OpenMeteoClient
from week3.server.prompts import register_prompts
from week3.server.resources import register_resources
from week3.server.service import WeatherService
from week3.server.tools import register_tools


def create_mcp_server(config: OpenMeteoConfig = DEFAULT_CONFIG) -> FastMCP:
    logger = configure_logging()
    client = OpenMeteoClient(config=config, logger=logger)
    service = WeatherService(client=client, max_place_results=config.max_place_results)

    mcp = FastMCP("openmeteo")
    register_tools(mcp=mcp, service=service, logger=logger)
    register_resources(mcp=mcp, config=config)
    register_prompts(mcp=mcp)
    return mcp
