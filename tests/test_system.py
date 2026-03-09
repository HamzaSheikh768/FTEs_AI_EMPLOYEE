#!/usr/bin/env python3
"""
Test script to verify the automated system components are properly set up
"""

import sys
from pathlib import Path

def test_system_setup():
    """Test that all components of the automated system are present"""
    print("[TEST] Testing Automated System Setup...")

    # Check required files exist
    required_files = [
        "filesystem_detector.py",
        "automated_orchestrator.py",
        "start_automated_system.py",
        "AUTOMATED_SYSTEM.md"
    ]

    vault_components = [
        "AI_Employee_Vault/Inbox",
        "AI_Employee_Vault/Needs_Action",
        "AI_Employee_Vault/Done",
        "AI_Employee_Vault/Logs",
        "AI_Employee_Vault/Dashboard.md"
    ]

    all_good = True

    print("\n[INFO] Checking system files...")
    for file in required_files:
        path = Path(file)
        if path.exists():
            print(f"  [OK] {file}")
        else:
            print(f"  [ERROR] {file}")
            all_good = False

    print("\n[INFO] Checking vault structure...")
    for component in vault_components:
        path = Path(component)
        if path.exists():
            print(f"  [OK] {component}")
        else:
            print(f"  [ERROR] {component}")
            all_good = False

    print(f"\n[RESULT] System setup {'[COMPLETE]' if all_good else '[HAS ISSUES]'}")

    if all_good:
        print("\n[INFO] The automated file processing system is ready to run!")
        print("   To start: python start_automated_system.py")

    return all_good

if __name__ == "__main__":
    test_system_setup()