#!/usr/bin/env python3
"""
Auto Transfer Script for Personal AI Employee
Automatically transfers all files from Needs_Action folder to Done folder
"""
import shutil
import time
from pathlib import Path
import logging
import re
from datetime import datetime


def setup_logging():
    """Set up logging for the transfer process"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('AI_Employee_Vault/Logs/auto_transfer.log'),
            logging.StreamHandler()
        ]
    )
    return logging.getLogger(__name__)


def transfer_all_needs_action_to_done():
    """Transfer all files from Needs_Action folder to Done folder"""
    logger = setup_logging()

    vault_path = Path("AI_Employee_Vault")
    needs_action_path = vault_path / "Needs_Action"
    done_path = vault_path / "Done"
    logs_path = vault_path / "Logs"

    # Create directories if they don't exist
    logs_path.mkdir(exist_ok=True)
    done_path.mkdir(exist_ok=True)

    # Verify directories exist
    if not needs_action_path.exists():
        logger.error(f"Needs_Action directory does not exist at {needs_action_path}")
        return 0

    if not done_path.exists():
        logger.error(f"Done directory does not exist at {done_path}")
        return 0

    # Get all files in Needs_Action
    needs_action_files = [f for f in needs_action_path.iterdir() if f.is_file()]

    if not needs_action_files:
        logger.info("No files found in Needs_Action to transfer.")
        return 0

    logger.info(f"Found {len(needs_action_files)} files in Needs_Action. Transferring to Done...")

    transferred_count = 0
    for file_path in needs_action_files:
        # Skip temporary files
        if (file_path.name.startswith('.') or
            file_path.name.startswith('~') or
            file_path.suffix.lower() in ['.tmp', '.swp', '.part', '.swx']):
            logger.info(f"Skipping temporary file: {file_path.name}")
            continue

        try:
            # Move the file from Needs_Action to Done
            dest_path = done_path / file_path.name
            shutil.move(str(file_path), str(dest_path))

            logger.info(f"[OK] Moved {file_path.name} from Needs_Action to Done")
            transferred_count += 1

        except Exception as e:
            logger.error(f"[ERROR] Error moving file {file_path.name}: {e}")

    # Update dashboard after transfer
    update_dashboard_counts()

    logger.info(f"Successfully transferred {transferred_count} files from Needs_Action to Done")
    return transferred_count


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
        pending_approval_path = vault_path / 'Pending_Approval'
        approved_path = vault_path / 'Approved'
        rejected_path = vault_path / 'Rejected'

        inbox_count = len([f for f in inbox_path.iterdir() if f.is_file()]) if inbox_path.exists() else 0
        needs_action_count = len([f for f in needs_action_path.iterdir() if f.is_file()]) if needs_action_path.exists() else 0
        done_count = len([f for f in done_path.iterdir() if f.is_file()]) if done_path.exists() else 0
        pending_approval_count = len([f for f in pending_approval_path.iterdir() if f.is_file()]) if pending_approval_path.exists() else 0
        approved_count = len([f for f in approved_path.iterdir() if f.is_file()]) if approved_path.exists() else 0
        rejected_count = len([f for f in rejected_path.iterdir() if f.is_file()]) if rejected_path.exists() else 0

        # Read current dashboard content
        content = dashboard_path.read_text(encoding='utf-8')

        # Update the counts in the table - update to include Needs_Action
        updated_content = re.sub(
            r'\| /Inbox \| \d+ \|\s*\n\s*\| /Pending_Approval \| \d+ \|\s*\n\s*\| /Approved \| \d+ \|\s*\n\s*\| /Rejected \| \d+ \|\s*\n\s*\| /Done \| \d+ \|',
            f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |\n| /Pending_Approval | {pending_approval_count} |\n| /Approved | {approved_count} |\n| /Rejected | {rejected_count} |\n| /Done | {done_count} |',
            content
        )

        # If the above replacement didn't work (because the format is different), try to update the existing format
        if updated_content == content:
            # Try to update the existing format that only has Inbox, Pending_Approval, Approved, Rejected, Done
            updated_content = re.sub(
                r'(\| /Inbox \| )\d+(\s*\|\s*\n\s*\| /Pending_Approval \| )\d+(\s*\|\s*\n\s*\| /Approved \| )\d+(\s*\|\s*\n\s*\| /Rejected \| )\d+(\s*\|\s*\n\s*\| /Done \| )\d+(\s*\|)',
                f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |\n| /Pending_Approval | {pending_approval_count} |\n| /Approved | {approved_count} |\n| /Rejected | {rejected_count} |\n| /Done | {done_count} |',
                content
            )

        # If still not updated, try a simpler approach - just add the Needs_Action row after Inbox
        if updated_content == content:
            updated_content = content.replace(
                f'| /Inbox | {inbox_count if "Inbox | 0" in content else "[0-9]+"} |',
                f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |'
            )

        dashboard_path.write_text(updated_content, encoding='utf-8')
        print(f"Dashboard updated: Inbox={inbox_count}, Needs_Action={needs_action_count}, Pending_Approval={pending_approval_count}, Approved={approved_count}, Rejected={rejected_count}, Done={done_count}")
    except Exception as e:
        print(f"Error updating dashboard: {e}")


def main():
    print("Personal AI Employee - Auto Transfer System")
    print("Transferring all files from Needs_Action to Done folder...")

    # Process files
    transferred_count = transfer_all_needs_action_to_done()

    if transferred_count > 0:
        print(f"\nSuccessfully transferred {transferred_count} files from Needs_Action to Done")
    else:
        print("\nNo files were found in Needs_Action to transfer.")


if __name__ == "__main__":
    main()