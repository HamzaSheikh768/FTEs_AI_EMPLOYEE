#!/usr/bin/env python3
"""
Test script for LinkedIn Poster functionality
"""

import os
import sys
import time
from pathlib import Path

# Add the project root to the path
sys.path.insert(0, str(Path(__file__).parent))

import sys
from pathlib import Path

# Add the project root and skills directory to the path
sys.path.insert(0, str(Path(__file__).parent))
sys.path.insert(0, str(Path(__file__).parent / ".claude" / "skills"))

from linkedin_poster_impl import LinkedInPoster


def test_linkedin_poster():
    """Test the LinkedIn poster functionality"""
    print("Testing LinkedIn Poster functionality...")

    # Initialize the poster with default vault path
    poster = LinkedInPoster(vault_path="AI_Employee_Vault")

    # Create a test post draft
    test_content = "This is a test LinkedIn post created by the Personal AI Employee system. #AI #Automation #LinkedIn"
    hashtags = ["AI", "Automation", "LinkedIn"]

    print(f"Creating test post draft with content: {test_content}")

    try:
        approval_file_path = poster.create_post_draft(
            content=test_content,
            hashtags=hashtags,
            post_type="update"
        )

        print(f"[PASS] Successfully created approval request: {approval_file_path}")

        # Verify the file exists
        approval_file = Path(approval_file_path)
        if approval_file.exists():
            print(f"[PASS] Approval file exists at: {approval_file_path}")

            # Read the file to verify content
            with open(approval_file, 'r', encoding='utf-8') as f:
                content = f.read()
                print(f"[PASS] File content preview: {content[:200]}...")
        else:
            print(f"[FAIL] Approval file does not exist at: {approval_file_path}")
            return False

        return True

    except Exception as e:
        print(f"[FAIL] Error testing LinkedIn poster: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_approval_workflow():
    """Test the approval workflow by creating and moving a test post"""
    print("\nTesting approval workflow...")

    # Create a sample approval file in Pending_Approval
    vault_path = Path("AI_Employee_Vault")
    pending_path = vault_path / "Pending_Approval"
    approved_path = vault_path / "Approved"

    # Create a test approval file
    test_post_id = f"TEST_POST_{int(time.time())}"
    test_file = pending_path / f"{test_post_id}.md"

    approval_content = f"""---
type: linkedin_post_approval
action: post_linkedin
content_type: update
created: {time.strftime('%Y-%m-%dT%H:%M:%S')}
status: pending_approval
expires: {time.strftime('%Y-%m-%dT23:59:59')}
---

## LinkedIn Post Draft

**Content:**
This is a test post for approval workflow testing.

**Hashtags:**
#test #approval #workflow

## Action Required
Move this file to:
- `/Approved/` to post to LinkedIn
- `/Rejected/` to skip posting

## Preview
This is a test post for approval workflow testing.
"""

    with open(test_file, 'w', encoding='utf-8') as f:
        f.write(approval_content)

    print(f"[PASS] Created test approval file: {test_file}")

    # Verify file was created
    if test_file.exists():
        print(f"[PASS] Test approval file exists")

        # Count files before and after move
        pending_count_before = len(list(pending_path.glob("*.md")))
        approved_count_before = len(list(approved_path.glob("*.md")))

        # Move to approved
        approved_file = approved_path / test_file.name
        test_file.rename(approved_file)

        pending_count_after = len(list(pending_path.glob("*.md")))
        approved_count_after = len(list(approved_path.glob("*.md")))

        if approved_file.exists():
            print(f"[PASS] Successfully moved to Approved folder: {approved_file}")
            print(f"[PASS] Pending count: {pending_count_before} -> {pending_count_after}")
            print(f"[PASS] Approved count: {approved_count_before} -> {approved_count_after}")

            # Clean up - move to Done
            done_path = vault_path / "Done"
            done_file = done_path / approved_file.name
            approved_file.rename(done_file)
            print(f"[PASS] Cleaned up test file to Done folder: {done_file}")

            return True
        else:
            print(f"[FAIL] Failed to move file to Approved folder")
            return False
    else:
        print(f"[FAIL] Test approval file was not created")
        return False


def main():
    """Run all tests"""
    print("LinkedIn Poster Test Suite")
    print("=" * 40)

    # Test 1: LinkedIn poster functionality
    test1_result = test_linkedin_poster()

    # Test 2: Approval workflow
    test2_result = test_approval_workflow()

    print("\nTest Results:")
    print(f"LinkedIn Poster: {'[PASS]' if test1_result else '[FAIL]'}")
    print(f"Approval Workflow: {'[PASS]' if test2_result else '[FAIL]'}")

    overall_result = test1_result and test2_result
    print(f"Overall: {'[PASS]' if overall_result else '[FAIL]'}")

    return overall_result


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)