"""
Settings for the test agents.

TEST REPO: every value below is FAKE. The hard-coded values are deliberate
"secrets in code" findings for Grafyn to detect. None of them work anywhere.
"""
import os

# --- Hard-coded secrets (deliberate findings) ---------------------------------
PINECONE_API_KEY = "FAKE-pinecone-key-sr-grafyn-test-0000000000"
SNOWFLAKE_PASSWORD = "FAKE-Passw0rd-sr-grafyn-test"

# --- Non-secret config ----------------------------------------------------------
PINECONE_INDEX = "customer-pii-index"

SNOWFLAKE_ACCOUNT = "fake-account-sr-test"
SNOWFLAKE_USER = "SUPPORT_BOT_SVC"
SNOWFLAKE_ROLE = "ACCOUNTADMIN"  # over-privileged role for a support bot (deliberate)

# --- Read from environment (the correct pattern, for comparison) -----------------
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY", "")
CRM_SERVICE_TOKEN = os.environ.get("CRM_SERVICE_TOKEN", "")
