#!/usr/bin/env python3
"""
File System Watcher for Personal AI Employee
Monitors a specified directory and moves new files to the AI Employee inbox
"""

import time
import logging
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import shutil

class DropFolderHandler(FileSystemEventHandler):
    """Handles file system events for the drop folder.

    Args:
        FileSystemEventHandler (_type_): Base class for handling file system events from watchdog.
    """    
    def __init__(self, vault_path: str):
        self.needs_action = Path(vault_path) / 'Inbox'

    def on_created(self, event):
        if event.is_directory:
            return

        source = Path(event.src_path)

        # Skip temporary files starting with ~ or ending with .tmp
        if source.name.startswith('~') or source.suffix.lower() == '.tmp':
            return

        # Skip if this looks like a metadata file we created (starts with FILE_ and has .md extension)
        if source.name.startswith('FILE_') and source.suffix.lower() == '.md':
            return

        # Skip if we're monitoring within the vault and this is already in the Inbox
        if self.needs_action in source.parents and source.suffix.lower() == '.md':
            return

        # Create metadata file with the same name + .md extension
        meta_path = self.needs_action / f'FILE_{source.name}.md'
        # Avoid creating a metadata file for a metadata file (double generation)
        if source.suffix.lower() != '.md':
            meta_content = f"""---
type: file_drop
original_name: {source.name}
size: {source.stat().st_size}
received: {time.strftime('%Y-%m-%dT%H:%M:%SZ')}
status: pending
---
New file dropped for processing.
"""
            try:
                meta_path.write_text(meta_content)
                print(f'File {source.name} detected and added to inbox for processing')
            except FileNotFoundError:
                print(f'Warning: Could not create metadata file {meta_path} - directory may not exist')
        else:
            # For .md files, just copy them to inbox if they're not already there
            if self.needs_action != source.parent:  # Only copy if not already in inbox
                dest_path = self.needs_action / source.name
                try:
                    shutil.copy2(source, dest_path)  # Copy with metadata
                    print(f'Markdown file {source.name} copied to inbox for processing')
                except Exception as e:
                    print(f'Error copying file {source.name}: {e}')

def main():
    # You can change this path to monitor a different directory
    watcher_path = input("Enter the directory path to monitor (default: ./watcher): ") or "./watcher"
    vault_path = "AI_Employee_Vault"

    # Create the watch folder if it doesn't exist
    Path(watcher_path).mkdir(exist_ok=True)

    event_handler = DropFolderHandler(vault_path)
    observer = Observer()
    observer.schedule(event_handler, watcher_path, recursive=True)

    print(f"Starting file system watcher for: {watcher_path}")
    print(f"Files will be processed to: {vault_path}/Inbox/")
    print("Press Ctrl+C to stop...")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping file system watcher...")

    observer.join()
    print("File system watcher stopped.")

if __name__ == "__main__":
    main()