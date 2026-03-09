"""
Test script to verify LinkedIn draft creation functionality
"""
import os
import sys
from pathlib import Path

# Add the project root to the Python path so we can import the LinkedIn poster
sys.path.insert(0, str(Path(__file__).parent))

import importlib.util
spec = importlib.util.spec_from_file_location("linkedin_poster_impl", "E:\\Hackathon 0\\Bronze\\Personal-AI-Employee\\.claude\\skills\\linkedin_poster_impl.py")
linkedin_poster_module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(linkedin_poster_module)
LinkedInPoster = linkedin_poster_module.LinkedInPoster


def test_linkedin_draft_creation():
    """Test LinkedIn draft creation functionality"""
    print("Testing LinkedIn draft creation...")

    # Create a test vault directory structure
    test_vault_path = Path("test_vault")
    pending_approval_path = test_vault_path / "Pending_Approval"
    pending_approval_path.mkdir(parents=True, exist_ok=True)

    try:
        # Initialize LinkedInPoster with test vault
        poster = LinkedInPoster(vault_path=str(test_vault_path))

        # Test content for the post
        test_content = "This is a test post from the Personal AI Employee system."
        test_hashtags = ["AI", "Automation", "DigitalEmployee"]

        # Create a draft for approval
        approval_file_path = poster.create_post_draft(test_content, test_hashtags)

        print(f"[OK] Created approval file: {approval_file_path}")

        # Verify the file was created
        approval_file = Path(approval_file_path)
        if approval_file.exists():
            print("[OK] Approval file exists on disk")

            # Read and verify content
            with open(approval_file, 'r', encoding='utf-8') as f:
                content = f.read()

            if "type: linkedin_post_approval" in content:
                print("[OK] Approval file has correct type")
            else:
                print("[ERROR] Approval file missing correct type")
                return False

            if test_content in content:
                print("[OK] Test content found in approval file")
            else:
                print("[ERROR] Test content not found in approval file")
                return False

            if "AI" in content and "Automation" in content:
                print("[OK] Hashtags found in approval file")
            else:
                print("[ERROR] Hashtags not found in approval file")
                return False

        else:
            print("[ERROR] Approval file was not created")
            return False

        print("[OK] LinkedIn draft creation functionality working properly")
        return True

    except Exception as e:
        print(f"[ERROR] LinkedIn draft creation test failed: {e}")
        import traceback
        traceback.print_exc()
        return False
    finally:
        # Clean up test files
        import shutil
        if test_vault_path.exists():
            shutil.rmtree(test_vault_path, ignore_errors=True)


def main():
    print("Testing LinkedIn draft creation functionality...")
    print()

    success = test_linkedin_draft_creation()
    print()

    if success:
        print("[OK] LinkedIn draft creation functionality test passed!")
        print("[OK] Ready to proceed with Phase 2: MCP Server Development")
        return True
    else:
        print("[ERROR] LinkedIn draft creation functionality test failed")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)