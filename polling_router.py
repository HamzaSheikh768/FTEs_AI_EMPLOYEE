#!/usr/bin/env python3
"""
Polling-based Router for Personal AI Employee
Monitors Inbox directory by periodically checking for new files
"""

import time
import shutil
from pathlib import Path
import os

def _update_frontmatter_status(file_path, new_status="routed"):
    """Update the status in YAML frontmatter of a markdown file"""
    try:
        content = file_path.read_text(encoding='utf-8')

        # Check if file has YAML frontmatter
        if content.startswith('---\n'):
            # Find the end of frontmatter
            parts = content.split('\n---\n', 1)
            if len(parts) == 2:
                frontmatter, rest = parts
                # Update or add status field
                status_updated = False
                for i, line in enumerate(lines := frontmatter.split('\n')):
                    if line.startswith('status:'):
                        lines[i] = f'status: {new_status}'
                        status_updated = True
                        break

                # If no status field, add one
                if not status_updated:
                    lines.append(f'status: {new_status}')

                # Reconstruct the file
                new_frontmatter = '\n'.join(lines)
                new_content = f"{new_frontmatter}\n---\n{rest}"
                file_path.write_text(new_content, encoding='utf-8')
            else:
                # No proper frontmatter, prepend status
                file_path.write_text(f"---\nstatus: {new_status}\n---\n{content}", encoding='utf-8')
        else:
            # No frontmatter at all, add one
            file_path.write_text(f"---\nstatus: {new_status}\n---\n{content}", encoding='utf-8')
    except Exception as e:
        print(f"Error updating frontmatter for {file_path}: {e}")

def route_inbox_files_once():
    """Process all files currently in the Inbox directory"""
    vault_path = "AI_Employee_Vault"
    inbox_path = Path(vault_path) / "Inbox"
    needs_action_path = Path(vault_path) / "Needs_Action"

    # Verify directories exist
    if not inbox_path.exists():
        print(f"Error: Inbox directory does not exist at {inbox_path}")
        return 0

    if not needs_action_path.exists():
        print(f"Error: Needs_Action directory does not exist at {needs_action_path}")
        return 0

    # Get all files in Inbox
    inbox_files = [f for f in inbox_path.iterdir() if f.is_file()]

    if not inbox_files:
        print("No files found in Inbox to route.")
        return 0

    print(f"Found {len(inbox_files)} files in Inbox. Routing to Needs_Action...")

    routed_count = 0
    for file_path in inbox_files:
        # Skip temporary files
        if file_path.name.startswith('.') or file_path.name.startswith('~') or file_path.suffix.lower() in ['.tmp', '.swp', '.part', '.swx']:
            continue

        # Skip if it's already a routing task file
        if 'PROCESS_' in file_path.name:
            continue

        try:
            # Update the status in the file's frontmatter
            if file_path.suffix.lower() == '.md':
                _update_frontmatter_status(file_path, "routed")

            # Move the file from Inbox to Needs_Action
            dest_path = needs_action_path / file_path.name
            shutil.move(str(file_path), str(dest_path))

            print(f"[OK] Moved {file_path.name} from Inbox to Needs_Action")
            routed_count += 1

        except Exception as e:
            print(f"[ERROR] Error moving file {file_path.name}: {e}")

    return routed_count

def update_dashboard_counts():
    """Update the dashboard with current folder counts"""
    try:
        vault_path = Path("AI_Employee_Vault")
        dashboard_path = vault_path / 'Dashboard.md'

        if not dashboard_path.exists():
            print("Dashboard.md not found")
            return

        # Count files in each directory
        inbox_path = vault_path / 'Inbox'
        needs_action_path = vault_path / 'Needs_Action'
        done_path = vault_path / 'Done'

        inbox_count = len([f for f in inbox_path.iterdir() if f.is_file()]) if inbox_path.exists() else 0
        needs_action_count = len([f for f in needs_action_path.iterdir() if f.is_file()]) if needs_action_path.exists() else 0
        done_count = len([f for f in done_path.iterdir() if f.is_file()]) if done_path.exists() else 0

        # Read current dashboard content
        content = dashboard_path.read_text(encoding='utf-8')

        # Update the counts in the table
        import re
        pattern = r'(\| /Inbox \| )\d+(\s*\|\s*\n\s*\| /Needs_Action \| )\d+(\s*\|\s*\n\s*\| /Done \| )\d+(\s*\|)'
        replacement = f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |\n| /Done | {done_count} |'

        updated_content = re.sub(
            r'\| /Inbox \| \d+ \|\s*\n\s*\| /Needs_Action \| \d+ \|\s*\n\s*\| /Done \| \d+ \|',
            f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |\n| /Done | {done_count} |',
            content
        )

        dashboard_path.write_text(updated_content, encoding='utf-8')
        print(f"Dashboard updated: Inbox={inbox_count}, Needs_Action={needs_action_count}, Done={done_count}")
    except Exception as e:
        print(f"Error updating dashboard: {e}")

def main():
    print("Personal AI Employee - Polling Router")
    print("Processing existing Inbox files now...")

    # Process files once
    routed_count = route_inbox_files_once()

    if routed_count > 0:
        # Update dashboard after routing
        update_dashboard_counts()
        print(f"\nSuccessfully routed {routed_count} files from Inbox to Needs_Action")
    else:
        print("\nNo files were found in Inbox to route.")

if __name__ == "__main__":
    main()