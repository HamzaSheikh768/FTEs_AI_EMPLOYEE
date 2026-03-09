"""
Approval Workflow System for Personal AI Employee
Monitors vault directories for approval changes and executes actions
"""
import os
import time
import shutil
from pathlib import Path
from datetime import datetime
from typing import Callable, Dict, Any
import importlib.util


class ApprovalWorkflow:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.pending_approval_path = self.vault_path / "Pending_Approval"
        self.approved_path = self.vault_path / "Approved"
        self.rejected_path = self.vault_path / "Rejected"
        self.done_path = self.vault_path / "Done"

        # Create vault directories if they don't exist
        self.pending_approval_path.mkdir(parents=True, exist_ok=True)
        self.approved_path.mkdir(parents=True, exist_ok=True)
        self.rejected_path.mkdir(parents=True, exist_ok=True)
        self.done_path.mkdir(parents=True, exist_ok=True)

        # Track processed files to avoid re-processing
        self.processed_files = set()

    def process_pending_approvals(self):
        """Process all pending approval files"""
        print("Checking for pending approvals...")

        approval_files = list(self.pending_approval_path.glob("*.md"))

        for approval_file in approval_files:
            if approval_file.name in self.processed_files:
                continue  # Skip already processed files

            print(f"Processing approval file: {approval_file.name}")

            try:
                self._process_approval_file(approval_file)
                self.processed_files.add(approval_file.name)
            except Exception as e:
                print(f"Error processing {approval_file.name}: {e}")
                import traceback
                traceback.print_exc()

    def _process_approval_file(self, approval_file: Path):
        """Process a single approval file based on its content"""
        with open(approval_file, 'r', encoding='utf-8') as f:
            content = f.read()

        # Parse the frontmatter to determine the action type
        frontmatter, body = self._parse_frontmatter(content)

        action_type = frontmatter.get('type', '')

        if action_type == 'linkedin_post_approval':
            self._handle_linkedin_post_approval(approval_file, frontmatter, body)
        elif action_type == 'email_action_approval':
            self._handle_email_action_approval(approval_file, frontmatter, body)
        else:
            print(f"Unknown action type: {action_type} in {approval_file.name}")
            # Move to Done by default
            self._move_to_done(approval_file)

    def _parse_frontmatter(self, content: str) -> tuple:
        """Parse YAML frontmatter from content"""
        lines = content.split('\n')
        frontmatter = {}
        body = content

        if len(lines) > 0 and lines[0].strip() == '---':
            # Find the end of frontmatter
            for i in range(1, len(lines)):
                if lines[i].strip() == '---':
                    # Parse frontmatter
                    frontmatter_content = '\n'.join(lines[1:i])
                    for line in frontmatter_content.split('\n'):
                        if ':' in line:
                            key, value = line.split(':', 1)
                            frontmatter[key.strip()] = value.strip().strip('"\'')

                    # Get the body content after the second ---
                    body = '\n'.join(lines[i+1:]).strip()
                    break

        return frontmatter, body

    def _handle_linkedin_post_approval(self, approval_file: Path, frontmatter: dict, body: str):
        """Handle LinkedIn post approval"""
        print(f"Handling LinkedIn post approval: {approval_file.name}")

        # Extract content and hashtags from body
        content, hashtags = self._extract_content_and_hashtags(body)

        # Check the file's parent directory to determine action
        # If it's already in Approved, process the post; otherwise, wait
        parent_dir = approval_file.parent.name.lower()

        if parent_dir == 'approved':
            print(f"LinkedIn post approved: {content[:50]}...")
            # In a real implementation, this would post to LinkedIn
            # For now, we'll just move to Done
            self._move_to_done(approval_file)
        elif parent_dir == 'rejected':
            print(f"LinkedIn post rejected: {content[:50]}...")
            # Move to Done since it's processed (just not posted)
            self._move_to_done(approval_file)
        else:
            # Still pending, leave as is
            print(f"LinkedIn post still pending: {content[:50]}...")

    def _handle_email_action_approval(self, approval_file: Path, frontmatter: dict, body: str):
        """Handle email action approval"""
        print(f"Handling email action approval: {approval_file.name}")

        # Extract email details
        content, _ = self._extract_content_and_hashtags(body)

        # Check the file's parent directory to determine action
        parent_dir = approval_file.parent.name.lower()

        if parent_dir == 'approved':
            print(f"Email action approved: {content[:50]}...")
            # In a real implementation, this would execute the email action
            self._move_to_done(approval_file)
        elif parent_dir == 'rejected':
            print(f"Email action rejected: {content[:50]}...")
            # Move to Done since it's processed
            self._move_to_done(approval_file)
        else:
            # Still pending, leave as is
            print(f"Email action still pending: {content[:50]}...")

    def _extract_content_and_hashtags(self, body: str) -> tuple:
        """Extract content and hashtags from approval body"""
        content = ""
        hashtags = []

        lines = body.split('\n')
        content_start = -1
        content_end = -1
        hashtags_line = -1

        for i, line in enumerate(lines):
            if line.strip() == "**Content:**" and content_start == -1:
                content_start = i + 1
            elif line.strip().startswith("**Hashtags:") and content_end == -1:
                content_end = i
                hashtags_line = i
            elif content_start > 0 and content_end == -1 and line.strip() == "":
                content_end = i

        # Extract the actual content
        if content_start > 0 and content_end > 0:
            content = "\n".join(lines[content_start:content_end]).strip()

        # Extract hashtags
        if hashtags_line > 0:
            hashtag_line = lines[hashtags_line].replace("**Hashtags:**", "").strip()
            if hashtag_line:
                hashtags = [tag.strip() for tag in hashtag_line.split() if tag.startswith("#")]
                hashtags = [tag.strip("#") for tag in hashtags]

        return content, hashtags

    def _move_to_done(self, approval_file: Path):
        """Move an approval file to the Done directory"""
        destination = self.done_path / approval_file.name
        shutil.move(str(approval_file), str(destination))
        print(f"Moved {approval_file.name} to Done")

    def run_monitoring_loop(self, interval: int = 5):
        """Run the monitoring loop to check for approval changes"""
        print(f"Starting approval workflow monitoring (checking every {interval}s)...")

        try:
            while True:
                self.process_pending_approvals()
                time.sleep(interval)
        except KeyboardInterrupt:
            print("\nApproval workflow monitoring stopped.")


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Approval Workflow System for Personal AI Employee")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--interval", type=int, default=5, help="Check interval in seconds")
    parser.add_argument("--run-once", action="store_true", help="Run once instead of continuously")

    args = parser.parse_args()

    workflow = ApprovalWorkflow(vault_path=args.vault_path)

    if args.run_once:
        workflow.process_pending_approvals()
        print("Approval workflow run completed.")
    else:
        workflow.run_monitoring_loop(interval=args.interval)


if __name__ == "__main__":
    main()