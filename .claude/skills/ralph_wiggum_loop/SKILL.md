---
name: ralph_wiggum_loop
description: |
  Implements the advanced Ralph Wiggum persistence loop for file-movement based processing.
  Handles the complete workflow from task detection to execution with human-in-the-loop approval where needed.
  TRIGGER → Inbox → Needs_Action → Plans → Approval → Execution → Logging → Dashboard → LOOP
---

# Ralph Wiggum Loop

This skill should be used when implementing the advanced file-movement based processing loop for the Personal AI Employee system. It orchestrates the complete workflow from task detection to execution with appropriate human-in-the-loop approval.

## Purpose

Implements the Ralph Wiggum persistence loop pattern:
- Monitors the file system for new tasks in the Inbox
- Routes tasks to Needs_Action for processing
- Creates plans and determines if approval is required
- Handles human-in-the-loop approval process
- Executes approved tasks
- Logs all actions comprehensively
- Updates dashboard
- Continues monitoring

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, file-based workflow patterns |
| **Conversation** | User's specific requirements for task processing, approval needs |
| **Skill References** | File processing patterns, approval workflow best practices |
| **User Guidelines** | Project-specific conventions, approval requirements |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Step 1: Trigger Detection
- Monitors `/Inbox/` for new files
- Identifies task type and requirements from file content

### Step 2: Inbox to Needs_Action Routing
- Moves files from `/Inbox/` to `/Needs_Action/` for processing
- Preserves file content and metadata

### Step 3: Needs_Action Processing
- Reads files in `/Needs_Action/`
- Analyzes content to determine if approval is required
- Creates plan files in `/Plans/` directory

### Step 4: Approval Routing
- If approval needed: moves file to `/Pending_Approval/`
- If no approval needed: executes immediately

### Step 5: Human-in-the-Loop Wait
- Monitors `/Pending_Approval/` for human action
- Waits for files to be moved to `/Approved/` or `/Rejected/`

### Step 6: Execution and Logging
- Executes approved tasks
- Logs all actions to `/Logs/`
- Moves files to `/Done/` or `/Rejected/` based on outcome

### Step 7: Dashboard Update
- Updates `/Dashboard.md` with current status
- Shows task counts and system health

### Step 8: Loop Continuation
- Returns to Step 1 to continue monitoring

## Data Sources Integration

### Vault Directories
- `/Inbox/`: Incoming tasks and triggers
- `/Needs_Action/`: Tasks awaiting processing
- `/Plans/`: Generated action plans
- `/Pending_Approval/`: Tasks requiring human approval
- `/Approved/`: Tasks approved for execution
- `/Rejected/`: Tasks declined or failed
- `/Done/`: Completed tasks
- `/Logs/`: Audit trail and logs
- `/Dashboard.md`: System status surface

## Output Format

The skill maintains the following vault structure and file states:

- Files in correct directories based on processing stage
- Comprehensive audit logs in JSON format in `/Logs/`
- Updated dashboard with current system status
- Plan files in `/Plans/` for complex tasks

## Error Handling

- If file processing fails: logs error and moves to Error_Logs
- If approval system unavailable: logs and continues monitoring
- If execution fails: preserves error information and moves to Rejected
- If logging fails: attempts to preserve audit trail in alternative locations

## Configuration

The skill requires these vault directories:
- All standard vault directories (Inbox, Needs_Action, etc.)
- Proper file system permissions for moving files between directories