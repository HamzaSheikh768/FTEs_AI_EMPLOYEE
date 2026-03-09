#!/usr/bin/env python3
"""
Advanced File System Detector for Personal AI Employee
Monitors the entire vault system and automatically processes files through the complete workflow:
Inbox → Needs_Action → Done with full lifecycle management.
"""

import time
import logging
import shutil
import re
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from datetime import datetime

class VaultDetector(FileSystemEventHandler):
    def __init__(self, vault_path: str):
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / 'Inbox'
        self.needs_action_path = self.vault_path / 'Needs_Action'
        self.done_path = self.vault_path / 'Done'

        # Set up logging
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(self.vault_path / 'Logs' / 'filesystem_detector.log'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

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

            self.logger.info(f"Updated frontmatter status for {file_path.name} to {new_status}")
        except Exception as e:
            self.logger.error(f"Error updating frontmatter for {file_path}: {e}")

    def _update_dashboard(self):
        """Update the dashboard with current counts"""
        try:
            dashboard_path = self.vault_path / 'Dashboard.md'
            if not dashboard_path.exists():
                return

            # Count files in each directory
            inbox_count = len([f for f in self.inbox_path.iterdir() if f.is_file()]) if self.inbox_path.exists() else 0
            needs_action_count = len([f for f in self.needs_action_path.iterdir() if f.is_file()]) if self.needs_action_path.exists() else 0
            done_count = len([f for f in self.done_path.iterdir() if f.is_file()]) if self.done_path.exists() else 0

            # Read current dashboard content
            content = dashboard_path.read_text(encoding='utf-8')

            # Update the counts in the table
            pattern = r'\| /Inbox \| \d+ \|\s*\n\s*\| /Needs_Action \| \d+ \|\s*\n\s*\| /Done \| \d+ \|'
            replacement = f'| /Inbox | {inbox_count} |\n| /Needs_Action | {needs_action_count} |\n| /Done | {done_count} |'

            updated_content = re.sub(pattern, replacement, content)

            dashboard_path.write_text(updated_content, encoding='utf-8')
            self.logger.info(f"Dashboard updated: Inbox={inbox_count}, Needs_Action={needs_action_count}, Done={done_count}")
        except Exception as e:
            self.logger.error(f"Error updating dashboard: {e}")

    def _process_file_from_inbox(self, file_path):
        """Process a file from Inbox to Needs_Action"""
        # Skip temporary files
        if (file_path.name.startswith('~') or
            file_path.name.startswith('.') or
            file_path.suffix.lower() in ['.tmp', '.swp', '.part', '.swx']):
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

            self.logger.info(f"Moved {file_path.name} from Inbox to Needs_Action")

            # Update dashboard
            self._update_dashboard()

        except Exception as e:
            self.logger.error(f"Error moving file {file_path.name}: {e}")

    def _process_file_from_needs_action(self, file_path):
        """Process a file from Needs_Action to Done (when complete)"""
        if not file_path.suffix.lower() == '.md':
            return  # Only process markdown files for completion status

        try:
            # Read the file to check its status
            content = file_path.read_text(encoding='utf-8')

            # Check if this is a multi-step task and create a plan if needed
            if self._is_multi_step_task(content) and 'Plan.md' not in content:
                # Create a plan for multi-step tasks
                self._create_plan_for_task(file_path, content)

            # Check if the file has been marked as completed
            if 'status: completed' in content or 'status: done' in content or 'status: finished' in content:
                # Move the file from Needs_Action to Done
                dest_path = self.done_path / file_path.name
                shutil.move(str(file_path), str(dest_path))

                self.logger.info(f"Moved {file_path.name} from Needs_Action to Done (completed)")

                # Update dashboard
                self._update_dashboard()

        except Exception as e:
            self.logger.error(f"Error processing completed file {file_path.name}: {e}")

    def _is_multi_step_task(self, content):
        """Check if the task requires multiple steps"""
        # Look for indicators of multi-step tasks
        multi_step_indicators = [
            'steps', 'step 1', 'step 2', 'first', 'then', 'finally',
            'multiple', 'several', 'process', 'workflow', 'procedure'
        ]

        content_lower = content.lower()
        for indicator in multi_step_indicators:
            if indicator in content_lower:
                return True
        return False

    def _create_plan_for_task(self, file_path, content):
        """Create a Plan.md file for a multi-step task"""
        try:
            import os
            from datetime import datetime

            # Create Plans directory if it doesn't exist
            plans_path = self.vault_path / "Plans"
            plans_path.mkdir(exist_ok=True)

            # Generate filename
            task_name = file_path.stem
            timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M")
            plan_filename = f"PLAN_{task_name}_{timestamp}.md"
            plan_path = plans_path / plan_filename

            # Create the plan content
            plan_content = f"""---
created: {datetime.now().isoformat()}
source_task: [[../Needs_Action/{file_path.name}]]
status: in-planning
---

# Task Execution Plan

## Objective
{self._extract_objective(content)}

## Required Steps
- [ ] Step 1: {self._suggest_first_step(content)}
- [ ] Step 2: Determine additional steps based on task requirements
- [ ] Final: Move source task file to /Done after completion

## Resources / Tools Needed
- File system access
- Any required skills or tools mentioned in the source task

## Risks
- Dependencies on external systems
- Potential for incomplete action

"""

            # Write the plan
            plan_path.write_text(plan_content, encoding='utf-8')

            # Check if plan link already exists to avoid duplicates
            if f"[[Plans/{plan_filename}]]" not in content:
                # Append link to the original file
                updated_content = f"{content}\n\n[[Plans/{plan_filename}]]"
                file_path.write_text(updated_content, encoding='utf-8')
            else:
                # Plan link already exists, just update the content
                file_path.write_text(content, encoding='utf-8')

            self.logger.info(f"Created plan {plan_filename} for multi-step task {file_path.name}")
        except Exception as e:
            self.logger.error(f"Error creating plan for task {file_path.name}: {e}")

    def _extract_objective(self, content):
        """Extract the main objective from the task content"""
        lines = content.split('\n')
        for line in lines:
            line = line.strip()
            if line.startswith('# ') or line.startswith('## '):
                return line.replace('#', '').strip()

        # If no header found, try to get the first meaningful sentence
        if len(lines) > 0:
            for line in lines:
                line = line.strip()
                if line and not line.startswith('---') and ':' not in line[:20]:
                    return line[:100]  # Return first 100 chars as summary
        return "Process the given task"

    def _suggest_first_step(self, content):
        """Suggest the first step based on content"""
        content_lower = content.lower()
        if 'email' in content_lower:
            return 'Check email requirements and prepare response'
        elif 'linkedin' in content_lower:
            return 'Analyze LinkedIn posting requirements'
        elif 'file' in content_lower or 'document' in content_lower:
            return 'Identify file operations needed'
        else:
            return 'Analyze the task requirements and determine first action'

    def on_created(self, event):
        """Handle file creation events"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Handle files created in Inbox
        if file_path.parent == self.inbox_path:
            self.logger.info(f"New file detected in Inbox: {file_path.name}")
            self._process_file_from_inbox(file_path)

        # Handle files created in Needs_Action (when they're marked as completed)
        elif file_path.parent == self.needs_action_path:
            # Check if it's a completed task file
            self._process_file_from_needs_action(file_path)

    def on_moved(self, event):
        """Handle file move events"""
        if event.is_directory:
            return

        dest_path = Path(event.dest_path)

        # Handle files moved into Inbox
        if dest_path.parent == self.inbox_path:
            self.logger.info(f"File moved to Inbox: {dest_path.name}")
            self._process_file_from_inbox(dest_path)

        # Handle files moved into Needs_Action (marking as completed)
        elif dest_path.parent == self.needs_action_path:
            self._process_file_from_needs_action(dest_path)

    def on_modified(self, event):
        """Handle file modification events (useful for status changes)"""
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        # Check if a file in Needs_Action has been modified and might be completed
        if file_path.parent == self.needs_action_path and file_path.suffix.lower() == '.md':
            # Small delay to ensure the file write is complete
            time.sleep(0.1)
            self._process_file_from_needs_action(file_path)

def main():
    vault_path = "AI_Employee_Vault"
    inbox_path = Path(vault_path) / "Inbox"
    needs_action_path = Path(vault_path) / "Needs_Action"
    done_path = Path(vault_path) / "Done"
    logs_path = Path(vault_path) / "Logs"

    # Create Logs directory if it doesn't exist
    logs_path.mkdir(exist_ok=True)

    # Verify the vault structure exists
    for path in [inbox_path, needs_action_path, done_path]:
        if not path.exists():
            print(f"Error: Directory does not exist at {path}")
            print("Please ensure your AI Employee vault is properly set up.")
            return

    event_handler = VaultDetector(vault_path)
    observer = Observer()

    # Monitor both Inbox and Needs_Action directories
    observer.schedule(event_handler, str(inbox_path), recursive=False)
    observer.schedule(event_handler, str(needs_action_path), recursive=False)

    print(f"Starting Advanced File System Detector for: {vault_path}")
    print(f"Monitoring: {inbox_path.name}, {needs_action_path.name}")
    print(f"Auto-routing: {inbox_path.name} -> {needs_action_path.name} -> {done_path.name}")
    print("Processing files in real-time...")
    print("Press Ctrl+C to stop...")

    observer.start()
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
        print("\nStopping Advanced File System Detector...")

    observer.join()
    print("Advanced File System Detector stopped.")

if __name__ == "__main__":
    main()