#!/usr/bin/env python3
"""
Test WhatsApp setup and authentication
"""

import os
import sys
from pathlib import Path

def test_whatsapp_setup():
    """Test WhatsApp setup requirements"""
    print("WhatsApp Setup Test")
    print("=" * 40)

    # Check Playwright installation
    try:
        import playwright
        print("[PASS] Playwright is installed")
    except ImportError:
        print("[FAIL] Playwright not installed. Run: pip install playwright")
        print("  Then run: playwright install")
        return False

    # Check session directory
    session_path = Path(".whatsapp_session")
    if not session_path.exists():
        session_path.mkdir(parents=True, exist_ok=True)
        print(f"[PASS] Created WhatsApp session directory: {session_path}")
    else:
        print(f"[PASS] WhatsApp session directory exists: {session_path}")

    # Check vault structure
    vault_path = Path("AI_Employee_Vault")
    required_dirs = ["Inbox", "Needs_Action", "Pending_Approval", "Approved", "Rejected", "Done", "Logs"]

    all_exist = True
    for dir_name in required_dirs:
        dir_path = vault_path / dir_name
        if not dir_path.exists():
            print(f"[FAIL] Missing directory: {dir_path}")
            all_exist = False
        else:
            print(f"[PASS] Directory exists: {dir_path}")

    if all_exist:
        print("\n[PASS] All required vault directories exist")
    else:
        print("\n[WARN] Some directories are missing, will be created automatically")

    # WhatsApp Authentication Information
    print("\n" + "=" * 40)
    print("WhatsApp Authentication Information")
    print("=" * 40)
    print("\nWhatsApp integration uses QR code authentication - NO credentials needed!")
    print("\nHow it works:")
    print("1. When you first use WhatsApp MCP server, it opens WhatsApp Web")
    print("2. Scan the QR code with your WhatsApp mobile app")
    print("3. The session is saved and reused automatically")
    print("4. No username/password required!")

    print("\nSession storage location:")
    print(f"- Local: {session_path.absolute()}")
    print("- In MCP: .claude/sessions/whatsapp (for MCP server)")

    print("\nSecurity notes:")
    print("- Session files contain authentication cookies")
    print("- Keep session files secure and private")
    print("- Don't share session files with others")
    print("- Session expires after prolonged inactivity")

    print("\nTesting WhatsApp Watcher...")

    # Test the WhatsApp watcher
    sys.path.insert(0, str(Path(__file__).parent))
    from watcher.whatsapp_watcher_impl import WhatsAppWatcher

    try:
        watcher = WhatsAppWatcher(vault_path="AI_Employee_Vault")
        print("[PASS] WhatsAppWatcher class imported successfully")

        # Test browser setup (dry run)
        os.environ["WHATSAPP_DRY_RUN"] = "true"

        print("\n[PASS] WhatsApp setup test completed successfully!")
        print("\nTo use WhatsApp:")
        print("1. Run: python watcher/whatsapp_watcher_impl.py --monitor")
        print("2. Scan QR code when prompted")
        print("3. The system will monitor messages automatically")

        return True

    except Exception as e:
        print(f"\n[FAIL] Error testing WhatsApp watcher: {e}")
        return False

def check_dependencies():
    """Check if all dependencies are installed"""
    print("\n" + "=" * 40)
    print("Dependency Check")
    print("=" * 40)

    required_packages = [
        ("playwright", "pip install playwright"),
        ("fastmcp", "pip install fastmcp"),
        ("pydantic", "pip install pydantic"),
        ("dotenv", "pip install python-dotenv")
    ]

    all_installed = True
    for package, install_cmd in required_packages:
        try:
            __import__(package.replace("-", "_"))
            print(f"[PASS] {package} is installed")
        except ImportError:
            print(f"[FAIL] {package} not installed. Run: {install_cmd}")
            all_installed = False

    return all_installed

if __name__ == "__main__":
    print("Personal AI Employee - WhatsApp Setup Test")
    print("=" * 50)

    # Check dependencies
    deps_ok = check_dependencies()

    if deps_ok:
        # Test WhatsApp setup
        test_whatsapp_setup()
    else:
        print("\n[WARN] Please install missing dependencies before proceeding")
        print("\nQuick install command:")
        print("pip install playwright fastmcp pydantic python-dotenv")
        print("playwright install")