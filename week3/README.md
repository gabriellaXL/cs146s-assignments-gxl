# Week 3: Open-Meteo MCP Server

Chinese version: [README.zh-CN.md](C:/Users/gabri/Documents/cs146s/modern-software-dev-assignments-master/week3/README.zh-CN.md)

This directory contains a production-style MCP server for the Week 3 assignment. It wraps the public [Open-Meteo](https://open-meteo.com/) APIs and exposes weather lookup capabilities through MCP tools, plus one supporting resource and one prompt for better client UX.

The implementation targets the **local STDIO deployment mode** required by the assignment. It is structured for maintainability rather than as a single-file demo.

## Assignment Coverage

This implementation satisfies the Week 3 requirements by providing:

- A real external API integration using Open-Meteo geocoding and forecast endpoints.
- Two MCP tools:
  - `search_place`
  - `get_current_weather`
- Resilience for:
  - invalid tool inputs
  - HTTP transport errors
  - timeouts
  - HTTP 429 rate limiting
  - upstream 4xx/5xx failures
  - empty results
  - malformed upstream payloads
- Clear setup and run instructions.
- MCP client configuration examples for Cursor and Claude Desktop.
- Example invocation flow and tool reference.
- Minimal automated tests for critical edge cases.

## Project Structure

```text
week3/
├── assignment.md
├── README.md
├── requirements.txt
├── server/
│   ├── app.py
│   ├── config.py
│   ├── errors.py
│   ├── formatters.py
│   ├── logging_utils.py
│   ├── main.py
│   ├── models.py
│   ├── openmeteo_client.py
│   ├── prompts.py
│   ├── resources.py
│   ├── service.py
│   ├── tools.py
│   └── validation.py
└── tests/
    ├── test_openmeteo_client.py
    ├── test_tools.py
    └── test_validation.py
```

## Upstream APIs

This server uses the following Open-Meteo endpoints:

- Geocoding API: `GET https://geocoding-api.open-meteo.com/v1/search`
- Forecast API: `GET https://api.open-meteo.com/v1/forecast`

No API key is required.

## Requirements

- Python 3.10+
- Internet access to `geocoding-api.open-meteo.com` and `api.open-meteo.com`

## Installation

From the repository root:

```bash
pip install -r week3/requirements.txt
```

If you want to run tests and `pytest` is not already installed in your environment:

```bash
pip install pytest
```

## Running the MCP Server

From the repository root:

```bash
python -m week3.server.main
```

This is an **STDIO MCP server**:

- MCP protocol messages are read from stdin and written to stdout.
- Application logs are written to stderr only.
- Do not manually type into the process after starting it in a terminal.
- The normal way to use it is to let an MCP client such as Cursor or Claude Desktop start the process.

## MCP Client Configuration

### Cursor

Create either `.cursor/mcp.json` inside the repository or `%USERPROFILE%\\.cursor\\mcp.json` globally:

```json
{
  "mcpServers": {
    "openmeteo": {
      "type": "stdio",
      "command": "python",
      "args": ["-m", "week3.server.main"],
      "cwd": "${workspaceFolder}"
    }
  }
}
```

After editing the file, fully restart Cursor and inspect **MCP Logs** if the server does not appear.

Important: after adding the config file, open **Cursor Settings > MCP** and make sure the `openmeteo` server is explicitly **Enabled**. A valid config file alone is not always enough if the server is still disabled in the UI.

### Claude Desktop

Edit `%AppData%\\Claude\\claude_desktop_config.json` and add:

```json
{
  "mcpServers": {
    "openmeteo": {
      "command": "python",
      "args": ["-m", "week3.server.main"],
      "cwd": "C:\\\\path\\\\to\\\\modern-software-dev-assignments-master"
    }
  }
}
```

Replace `cwd` with the absolute path to your repository root, then restart Claude Desktop.

## Tool Reference

### `search_place`

Resolves a city or place name into one or more candidate locations.

Parameters:

- `name` (`str`, required): place name to search for.
- `max_results` (`int`, optional, default `5`): maximum number of results, from `1` to `10`.

Example input:

```json
{
  "name": "Beijing",
  "max_results": 2
}
```

Example output:

```text
1. Beijing (China, Beijing)
   Coordinates: 39.9042, 116.4074
```

Expected behavior:

- Rejects blank or overly long place names.
- Rejects `max_results` outside `1..10`.
- Returns a concise "not found" message if no place matches.
- Returns a user-friendly error message if the upstream service fails.

### `get_current_weather`

Fetches current weather conditions for a coordinate pair.

Parameters:

- `latitude` (`float`, required): between `-90` and `90`.
- `longitude` (`float`, required): between `-180` and `180`.

Example input:

```json
{
  "latitude": 39.9042,
  "longitude": 116.4074
}
```

Example output:

```text
Observed at: 2026-03-27T15:00
Conditions: Mostly clear
Temperature: 18.4 C
Feels like: 17.9 C
Relative humidity: 32%
Wind: 11.2 km/h at 210 degrees
```

Expected behavior:

- Rejects invalid latitude/longitude values.
- Returns stable plain-text output for LLM consumption.
- Distinguishes between validation failures, not-found conditions, and upstream service failures.

## Additional MCP Capabilities

Although the assignment requires only tools, this server also includes:

- Resource: `openmeteo://server-info`
  - Gives a concise overview of server behavior, upstream endpoints, and retry policy.
- Prompt: `plan_weather_lookup`
  - Helps a client plan a two-step weather lookup flow.

These are lightweight additions and do not replace the required tools.

## Example Invocation Flow

In a client such as Cursor or Claude Desktop:

1. Ask: `Find the current weather in Beijing.`
2. The client should call `search_place` with `name="Beijing"`.
3. The model chooses the most relevant returned location.
4. The client then calls `get_current_weather` with that result's coordinates.
5. The model summarizes the observed weather and mentions the observation time.

You can also explicitly guide the client:

```text
Use the search_place tool to find Beijing, then call get_current_weather with the returned coordinates.
```

## Reliability and Error Handling

The implementation includes:

- centralized configuration for URLs, timeouts, retry counts, backoff, and user-agent
- input validation before any upstream request
- HTTP timeout handling
- transport error handling
- explicit handling for upstream 429 rate limiting
- explicit handling for upstream 4xx and 5xx responses
- malformed JSON and malformed payload shape detection
- stderr-only logging, safe for STDIO MCP usage

User-facing tool messages are intentionally concise. Developer-facing detail stays in stderr logs.

## Running Tests

From the repository root:

```bash
pytest week3/tests -q
```

The test suite covers:

- invalid tool parameters
- empty search results
- malformed upstream payloads
- upstream timeout translation
- upstream 429 handling
- MCP registration of required tools and resource

## Limitations

- This submission implements the **local STDIO mode**, not remote HTTP transport.
- It does not implement authentication because Open-Meteo does not require an API key.
- Real upstream behavior still depends on network availability and Open-Meteo uptime.

## Verification Notes

In this repository environment, automated tests can verify validation, formatting, and mocked upstream error handling without needing live network access. A full real-network end-to-end run should still be done in Cursor, Claude Desktop, or MCP Inspector on a machine with internet access before final submission.
