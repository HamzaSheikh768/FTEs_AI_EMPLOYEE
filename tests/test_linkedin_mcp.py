#!/usr/bin/env python3
"""
Test script for LinkedIn MCP-based posting
"""

import asyncio
from linkedin_poster_impl import LinkedInPoster


async def main():
    """Test the LinkedIn MCP posting system"""
    print("Testing LinkedIn MCP-based posting system...")
    print("=" * 50)

    # Initialize poster
    poster = LinkedInPoster("AI_Employee_Vault")

    # Check MCP connection
    print("\n1. Checking MCP server connection...")
    connected = await poster.check_mcp_connection()
    if connected:
        print("[OK] MCP server is accessible")
    else:
        print("[ERROR] MCP server is not running or not accessible")
        return

    # Run auto test
    print("\n2. Running auto test...")
    result = await poster.run_auto_test()

    # Report results
    print("\n" + "=" * 50)
    print("TEST RESULTS:")
    print(f"- Test created: {'Yes' if result['test_created'] else 'No'}")
    print(f"- Posts processed: {result['processed']}")
    print(f"- Errors: {result['errors']}")
    print(f"- Success: {'Yes' if result['success'] else 'No'}")

    if result['success']:
        print("\n[SUCCESS] Test post was successfully published to LinkedIn via MCP!")
    else:
        print("\n[FAILED] Test post failed - check error logs for details")


if __name__ == "__main__":
    asyncio.run(main())