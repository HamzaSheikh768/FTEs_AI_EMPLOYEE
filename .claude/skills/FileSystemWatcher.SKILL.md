---
name: filesystem-watcher
description: |
  Monitors a designated folder for dropped files and creates metadata files in /Inbox/FILE_{name}.md.
  This skill should be used when monitoring external file drops for processing by the AI Employee.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# FileSystemWatcher Skill

## Purpose
Monitors a designated folder for dropped files and creates metadata files in `/Inbox/FILE_{name}.md` to be processed by the AI Employee system.

## When to Use This Skill
- When external files need to be automatically detected and processed
- As part of the Bronze Tier foundation for the Personal AI Employee
- When integrating with external systems that drop files for processing

## Inputs
- **watch_path**: The directory path to monitor for new files (injected via hook)
- **interval**: How often to check for new files (default 120 seconds)

## Outputs
- Creates metadata files in `/Inbox/` with format `FILE_{name}.md`
- Copies original file to the vault if needed
- Updates system logs with file detection events

## Hook Dependencies
- `.claude/hook/filesystem_watch.hook` - Contains the path to watch

## Approval Required
No - reading and copying files only

## DRY_RUN Support
Yes - logs intent to monitor but doesn't actually monitor

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, file naming conventions, log formats |
| **Conversation** | User's specific watch path, file types to monitor, frequency requirements |
| **Skill References** | File system monitoring patterns, metadata formats, vault conventions |
| **User Guidelines** | Project-specific vault organization, security requirements |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Read watch path from hook configuration
2. Poll the directory at specified intervals (or use inotify if available)
3. Detect new files that haven't been processed
4. Create metadata file in /Inbox/FILE_{original_name}.md
5. Copy original file if retention is needed
6. Log the file detection event
7. Update dashboard counters if needed
```

### Metadata File Schema
The skill creates files in `/Inbox/` with this structure:

```yaml
---
type: file_drop
original_name: {filename}
size: {bytes}
received: {ISO-8601}
status: pending
---
New file dropped for processing.
```

### Error Handling
- If watch path doesn't exist: log error and wait for next interval
- If permission denied: log error and notify user
- If file copy fails: log error, create metadata anyway
- If metadata creation fails: log error and skip file

### Configuration
The watch path must be configured in `.claude/hook/filesystem_watch.hook` and injected at runtime.