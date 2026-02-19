# Personal AI Employee Agents

This document outlines the various specialized agents that will work together to form your Personal AI Employee system as described in the hackathon requirements.

## Core Agents

### 1. Orchestrator Agent
**Role**: Central coordination and process management
- Manages the main workflow and timing
- Monitors folder structures for changes
- Coordinates between other agents
- Implements the "Ralph Wiggum" persistence loop
- Handles process management and health monitoring

### 2. Perception Agents (Watchers)

#### Gmail Watcher Agent
**Role**: Monitors Gmail for new messages requiring action
- Uses Gmail API to check for unread/important emails
- Creates markdown files in /Needs_Action when triggers found
- Identifies priority messages based on keywords/rules
- Handles OAuth authentication and token management

#### WhatsApp Watcher Agent
**Role**: Monitors WhatsApp for messages requiring action
- Uses Playwright for WhatsApp Web automation
- Detects messages with trigger keywords
- Creates action items in /Needs_Action
- Respects WhatsApp's terms of service

#### File System Watcher Agent
**Role**: Monitors local file system for new files
- Watches designated drop folders
- Moves files to processing queues
- Creates metadata files for new uploads
- Handles file-based triggers

#### Finance Watcher Agent
**Role**: Monitors banking/financial transactions
- Interfaces with banking APIs or CSV imports
- Identifies transactions requiring attention
- Updates accounting records in /Accounting
- Flags unusual or high-value transactions

### 3. Reasoning Agent (Claude Code)
**Role**: Core decision-making and planning
- Reads files from multiple vault directories
- Creates detailed plans in /Plans
- Interprets company handbook and business rules
- Generates CEO briefings and audits
- Implements human-in-the-loop approval workflows

### 4. Action Agents (MCP Servers)

#### Email MCP Agent
**Role**: Handles email sending and management
- Sends approved emails via Gmail API
- Drafts email responses
- Manages email templates
- Implements approval requirements for sensitive sends

#### Browser MCP Agent
**Role**: Handles web-based actions
- Automates payment portals and banking sites
- Fills forms and submits data
- Handles authentication for various services
- Implements security safeguards for financial actions

#### Social Media MCP Agent
**Role**: Manages social media posts and interactions
- Posts scheduled content to LinkedIn, Twitter, etc.
- Monitors for engagement
- Handles automated responses based on rules
- Respects platform-specific guidelines

### 5. Human-in-the-Loop Agent
**Role**: Manages approval workflows
- Creates approval request files in /Pending_Approval
- Monitors /Approved and /Rejected folders
- Implements approval rules based on transaction values
- Handles escalation for unusual situations

## Agent Communication Protocol

All agents communicate through the Obsidian vault file system using standardized markdown formats with YAML frontmatter:

### Standard File Format
```markdown
---
type: [email|whatsapp|payment|approval_request|briefing]
created: 2026-02-20T10:00:00Z
status: [pending|in_progress|completed|failed]
priority: [high|medium|low]
---
```

### Communication Patterns
1. **Trigger Pattern**: Watchers create files in /Needs_Action
2. **Planning Pattern**: Reasoning agent creates /Plans/PLAN_*.md
3. **Approval Pattern**: Files moved from /Pending_Approval to /Approved
4. **Completion Pattern**: Files moved from /Needs_Action to /Done

## Security & Safety Features

- All sensitive actions require human approval via file movement
- Financial transactions have value-based approval thresholds
- Rate limiting prevents spam or excessive actions
- All actions logged in /Logs for audit trail
- Credentials stored securely, never in vault

## Agent Skills Required

Each agent should implement these core skills:
- File system I/O for vault communication
- API integration for external services
- Error handling and retry logic
- Security and audit logging
- Configuration management