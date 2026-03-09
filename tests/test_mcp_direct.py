#!/usr/bin/env python3
"""
Direct test of LinkedIn MCP server
"""

import json
import httpx
import asyncio


async def test_mcp_direct():
    """Test MCP server directly"""
    print("Testing LinkedIn MCP server directly...")

    base_url = "http://localhost:8001"

    # Test health endpoint
    async with httpx.AsyncClient() as client:
        try:
            # Try different endpoints
            endpoints_to_try = [
                "/health",
                "/",
                "/mcp/info",
                "/info"
            ]

            for endpoint in endpoints_to_try:
                try:
                    response = await client.get(f"{base_url}{endpoint}")
                    print(f"Endpoint {endpoint}: {response.status_code}")
                    if response.status_code == 200:
                        print(f"Response: {response.text[:200]}...")
                except Exception as e:
                    print(f"Error testing {endpoint}: {e}")

            # Try to call a tool
            print("\nTrying to call linkedin_create_post_draft tool...")

            # Try the MCP call format
            tool_call = {
                "method": "tools/call",
                "params": {
                    "name": "linkedin_create_post_draft",
                    "arguments": {
                        "user_id": "test@example.com",
                        "content": "Test post via MCP",
                        "hashtags": ["test", "mcp"],
                        "post_type": "update",
                        "visibility": "connections"
                    }
                }
            }

            response = await client.post(f"{base_url}/mcp/call", json=tool_call)
            print(f"MCP Call response: {response.status_code}")
            if response.status_code == 200:
                print(f"Response: {response.text}")

        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    asyncio.run(test_mcp_direct())