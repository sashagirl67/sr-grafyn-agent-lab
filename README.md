# sr-grafyn-agent-lab

Test repository for Grafyn code-repository and MCP discovery. Owner: Saswati Rao.

**Nothing here is meant to run.** All endpoints use `example.com`, and every key, password and
account in `config/settings.py` is fake. Cost to test: $0.

## What's in it

| Path | What it is |
|---|---|
| `agents/finance_assistant/agent.py` | LangGraph agent, OpenAI `gpt-4.1-mini`, 2 MCP servers wired in, Pinecone vector DB with customer PII |
| `agents/support_bot/agent.py` | Strands agent, Claude Sonnet on Amazon Bedrock, Snowflake orders data, a refund tool, no MCP |
| `legacy/old_mcp_helper.py` | MCP client code that nothing imports (unused-code test) |
| `config/settings.py` | Hard-coded fake secrets + over-privileged Snowflake role |
| `.vscode/mcp.json` | Workspace MCP config: filesystem server on `C:\`, GitHub MCP, an unauthenticated internal wiki MCP |

## Setup

1. On github.com, create a **private** repository named `sr-grafyn-agent-lab` (no README).
2. Push this folder (PowerShell, from inside the unzipped folder):
   ```powershell
   git init
   git add .
   git commit -m "Grafyn discovery test repo"
   git branch -M main
   git remote add origin https://github.com/<your-username>/sr-grafyn-agent-lab.git
   git push -u origin main
   ```
   (Use git rather than drag-and-drop on github.com: browser uploads can skip the `.vscode` folder.)
3. In Grafyn: **Integrations → New → Code Repositories → GitHub**. Name it `sr-github-agent-lab`.
   If it asks for a token, create a **fine-grained personal access token** scoped to this one
   repository with **read-only** Contents and Metadata.
4. Run jobs: **Agent Discovery**, then **MCP Discovery**, then **Policy Evaluation**.

## Answer key: what Grafyn should find

### Agents (2)
| Agent | Framework | Model | Tools | Data | MCP |
|---|---|---|---|---|---|
| finance_assistant | LangGraph | OpenAI gpt-4.1-mini | search_customer_records, get_account_balance (+ MCP tools) | Pinecone `customer-pii-index` | market-data, crm |
| support_bot | Strands | Claude Sonnet 4.5 on Bedrock | lookup_order, create_refund | Snowflake RETAIL.PUBLIC.ORDERS / REFUNDS | none |

### MCP servers
| Server | Where | Auth | Used by an agent? | Expected finding |
|---|---|---|---|---|
| market-data | finance_assistant code | **none** | yes | MCP server without authentication |
| crm | finance_assistant code | bearer token from env | yes | OK |
| filesystem | .vscode/mcp.json | n/a (local) | developer IDE | Broad local file access (whole `C:\` drive) |
| github | .vscode/mcp.json | token prompt | developer IDE | OK |
| internal-wiki | .vscode/mcp.json | **none** | developer IDE | MCP server without authentication |
| legacy-tools | legacy/old_mcp_helper.py | none | **no** | Should NOT appear as an active connection (at most "present but unused") |

All `example.com` MCP URLs are unreachable, so discovery health may also report them as unreachable —
that's expected and is itself a useful check.

### Other findings to expect
- **Hard-coded secrets:** `PINECONE_API_KEY`, `SNOWFLAKE_PASSWORD` in `config/settings.py`
- **Over-privileged identity:** support_bot connects to Snowflake as `ACCOUNTADMIN`
- **Sensitive data exposure:** finance_assistant reaches customer PII (vector DB); support_bot reaches
  customer orders and addresses
- **Action risk:** support_bot's `create_refund` moves money with no approval step
- **Not expected:** any MCP server for support_bot; legacy-tools as an active connection

### Comparison with the AWS AgentCore test
Same kind of checks, but plain source code instead of a deployment zip with bundled dependencies.
If the MCP false positives disappear here, the AgentCore issue is the dependency bundle. If
legacy-tools shows up as active, the scanner reports MCP code regardless of whether it's used.
