---
name: gmail-watcher
description: |
  Monitors Gmail account for new messages and creates action files in /Inbox/EMAIL_{id}.md.
  This skill should be used when monitoring Gmail for messages requiring action by the AI Employee.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# GmailWatcher Skill

## Purpose
Monitors Gmail account for new messages and creates action files in `/Inbox/EMAIL_{id}.md` to be processed by the AI Employee system.

## When to Use This Skill
- When monitoring Gmail for new messages requiring action
- As part of the Silver Tier enhancement for the Personal AI Employee
- When implementing multi-source watcher functionality

## Inputs
- **gmail_filter**: The Gmail search filter to apply (default: "is:unread")
- **poll_interval**: How often to check for new emails (default 120 seconds)

## Outputs
- Creates email files in `/Inbox/` with format `EMAIL_{gmail_id}.md`
- Extracts relevant email information and formats it for processing
- Updates system logs with email detection events

## Hook Dependencies
- `.claude/hook/gmail_credentials.hook` - Contains Gmail API credentials

## Approval Required
No - reading emails only

## DRY_RUN Support
Yes - logs intent to check Gmail but doesn't actually poll

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, email formats, log formats |
| **Conversation** | User's specific Gmail filters, frequency requirements, sensitivity levels |
| **Skill References** | Gmail API documentation, email processing patterns, vault conventions |
| **User Guidelines** | Project-specific email handling rules, security requirements |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Read Gmail credentials from hook configuration
2. Authenticate with Gmail API using OAuth2
3. Poll Gmail account at specified intervals
4. Apply filter to identify relevant messages
5. For each new email that matches filter:
   a. Extract sender, subject, snippet, labels
   b. Create markdown file in /Inbox/EMAIL_{id}.md
   c. Include YAML frontmatter with email metadata
   d. Log email detection event
6. Mark processed emails as read in Gmail
```

### Email File Schema
The skill creates files in `/Inbox/` with this structure:

```yaml
---
type: email
from: {sender_email}
subject: {email_subject}
received: {ISO-8601}
priority: {high|medium|low}
status: pending
gmail_id: {gmail_message_id}
labels: [{list_of_gmail_labels}]
---
## Email Content
{email_content_snippet}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
- [ ] Add to task list: {suggested_next_steps}
```

### Error Handling
- If Gmail API is unreachable: wait for next poll interval, log error
- If authentication fails: log error and stop polling (requires credential fix)
- If email processing fails: log error, mark email as read to avoid infinite loop
- If file creation fails: log error separately but continue processing other emails

### Security Considerations
- Never store Gmail credentials in files directly
- Use OAuth2 with proper scopes (read-only for watching)
- Respect Gmail API rate limits
- Filter sensitive content appropriately