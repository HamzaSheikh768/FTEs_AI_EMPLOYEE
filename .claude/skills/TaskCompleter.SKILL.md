---
name: task-completer
description: |
  Moves processed items from /Needs_Action/ to /Done/ folder, logs completion events, and updates Dashboard.md.
  This skill should be used when completing tasks that have been processed by the AI Employee.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# TaskCompleter Skill

## Purpose
Moves processed items from `/Needs_Action/` to `/Done/` folder, logs completion events to system logs, and updates `Dashboard.md`. This completes the core task lifecycle for the Personal AI Employee.

## When to Use This Skill
- When tasks in `/Needs_Action/` have been processed and need to be completed
- As part of the Bronze Tier foundation for the Personal AI Employee
- When implementing the core task completion workflow

## Inputs
- **completion_criteria**: How to identify completed tasks (e.g., marked with [X] or specific status)
- **process_path**: Path to monitor for completed tasks (default /Needs_Action/)

## Outputs
- Moves files from `/Needs_Action/` to `/Done/` folder
- Creates log entries in `/Logs/YYYY-MM-DD.md`
- Updates Dashboard.md with completed task counts

## Hook Dependencies
None

## Approval Required
No - file movement and logging only

## DRY_RUN Support
Yes - logs intent to complete but doesn't actually move files

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Vault structure, dashboard format, log formats, completion criteria |
| **Conversation** | User's specific completion criteria, logging requirements |
| **Skill References** | File completion patterns, dashboard update mechanisms, log formats |
| **User Guidelines** | Project-specific completion rules, dashboard update frequency |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Scan /Needs_Action/ for completed files (based on criteria)
2. For each completed file:
   a. Move file to /Done/ folder
   b. Log completion event to /Logs/{today}.md
   c. Update Dashboard.md counters
3. Continue monitoring for completed tasks
```

### Log Entry Format
The skill appends entries to `/Logs/YYYY-MM-DD.md` in this format:
```
[ISO-8601] | AGENT:TaskCompleter | ACTION:move_to_done | STATUS:success | file:{filename}
```

### Dashboard Update
The skill updates the task counts in Dashboard.md:
- Increment `/Done` counter
- Decrement `/Needs_Action` counter
- Preserve other dashboard elements

### Error Handling
- If move fails: log error and keep file in Needs_Action for retry
- If logging fails: continue, log error separately but complete move
- If dashboard update fails: continue with completion
- If file is already in Done: skip, log as duplicate detection

### File Processing Guarantees
- Files are moved only once (idempotent operation)
- Log entries created before file moves for traceability
- Dashboard updates happen after successful completion