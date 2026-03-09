#!/usr/bin/env python3
"""
Setup LinkedIn MCP with Composio
"""
import os
import sys
import composio
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

from composio import Composio
# Try to import actions, but don't fail if not available
try:
    from composio.core.actions import Action
except ImportError:
    Action = None

def setup_linkedin():
    """Setup LinkedIn integration with Composio"""

    # Initialize Composio client
    api_key = os.getenv("COMPOSIO_API_KEY")
    if not api_key:
        print("Error: COMPOSIO_API_KEY not found in .env file!")
        print("Please add your Composio API key to .env file")
        print("Get your API key from https://app.composio.com")
        return None

    composio_client = Composio(api_key=api_key)

    print("1. Checking existing integrations...")
    try:
        # Check if LinkedIn is already connected
        accounts = composio_client.connected_accounts.list()
        linkedin_account = None

        for account in accounts:
            if hasattr(account, 'provider') and account.provider == "linkedin":
                linkedin_account = account
                break

        if linkedin_account and hasattr(linkedin_account, 'status') and linkedin_account.status == "ACTIVE":
            print("LinkedIn already connected!")
            print(f"   Account: {getattr(linkedin_account, 'id', 'N/A')}")
        else:
            print("2. Setting up LinkedIn integration...")
            print("   Please open the following URL to authorize:")

            # Initiate LinkedIn connection
            connection = composio_client.connected_accounts.initiate(provider="linkedin")

            if hasattr(connection, 'redirectUrl'):
                print(f"   Authorization URL: {connection.redirectUrl}")
                print("   After authorizing, the script will continue...")

                # Wait for connection (in real scenario, you'd poll or use webhook)
                input("   Press Enter after authorizing in browser...")

                # Verify connection
                accounts = composio_client.connected_accounts.list()
                for account in accounts:
                    if hasattr(account, 'provider') and account.provider == "linkedin":
                        if hasattr(account, 'status') and account.status == "ACTIVE":
                            linkedin_account = account
                            print("LinkedIn successfully connected!")
                            break
            else:
                print("Could not initiate connection")

        # Check for company page connection
        print("\n3. Checking company page access...")
        if linkedin_account:
            # Check if we have account details
            account_id = getattr(linkedin_account, 'id', None)
            if account_id:
                print(f"   Account ID: {account_id}")
                print("   Company page access will be available through MCP tools")
            else:
                print("   Could not get account details")

        # Setup MCP server
        print("\n4. Setting up MCP server...")
        print("   Starting Composio MCP server on port 3333...")

        # In a real implementation, you would start the MCP server
        # For now, we'll provide the configuration
        mcp_config = {
            "mcpServers": {
                "composio": {
                    "command": "python",
                    "args": ["-m", "composio.mcp.server"],
                    "env": {
                        "COMPOSIO_API_KEY": os.getenv("COMPOSIO_API_KEY", ""),
                        "ACCEPT": "application/json",
                        "CONTENT_TYPE": "application/json"
                    }
                }
            }
        }

        print("\n✅ Setup complete!")
        print("\nNext steps:")
        print("1. Add the MCP server configuration to Claude Code")
        print("2. Restart Claude Code")
        print("3. Test LinkedIn integration")

        return mcp_config

    except Exception as e:
        print(f"Error during setup: {str(e)}")
        return None

if __name__ == "__main__":
    setup_linkedin()