#!/usr/bin/env python3
"""
Willow MCP Server — Exposes Willow skills to Claude Desktop.

Uses Model Context Protocol (MCP) so Claude Desktop can:
- Check system status
- Query knowledge base
- Add journal entries
- Invoke personas
- Speak text via TTS

Install: pip install mcp
Configure in Claude Desktop settings.json:
{
  "mcpServers": {
    "willow": {
      "command": "python",
      "args": ["C:/path/to/Willow/mcp/willow_server.py"]
    }
  }
}
"""

import asyncio
import json
import sys
from pathlib import Path

import requests
import mcp.server.stdio
import mcp.types as types
from mcp.server import Server
from mcp.server.models import InitializationOptions

WILLOW_BASE = "http://127.0.0.1:8420"

server = Server("willow")


def _call(method: str, path: str, **kwargs) -> dict:
    """Call the Willow API."""
    try:
        if method == "GET":
            r = requests.get(f"{WILLOW_BASE}{path}", timeout=10, **kwargs)
        else:
            r = requests.post(f"{WILLOW_BASE}{path}", timeout=10, **kwargs)
        return r.json()
    except Exception as e:
        return {"error": str(e)}


@server.list_tools()
async def list_tools() -> list[types.Tool]:
    """Declare available Willow tools."""
    return [
        types.Tool(
            name="willow_status",
            description="Check Willow system health — server, daemons, tunnel, disk usage.",
            inputSchema={"type": "object", "properties": {}}
        ),
        types.Tool(
            name="willow_query",
            description="Search Willow knowledge base for information.",
            inputSchema={
                "type": "object",
                "properties": {
                    "query": {"type": "string", "description": "Search query"},
                    "limit": {"type": "integer", "description": "Max results", "default": 10}
                },
                "required": ["query"]
            }
        ),
        types.Tool(
            name="willow_journal",
            description="Add a timestamped entry to the continuity ring journal.",
            inputSchema={
                "type": "object",
                "properties": {
                    "content": {"type": "string", "description": "Journal entry text"},
                    "category": {"type": "string", "description": "Category (note, idea, task, etc.)", "default": "note"}
                },
                "required": ["content"]
            }
        ),
        types.Tool(
            name="willow_persona",
            description="Invoke a Willow persona (PA, Analyst, Archivist, Poet, Debugger) with a prompt.",
            inputSchema={
                "type": "object",
                "properties": {
                    "persona": {"type": "string", "description": "Persona name"},
                    "prompt": {"type": "string", "description": "Prompt for the persona"}
                },
                "required": ["persona", "prompt"]
            }
        ),
        types.Tool(
            name="willow_speak",
            description="Convert text to speech using Willow TTS router.",
            inputSchema={
                "type": "object",
                "properties": {
                    "text": {"type": "string", "description": "Text to speak"},
                    "voice": {"type": "string", "description": "Voice ID (optional)"}
                },
                "required": ["text"]
            }
        ),
        types.Tool(
            name="willow_route",
            description="Route a file through Willow with content extraction and LLM analysis.",
            inputSchema={
                "type": "object",
                "properties": {
                    "file": {"type": "string", "description": "Absolute path to file"}
                },
                "required": ["file"]
            }
        )
    ]


@server.call_tool()
async def call_tool(name: str, arguments: dict) -> list[types.TextContent]:
    """Execute a Willow tool."""
    if name == "willow_status":
        result = _call("GET", "/api/skills/status")

    elif name == "willow_query":
        q = arguments.get("query", "")
        limit = arguments.get("limit", 10)
        result = _call("GET", f"/api/skills/query?q={q}&limit={limit}")

    elif name == "willow_journal":
        result = _call("POST", "/api/skills/journal", json={
            "content": arguments.get("content", ""),
            "category": arguments.get("category", "note")
        })

    elif name == "willow_persona":
        result = _call("POST", "/api/skills/persona", json={
            "persona": arguments.get("persona", "PA"),
            "prompt": arguments.get("prompt", "")
        })

    elif name == "willow_speak":
        result = _call("POST", "/api/tts/speak", json={
            "text": arguments.get("text", ""),
            "voice": arguments.get("voice", "default")
        })
        # TTS returns audio bytes, not JSON — just confirm success
        if isinstance(result, dict) and "error" in result:
            pass  # keep error
        else:
            result = {"success": True, "message": "Audio generated"}

    elif name == "willow_route":
        result = _call("POST", "/api/skills/route", json={
            "file": arguments.get("file", "")
        })

    else:
        result = {"error": f"Unknown tool: {name}"}

    return [types.TextContent(type="text", text=json.dumps(result, indent=2))]


async def main():
    async with mcp.server.stdio.stdio_server() as (read_stream, write_stream):
        await server.run(
            read_stream,
            write_stream,
            InitializationOptions(
                server_name="willow",
                server_version="1.0.0",
                capabilities=server.get_capabilities(
                    notification_options=None,
                    experimental_capabilities={}
                )
            )
        )


if __name__ == "__main__":
    asyncio.run(main())
