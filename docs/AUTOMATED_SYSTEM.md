# Personal AI Employee - Automated File Processing System

## Overview
This system automatically detects file movements and processes them through the complete workflow from Inbox → Needs_Action → Done without any manual intervention.

## Components

### 1. File System Detector (`filesystem_detector.py`)
- Monitors the entire vault system (Inbox, Needs_Action, Done folders)
- Automatically detects when files are created or moved
- Processes files through the complete lifecycle

### 2. Automated Orchestrator (`automated_orchestrator.py`)
- Manages the complete workflow
- Ensures all required directories exist
- Coordinates the file processing system

### 3. Start Script (`start_automated_system.py`)
- Simple entry point to start the entire automated system
- Sets up the vault structure if needed
- Provides clear status information

## Workflow

1. **File Detection**: When files are added to the Inbox folder, they are automatically detected
2. **Automatic Routing**: Files are moved from Inbox → Needs_Action with status updates
3. **Task Processing**: Tasks in Needs_Action can be processed by AI or humans
4. **Completion Detection**: When a task's status is updated to "completed", "done", or "finished" in the markdown file, it's automatically moved to the Done folder
5. **Dashboard Updates**: The dashboard is automatically updated with current folder counts

## How to Use

1. Ensure your vault structure exists (or let the system create it):
   ```
   AI_Employee_Vault/
   ├── Inbox/
   ├── Needs_Action/
   ├── Done/
   └── Dashboard.md
   ```

2. Start the automated system:
   ```bash
   python start_automated_system.py
   ```

3. Add files to the Inbox folder - they will be automatically routed to Needs_Action
4. Process tasks in Needs_Action
5. Mark tasks as complete by updating their status to "completed", "done", or "finished" in their markdown frontmatter - they will be automatically moved to Done

## Status Tracking

Task files in the system can have the following status values:
- `pending`: New task in Inbox
- `routed`: Task has been moved to Needs_Action
- `in_progress`: Task is being worked on (optional)
- `completed`: Task is finished and will be moved to Done
- `done`: Task has been completed and moved to Done folder

## Dashboard

The system automatically updates the Dashboard.md file with current counts of files in each folder, providing real-time visibility into the system status.

## Logging

All file operations are logged to `AI_Employee_Vault/Logs/filesystem_detector.log` for monitoring and debugging purposes.