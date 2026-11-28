<!--
Project: AgriVibes MCP Multi Agent Orchestration
Maintained By: D.K.C.N Gomes
Year: 2026
-->

<!-- Developer: D.K.C.Nipuna Gomes -->

# AgriVibe FieldSat MCP Server

FieldSat is a read-only Model Context Protocol (MCP) server that provides
field-level satellite vegetation evidence and weather context for Sri Lankan
agriculture. It is built with FastMCP and exposes four production field
registrations for paddy and tea zones.

The live server combines:

- Copernicus Sentinel-2 L2A statistics for NDVI, vegetation change, and data quality
- Open-Meteo hourly observations and forecasts for rainfall and humidity

The server deliberately reports measurements and data quality rather than
diagnosing crop problems. Its outputs do not replace on-field inspections,
agronomic advice, or ground measurements.

## Registered fields

| Field ID | Name | Crop |
| --- | --- | --- |
| `SL-PADDY-MINNERIYA` | Minneriya Paddy Fields | Paddy |
| `SL-PADDY-SAMMANTHURAI` | Sammanthurai Plains / Gal Oya Scheme | Paddy |
| `SL-PADDY-KALA-WEWA` | Mahaweli System H / Kala Wewa Basin | Paddy |
| `SL-TEA-PEDRO` | Pedro Tea Estate | Tea |

Demo mode adds deterministic verification fields for poor data quality,
provider failures, and slow responses:

| Field ID | Intended result |
| --- | --- |
| `SL-PADDY-POOR` | Successful satellite result with poor data quality |
| `SL-PADDY-SAT-FAIL` | Satellite provider unavailable |
| `SL-PADDY-WEATHER-FAIL` | Weather provider unavailable |
| `SL-PADDY-SLOW` | Delayed satellite response |

Field IDs are case-insensitive and surrounding whitespace is ignored.

## Requirements

- Python 3.12 through 3.14
- [uv](https://docs.astral.sh/uv/) for dependency and environment management

## Installation

```powershell
git clone https://github.com/dkcngomes/agrivibe-mcp-server.git
cd agrivibe-mcp-server
uv sync
```

`uv sync` creates the project environment and installs the package and development
dependencies from `pyproject.toml` and `uv.lock`.

## Quick start: demo mode

Demo mode needs no credentials or network access. It uses fixed evidence and is
the simplest way to try the server or run integration checks.

### Stdio transport

```powershell
uv run fieldsat --demo
```

An MCP host starts this command itself for stdio clients.

### Streamable HTTP transport

```powershell
uv run fieldsat --demo --transport http --host 127.0.0.1 --port 8001
```

The MCP endpoint is:

```text
http://127.0.0.1:8001/mcp
```

The legacy SSE transport is also available:

```powershell
uv run fieldsat --demo --transport sse --host 127.0.0.1 --port 8001
```

Demo mode can also be enabled in the environment:

```powershell
$env:AGRIVIBE_MCP_DEMO="1"
uv run fieldsat
```

## Live mode

Live satellite data requires a Copernicus Data Space OAuth client. Create one
with Sentinel Hub access, then copy `.env.example` to `.env` at the project root:

```dotenv
COPERNICUS_CLIENT_ID=your-client-id
COPERNICUS_CLIENT_SECRET=your-client-secret
```

Environment variables take precedence over values loaded from `.env`.

Start live stdio or HTTP mode:

```powershell
uv run fieldsat
uv run fieldsat --transport http --host 127.0.0.1 --port 8001
```

Live mode uses Copernicus Sentinel-2 L2A through the Sentinel Hub Statistics API
and Open-Meteo without an API key. It refuses to start if either Copernicus
credential is missing.

## MCP client configuration

For a stdio MCP client, use the project directory and this command:

```json
{
  "command": "uv",
  "args": ["run", "fieldsat", "--demo"],
  "cwd": "D:\\path\\to\\agrivibe-mcp-server"
}
```

For live MCP client access, replace `--demo` with the live configuration and
provide the Copernicus credentials in the process environment or `.env`.

## MCP API

### Tools

| Tool | Description |
| --- | --- |
| `list_fields` | Lists all registered fields, names, and crops. |
| `get_satellite_analysis` | Compares Sentinel-2 NDVI for the requested field over the current and previous periods. `comparison_days` is required and accepts 1-90. |
| `get_weather_context` | Returns the last 7 days of rainfall and humidity plus a 48-hour forecast. `historical_days` accepts 1-30 and defaults to 7; `forecast_days` accepts 1-7 and defaults to 2. |

Both evidence tools are read-only and identify provider failures as structured MCP
tool errors.

Example tool call for satellite evidence:

```json
{
  "field_id": "SL-PADDY-MINNERIYA",
  "comparison_days": 14
}
```

Example tool call for weather context:

```json
{
  "field_id": "SL-PADDY-MINNERIYA",
  "historical_days": 7,
  "forecast_days": 2
}
```

### Resources

| URI | Description |
| --- | --- |
| `fields://registry` | JSON profiles for every registered field. |
| `fields://{field_id}` | JSON profile for one field; field geometry stays on the server. |

Field resources expose IDs, names, crops, and time zones, while analysis tools
return only the evidence needed for the selected field.

### Prompts

`field_health_brief` creates instructions for a short field-health brief. It
accepts:

- `field_id` - required field ID
- `audience` - `farmer` or `extension_officer` (default)

The prompt directs the client to call satellite and weather tools, report
measurements only, and clearly flag poor data quality.

## ASGI hosting

The repository includes an ASGI app for uvicorn and platforms that discover
`app.py`. Live credentials are required.

```powershell
uv run uvicorn fieldsat.asgi:app --host 0.0.0.0 --port 8001
```

The ASGI app creates a stateless HTTP MCP server with JSON responses. It loads
`.env` through `python-dotenv`; variables already present in the process
environment take precedence.

## Development

Run the test suite:

```powershell
uv run pytest
```

Run static and style checks:

```powershell
uv run ruff check .
uv run mypy
```

Run the protocol smoke test against both streamable HTTP and legacy client modes:

```powershell
uv run python scripts/smoke_mcp.py
```

The smoke test starts the demo server on a free local port and verifies tool
discovery and real MCP calls.

## Project structure

```text
app.py                 ASGI entry point for platforms
src/fieldsat/
  cli.py               Command-line server launcher
  runtime.py           Demo/live server selection
  server.py            FastMCP registration
  tools/               MCP tool implementations
  resources.py         MCP field resources
  prompts.py           Reusable MCP prompts
  domain/              Evidence contracts and field geometry
  providers/           Copernicus, Open-Meteo, and demo providers
scripts/
  smoke_mcp.py         HTTP protocol integration check
tests/                 Unit and MCP integration tests
```


## Startup Locally : npx @modelcontextprotocol/inspector uv run fieldsat