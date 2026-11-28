# Project: AgriVibes MCP Multi Agent Orchestration
# Maintained By: D.K.C.N Gomes
# Year: 2026

"""The demo server as importable objects, for tests and the protocol smoke script."""

from fieldsat.runtime import create_demo_server

mcp = create_demo_server()
app = mcp.http_app(stateless_http=True, json_response=True)
