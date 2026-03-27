from __future__ import annotations

import asyncio

from week3.server.app import create_mcp_server


async def _run_search_place_tool_returns_validation_error_message() -> None:
    server = create_mcp_server()
    content, structured = await server.call_tool("search_place", {"name": "", "max_results": 3})
    assert "Input error:" in content[0].text
    assert structured["result"].startswith("Input error:")


async def _run_server_registers_required_tools_and_resource() -> None:
    server = create_mcp_server()

    tools = await server.list_tools()
    tool_names = {tool.name for tool in tools}
    assert {"search_place", "get_current_weather"} <= tool_names

    resources = await server.list_resources()
    resource_names = {resource.name for resource in resources}
    assert "server_info" in resource_names


def test_search_place_tool_returns_validation_error_message_sync() -> None:
    asyncio.run(_run_search_place_tool_returns_validation_error_message())


def test_server_registers_required_tools_and_resource_sync() -> None:
    asyncio.run(_run_server_registers_required_tools_and_resource())
