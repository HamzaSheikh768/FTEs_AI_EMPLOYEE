---
name: comprehensive_audit_logger
description: |
  Provides comprehensive audit logging in JSON format for all system actions.
  Logs include timestamp, action type, status, agent, and detailed parameters.
  Maintains audit trail for compliance and debugging.
---

# Comprehensive Audit Logger

This skill should be used when implementing comprehensive audit logging for all system actions in the Personal AI Employee system. It provides detailed logs in JSON format for compliance, debugging, and system monitoring.

## Purpose

Implements comprehensive audit logging for all system actions with the following features:
- JSON formatted log entries
- Timestamp for each action
- Action type identification
- Status tracking (SUCCESS, ERROR, PENDING)
- Agent identification
- Detailed parameters and context
- Error traces when applicable

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing logging patterns, log directory structure |
| **Conversation** | User's specific requirements for audit content, retention needs |
| **Skill References** | JSON logging best practices, audit compliance standards |
| **User Guidelines** | Project-specific audit requirements, security policies |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Log Entry Creation
- Creates structured log entries in JSON format
- Includes timestamp, action type, status, agent, and details
- Captures relevant context for each system action

### Log Storage
- Stores logs in `/Logs/{YYYY-MM-DD}.md` files
- Uses daily log files for easy management
- Maintains append-only format for integrity

### Audit Categories
- File movement operations (Inbox → Needs_Action → Done, etc.)
- Task processing and execution
- Approval workflows
- System health monitoring
- Error conditions and recovery
- CEO briefing generation
- Skill execution

## Data Sources Integration

### Log Directory
- `/Logs/`: Main directory for audit logs
- Files named `{YYYY-MM-DD}.md`: Daily audit trail
- JSON format: Structured data for analysis

## Output Format

Each log entry follows this JSON structure:

```json
{
  "timestamp": "2026-03-09T23:04:21.123456",
  "action": "ACTION_TYPE",
  "status": "SUCCESS|ERROR|PENDING",
  "agent": "AGENT_NAME",
  "details": {
    "parameter1": "value1",
    "parameter2": "value2",
    "error": "error_message_if_applicable",
    "traceback": "full_traceback_if_applicable"
  }
}
```

## Error Handling

- If primary log storage fails: attempts to write to backup audit location
- If JSON serialization fails: falls back to text-based logging
- If disk space low: maintains essential audit information
- If log directory inaccessible: attempts to create directory

## Configuration

The skill requires:
- Access to `/Logs/` directory
- Write permissions for log files
- Standard vault structure with Logs folder
- Proper error handling for disk space and permissions