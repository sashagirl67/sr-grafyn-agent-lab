"""
Legacy MCP helper — NOT imported or used by any agent in this repo.

Kept on purpose to test whether discovery reports unused MCP code as an active
MCP connection (the false positive seen with the AgentCore project template).
"""
from mcp import ClientSession
from mcp.client.streamable_http import streamablehttp_client

LEGACY_MCP_URL = "https://mcp.legacy-tools.example.com/mcp"


async def call_legacy_tool(name: str, args: dict):
    async with streamablehttp_client(LEGACY_MCP_URL) as (read, write, _):
        async with ClientSession(read, write) as session:
            await session.initialize()
            return await session.call_tool(name, args)
