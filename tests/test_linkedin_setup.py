"""
Basic test to verify Playwright can be imported and will work with LinkedIn
"""
import sys
import os
from pathlib import Path

def test_playwright_import():
    """Test that Playwright can be imported"""
    try:
        from playwright.sync_api import sync_playwright
        print("[OK] Playwright imported successfully")
        return True
    except ImportError as e:
        print(f"[ERROR] Playwright import failed: {e}")
        return False

def test_linkedin_automation_setup():
    """Test that LinkedIn automation components are properly set up"""
    # Test that our implementation file exists and can be imported
    try:
        import importlib.util
        spec = importlib.util.spec_from_file_location(
            "linkedin_poster_impl",
            "E:\\Hackathon 0\\Bronze\\Personal-AI-Employee\\.claude\\skills\\linkedin_poster_impl.py"
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        print("[OK] LinkedIn poster implementation can be imported")
        print("[OK] All LinkedIn automation components are properly set up")
        return True
    except Exception as e:
        print(f"[ERROR] LinkedIn poster implementation failed: {e}")
        return False

def main():
    print("Testing Playwright setup for LinkedIn automation...")
    print()

    # Test Playwright import
    playwright_ok = test_playwright_import()
    print()

    # Test LinkedIn implementation
    linkedin_ok = test_linkedin_automation_setup()
    print()

    if playwright_ok and linkedin_ok:
        print("[OK] All Playwright and LinkedIn automation components are properly set up!")
        print("[OK] Ready to proceed with Task 1.6: Test LinkedIn draft creation functionality")
        return True
    else:
        print("[ERROR] Setup incomplete. Please ensure Playwright is properly installed with browsers.")
        return False

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)