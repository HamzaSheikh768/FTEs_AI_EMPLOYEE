---
name: audit-logger
description: |
  Maintains append-only audit trail in /Logs/ with standardized log entries.
  This skill should be used when any system component needs to log events to the audit trail.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# AuditLogger Skill

## Purpose
Maintains append-only audit trail in `/Logs/` with standardized log entries. This provides the centralized logging functionality for the Personal AI Employee system.

## When to Use This Skill
- When any system component needs to log events to the audit trail
- As part of the Bronze Tier foundation for the Personal AI Employee
- When implementing the core audit logging requirement

## Inputs
- **timestamp**: ISO-8601 formatted timestamp (default: current time)
- **agent**: Name of the agent performing the action
- **action**: Description of the action being logged
- **status**: Status of the action (success, error, pending, etc.)
- **file_reference**: Optional reference to relevant file
- **additional_info**: Any additional information to log

## Outputs
- Appends entries to `/Logs/YYYY-MM-DD.md`
- Follows standardized log format
- Maintains append-only integrity

## Hook Dependencies
None

## Approval Required
No - logging only

## DRY_RUN Support
Yes - logs intent to log but doesn't actually write to log file

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Current log format, vault structure, system naming conventions |
| **Conversation** | User's specific logging requirements, additional fields needed |
| **Skill References** | Log format standards, audit trail best practices, file append patterns |
| **User Guidelines** | Project-specific logging policies, retention requirements |

Ensure all required context is gathered before implementing.

### Log Entry Format
The skill appends entries to `/Logs/YYYY-MM-DD.md` in this format:
```
[ISO-8601] | AGENT:{agent_name} | ACTION:{action_description} | STATUS:{status} | file:{filename}
```

For example:
```
2026-02-20T01:35:45Z | AGENT:FileSystemWatcher | ACTION:file_detected | STATUS:success | file:FILE_example.md
```

### Workflow
```
1. Format the log entry according to the standard format
2. Ensure today's log file exists (/Logs/YYYY-MM-DD.md)
3. Append the entry to the end of the file
4. Preserve append-only integrity (never modify existing entries)
5. Return success/failure status
```

### Error Handling
- If log directory doesn't exist: create it and then log
- If file write fails: return error status but don't fail the calling process
- If timestamp is invalid: use current time instead
- If log entry is malformed: format it correctly before appending

### Log File Management
- Creates daily log files in format `/Logs/YYYY-MM-DD.md`
- Ensures file exists before attempting to append
- Maintains proper file permissions for append-only access
- Handles concurrent access scenarios appropriately

### Standard Fields
- **timestamp**: ISO-8601 format (e.g., 2026-02-20T01:35:45Z)
- **agent**: Name of the component making the log entry
- **action**: Brief description of the action taken
- **status**: Result of the action (success, error, etc.)
- **file**: Optional file reference if relevant to the action