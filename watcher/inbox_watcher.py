#!/usr/bin/env python3
"""
File System Watcher for Personal AI Employee
Monitors the Inbox directory for new files and processes them
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class InboxHandler(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.inbox_path = Path(vault_path) / 'Inbox'
        self.needs_action_path = Path(vault_path) / 'Needs_Action'

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Skip .md files that are already action files, but not our special files
        if file_path.suffix.lower() == '.md' and not any(tag in file_path.name.lower() for tag in ['file_', 'email_', 'system_test']):
            return

        # Skip temporary files
        if file_path.name.startswith('~') or file_path.suffix.lower() in ['.tmp', '.swp', '.part']:
            return

        # Skip if this looks like a processing task file we created (starts with PROCESS_)
        if file_path.name.startswith('PROCESS_') and file_path.suffix.lower() == '.md':
            return

        # Process the file by creating a simple entry in Needs_Action
        if self.needs_action_path.exists():
            # Create a simple task to process the new file
            task_file = self.needs_action_path / f'PROCESS_{file_path.name}.md'
            # Check if the task file already exists to avoid duplication
            if not task_file.exists():
                task_content = f"""---
type: file_processing
original_file: {file_path.name}
received: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}
status: pending
---
File {file_path.name} was added to Inbox and needs processing.
"""
                task_file.write_text(task_content)
                print(f'Detected: {file_path.name} - Created processing task: {task_file.name}')
            else:
                print(f'Detected: {file_path.name} - Processing task already exists')
        else:
            print(f'Detected: {file_path.name} - Needs_Action folder not found')

    def on_moved(self, event):
        if event.is_directory:
            return
        # Handle files moved into the Inbox
        dest_path = Path(event.dest_path)
        if self.needs_action_path.exists():
            task_file = self.needs_action_path / f'PROCESS_{dest_path.name}.md'
            task_content = f"""---
type: file_processing
original_file: {dest_path.name}
received: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}
status: pending
---
File {dest_path.name} was moved to Inbox and needs processing.
"""
            task_file.write_text(task_content)
            print(f'File moved to Inbox: {dest_path.name} - Created processing task: {task_file.name}')

def main():
    vault_path = "AI_Employee_Vault"
    inbox_path = Path(vault_path) / "Inbox"

    # Verify the vault structure exists
    if not inbox_path.exists():
        print(f"Error: Inbox directory does not exist at {inbox_path}")
        print("Please ensure your AI Employee vault is properly set up.")
        return

    event_handler = InboxHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, str(inbox_path), recursive=False)

    print(f"Starting Inbox watcher for: {inbox_path}")
    print(f"Monitoring for new files in the Inbox...")
    print("When files are added to Inbox, they will trigger processing tasks in Needs_Action")
    print("Press Ctrl+C to stop...")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping Inbox watcher...")

    observer.join()
    print("Inbox watcher stopped.")

if __name__ == "__main__":
    main()