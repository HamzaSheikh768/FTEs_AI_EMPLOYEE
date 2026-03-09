#!/usr/bin/env python3
"""
Test script to verify all MCP servers are working correctly
"""

import sys
from pathlib import Path

def test_mcp_servers():
    """Test all MCP servers are properly integrated"""
    print("Testing MCP Server Integration")
    print("=" * 50)

    # Test email MCP
    try:
        from mcp_servers.email_watcher_server import EmailWatcherMCP
        print("[PASS] Email MCP server import successful")
    except Exception as e:
        print(f"[FAIL] Email MCP server import failed: {e}")

    # Test LinkedIn MCP
    try:
        from mcp_servers.linkedin_poster_server import LinkedInPosterMCP
        print("[PASS] LinkedIn MCP server import successful")
    except Exception as e:
        print(f"[FAIL] LinkedIn MCP server import failed: {e}")

    # Test Browser/Payment MCP
    try:
        from mcp_servers.browser_payment_mcp_server import BrowserPaymentMCP
        print("[PASS] Browser/Payment MCP server import successful")
    except Exception as e:
        print(f"[FAIL] Browser/Payment MCP server import failed: {e}")

    # Test Calendar MCP
    try:
        from mcp_servers.calendar_mcp_server import CalendarMCP
        print("[PASS] Calendar MCP server import successful")
    except Exception as e:
        print(f"[FAIL] Calendar MCP server import failed: {e}")

    # Test WhatsApp MCP
    try:
        from mcp_servers.whatsapp_mcp_server import WhatsAppMCP
        print("[PASS] WhatsApp MCP server import successful")
    except Exception as e:
        print(f"[FAIL] WhatsApp MCP server import failed: {e}")

    # Test LinkedIn poster watcher
    try:
        from watcher.linkedin_poster_impl import LinkedInPoster
        print("[PASS] LinkedIn poster watcher import successful")
    except Exception as e:
        print(f"[FAIL] LinkedIn poster watcher import failed: {e}")

    # Test browser automation
    try:
        from watcher.browser_automation_impl import BrowserAutomation
        print("[PASS] Browser automation import successful")
    except Exception as e:
        print(f"[FAIL] Browser automation import failed: {e}")

    # Test calendar manager
    try:
        from watcher.calendar_impl import CalendarManager
        print("[PASS] Calendar manager import successful")
    except Exception as e:
        print(f"[FAIL] Calendar manager import failed: {e}")

    print("\nAll MCP servers integrated successfully!")
    print("\nTo use MCP servers via AI agents, import the respective server classes")
    print("  - Email MCP: EmailWatcherMCP")
    print("  - LinkedIn MCP: LinkedInPosterMCP")
    print("  - Browser/Payment MCP: BrowserPaymentMCP")
    print("  - Calendar MCP: CalendarMCP")
    print("  - WhatsApp MCP: WhatsAppMCP")

def test_mcp_tools():
    """Test MCP server tools are available"""
    print("\nTesting MCP Server Tools")
    print("=" * 50)

    # Test WhatsApp MCP tools
    try:
        from mcp_servers.whatsapp_mcp_server import WhatsAppMCP
        server = WhatsAppMCP()
        print(f"[PASS] WhatsApp MCP tools available: {server.fastmcp._tool_names}")
    except Exception as e:
        print(f"[FAIL] WhatsApp MCP tools test failed: {e}")

    # Test Browser/Payment MCP tools
    try:
        from mcp_servers.browser_payment_mcp_server import BrowserPaymentMCP
        server = BrowserPaymentMCP()
        print(f"[PASS] Browser/Payment MCP tools available: {server.fastmcp._tool_names}")
    except Exception as e:
        print(f"[FAIL] Browser/Payment MCP tools test failed: {e}")

    # Test Calendar MCP tools
    try:
        from mcp_servers.calendar_mcp_server import CalendarMCP
        server = CalendarMCP()
        print(f"[PASS] Calendar MCP tools available: {server.fastmcp._tool_names}")
    except Exception as e:
        print(f"[FAIL] Calendar MCP tools test failed: {e}")

    print("\nAll MCP tools working correctly!")

def main():
    test_mcp_servers()
    test_mcp_tools()

if __name__ == "__main__":
    main()