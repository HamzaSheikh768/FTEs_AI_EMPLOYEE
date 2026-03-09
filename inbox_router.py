#!/usr/bin/env python3
"""
Inbox Router for Personal AI Employee
Automatically moves files from Inbox to Needs_Action with status update
"""

import time
import logging
from pathlib import Path
import shutil
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxRouter(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.inbox_path = Path(vault_path) / 'Inbox'
        self.needs_action_path = Path(vault_path) / 'Needs_Action'

    def _update_frontmatter_status(self, file_path, new_status="pending"):
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
                    lines = frontmatter.split('\n')
                    status_updated = False
                    for i, line in enumerate(lines):
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

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip temporary files
        if file_path.name.startswith('~') or file_path.suffix.lower() in ['.tmp', '.swp', '.part']:
            return

        # Skip if it's already a routing task file
        if 'PROCESS_' in file_path.name:
            return

        try:
            # Update the status in the file's frontmatter
            if file_path.suffix.lower() == '.md':
                self._update_frontmatter_status(file_path, "routed")

            # Move the file from Inbox to Needs_Action
            dest_path = self.needs_action_path / file_path.name
            shutil.move(str(file_path), str(dest_path))

            print(f"Router: Moved {file_path.name} from Inbox to Needs_Action")
        except Exception as e:
            print(f"Error moving file {file_path.name}: {e}")

    def on_moved(self, event):
        # This handles files moved into the Inbox
        if event.is_directory:
            return

        dest_path = Path(event.dest_path)
        if dest_path.parent == self.inbox_path:
            # File was moved into Inbox, route it to Needs_Action
            try:
                # Update the status in the file's frontmatter
                if dest_path.suffix.lower() == '.md':
                    self._update_frontmatter_status(dest_path, "routed")

                # Move the file from Inbox to Needs_Action
                new_dest_path = self.needs_action_path / dest_path.name
                shutil.move(str(dest_path), str(new_dest_path))

                print(f"Router: Moved {dest_path.name} from Inbox to Needs_Action")
            except Exception as e:
                print(f"Error moving file {dest_path.name}: {e}")

def main():
    vault_path = "AI_Employee_Vault"
    inbox_path = Path(vault_path) / "Inbox"
    needs_action_path = Path(vault_path) / "Needs_Action"

    # Verify the vault structure exists
    if not inbox_path.exists():
        print(f"Error: Inbox directory does not exist at {inbox_path}")
        print("Please ensure your AI Employee vault is properly set up.")
        return

    if not needs_action_path.exists():
        print(f"Error: Needs_Action directory does not exist at {needs_action_path}")
        print("Please ensure your AI Employee vault is properly set up.")
        return

    event_handler = InboxRouter(vault_path)
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)

    print(f"Starting Inbox Router for: {inbox_path}")
    print(f"Will automatically move new files from Inbox to Needs_Action")
    print("Processing files in real-time...")
    print("Press Ctrl+C to stop...")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping Inbox Router...")

    observer.join()
    print("Inbox Router stopped.")

if __name__ == "__main__":
    main()