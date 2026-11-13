"""
Support bot agent (Strands + Anthropic Claude on Amazon Bedrock).

TEST REPO for Grafyn discovery. Not meant to be run.

  - Model:      Claude Sonnet on Amazon Bedrock (via Strands BedrockModel)
  - MCP:        none (this agent uses only local tools)
  - Tools:      lookup_order, create_refund  (create_refund = action that moves money)
  - Data:       orders table in Snowflake (connection details from config.settings)
"""
import snowflake.connector
from strands import Agent, tool
from strands.models import BedrockModel

from config.settings import SNOWFLAKE_ACCOUNT, SNOWFLAKE_USER, SNOWFLAKE_ROLE, SNOWFLAKE_PASSWORD

MODEL_ID = "us.anthropic.claude-sonnet-4-5-20250929-v1:0"


def _conn():
    return snowflake.connector.connect(
        account=SNOWFLAKE_ACCOUNT,
        user=SNOWFLAKE_USER,
        password=SNOWFLAKE_PASSWORD,
        role=SNOWFLAKE_ROLE,  # ACCOUNTADMIN: over-privileged on purpose
        warehouse="COMPUTE_WH",
        database="RETAIL",
        schema="PUBLIC",
    )


@tool
def lookup_order(order_id: str) -> str:
    """Look up an order (customer name, email, shipping address, items, total)."""
    with _conn() as c:
        cur = c.cursor()
        cur.execute("SELECT * FROM ORDERS WHERE ORDER_ID = %s", (order_id,))
        return str(cur.fetchone())


@tool
def create_refund(order_id: str, amount: float) -> str:
    """Issue a refund for an order. No approval step."""
    with _conn() as c:
        c.cursor().execute(
            "INSERT INTO REFUNDS (ORDER_ID, AMOUNT) VALUES (%s, %s)", (order_id, amount)
        )
    return f"Refunded {amount} for order {order_id}"


agent = Agent(
    model=BedrockModel(model_id=MODEL_ID, region_name="us-east-1"),
    tools=[lookup_order, create_refund],
    system_prompt="You are a customer support agent. Help customers with orders and refunds.",
)

if __name__ == "__main__":
    print(agent("Where is my order 5001?"))
