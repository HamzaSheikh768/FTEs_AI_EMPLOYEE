---
name: inbox-router
description: |
  Monitors /Inbox/ for new files and moves them to /Needs_Action/ folder while updating Dashboard.md counters.
  This skill should be used when routing newly detected items from the inbox to the processing queue.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# InboxRouter Skill

## Purpose
Monitors `/Inbox/` for new files and moves them to `/Needs_Action/` folder while updating `Dashboard.md` counters. This is part of the core routing mechanism for the Personal AI Employee.

## When to Use This Skill
- When new items need to be routed from `/Inbox/` to `/Needs_Action/` for processing
- As part of the Bronze Tier foundation for the Personal AI Employee
- When implementing the core task routing workflow

## Inputs
- **poll_interval**: How often to check for new files (default 10 seconds)

## Outputs
- Moves files from `/Inbox/` to `/Needs_Action/` folder
- Updates Dashboard.md with current task counts
- Logs routing events to the system logs

## Hook Dependencies
None

## Approval Required
No - file routing only

## DRY_RUN Support
Yes - logs intent to route but doesn't actually move files

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Vault structure, dashboard format, log formats, file naming conventions |
| **Conversation** | User's specific routing requirements, priority handling needs |
| **Skill References** | File routing patterns, dashboard update mechanisms, log formats |
| **User Guidelines** | Project-specific routing rules, dashboard update frequency |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Scan /Inbox/ for new files not yet processed
2. For each new file:
   a. Read frontmatter to extract metadata
   b. Set status to 'routed' in frontmatter
   c. Move file to /Needs_Action/ folder
   d. Log routing event to /Logs/
   e. Update Dashboard.md counters
3. Continue monitoring for new files
```

### Routing Logic
```
/Inbox/{file}
  → Read frontmatter
  → Set status: routed
  → Move to /Needs_Action/{file}
  → Append to /Logs/{YYYY-MM-DD}.md
  → Update Dashboard.md pending count
```

### Dashboard Update
The skill updates the task counts in Dashboard.md:
- Increment `/Needs_Action` counter
- Decrement `/Inbox` counter
- Preserve other dashboard elements

### Error Handling
- If read fails: log error and skip file
- If move fails: log error and keep file in inbox for retry
- If dashboard update fails: continue, log error separately
- If logging fails: continue with routing

### File Processing Guarantees
- Files are processed once (idempotent operation)
- Files not modified during processing, only moved
- Dashboard updates happen after successful moves