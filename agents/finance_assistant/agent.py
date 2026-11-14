"""
Finance assistant agent (LangGraph + OpenAI + MCP + Pinecone).


  - Model:      OpenAI gpt-4.1-mini (via langchain-openai)
  - MCP:        two MCP servers, actually wired into the agent
                  * "market-data"  -> public HTTP endpoint, NO authentication
                  * "crm"          -> HTTP endpoint with a bearer token from env
  - Vector DB:  Pinecone index "customer-pii-index" (customer records -> sensitive data)
  - Tools:      search_customer_records, get_account_balance
  - Identity:   reads CRM_SERVICE_TOKEN (service identity) from the environment
"""
import asyncio
import os

from langchain.agents import create_agent
from langchain_core.tools import tool
from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_openai import ChatOpenAI
from pinecone import Pinecone

from config.settings import PINECONE_API_KEY, PINECONE_INDEX

MODEL = "gpt-4.1-mini"

pc = Pinecone(api_key=PINECONE_API_KEY)
index = pc.Index(PINECONE_INDEX)


@tool
def search_customer_records(query: str) -> str:
    """Search customer profiles (name, email, account number, SSN last 4) in the vector store."""
    res = index.query(vector=[0.0] * 1536, top_k=5, include_metadata=True, filter={"text": query})
    return "\n".join(m["metadata"].get("text", "") for m in res.get("matches", []))


@tool
def get_account_balance(account_id: str) -> str:
    """Return the balance for a customer account."""
    return f"Balance for {account_id}: (placeholder)"


MCP_SERVERS = {
    # Public MCP server with no authentication (should be flagged)
    "market-data": {
        "transport": "streamable_http",
        "url": "https://mcp.market-data.example.com/mcp",
    },
    # Authenticated MCP server using a service token
    "crm": {
        "transport": "streamable_http",
        "url": "https://mcp.crm.example.com/mcp",
        "headers": {"Authorization": f"Bearer {os.environ.get('CRM_SERVICE_TOKEN', '')}"},
    },
}

SYSTEM_PROMPT = (
    "You are a finance assistant for advisors. Look up customer records and balances, "
    "and use market data tools when asked about prices."
)


async def build_agent():
    mcp_client = MultiServerMCPClient(MCP_SERVERS)
    mcp_tools = await mcp_client.get_tools()
    llm = ChatOpenAI(model=MODEL, temperature=0)
    return create_agent(
        model=llm,
        tools=[search_customer_records, get_account_balance, *mcp_tools],
        system_prompt=SYSTEM_PROMPT,
    )


async def main():
    agent = await build_agent()
    result = await agent.ainvoke({"messages": [("user", "What is the balance for account 1001?")]})
    print(result["messages"][-1].content)


if __name__ == "__main__":
    asyncio.run(main())
