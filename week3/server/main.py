"""STDIO entrypoint for the Week 3 Open-Meteo MCP server."""

from __future__ import annotations

from week3.server.app import create_mcp_server


def main() -> None:
    server = create_mcp_server()
    server.run(transport="stdio")


if __name__ == "__main__":
    main()
