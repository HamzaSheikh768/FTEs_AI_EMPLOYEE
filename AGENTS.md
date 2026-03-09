# AGENTS.md - Personal AI Employee Agent Definitions

## Overview
This document defines the specialized agents for the Personal AI Employee system. Each agent has specific capabilities and skills designed to handle different aspects of personal and business automation, following the hackathon requirements for Bronze, Silver, Gold, and Platinum tiers.

## Core Architecture Agents

### 1. Orchestrator Agent
**Purpose**: Master coordinator for all AI Employee components
- **Role**: Manages all other agents, handles scheduling, health monitoring
- **Skills**:
  - Process management (start/stop/restart services)
  - Health checks and monitoring
  - Scheduling and periodic task execution
  - File system orchestration
  - Folder monitoring with real-time change detection
- **Capabilities**: Runs 24/7, manages all watcher processes, implements "Ralph Wiggum" persistence loop
- **Configuration**: Monitors Gmail, LinkedIn, file system inputs, and folder changes across all vault directories
- **Monitoring**: Tracks all vault folders (Inbox, Needs_Action, Plans, Done, Pending_Approval, Approved, Rejected)

### 2. Gmail Watcher Agent
**Purpose**: Monitors Gmail account for new messages and creates action files
- **Role**: Email triage and processing
- **Skills**:
  - Gmail API integration (read, modify scopes)
  - Email parsing and categorization
  - Urgency detection (urgent, asap, immediate, critical keywords)
  - Priority classification (high/medium/low)
  - Secure credential handling via OAuth2
  - Email body decoding and content extraction
- **Capabilities**: Reads unread emails, creates .md files in /Needs_Action, marks emails as read
- **Configuration**: Checks every 120 seconds, filters for important emails with YAML frontmatter

### 3. LinkedIn Poster Agent
**Purpose**: Creates and manages LinkedIn posts for business promotion
- **Role**: Social media automation
- **Skills**:
  - LinkedIn API/web automation
  - Content generation and approval workflow
  - Auto-posting for safe content (business promotion, value posts, no personal data)
  - HITL (Human-in-the-Loop) for sensitive content
  - Content classification for auto-approval (>90% confidence required)
- **Capabilities**: Auto-posts business promotion content (100-500 chars), routes complex content to /Pending_Approval
- **Configuration**: Auto-posts if confidence >90% that content is safe & on-brand, requires approval for all other posts

**MCP Tools Available**:
- `create_linkedin_post_draft`: Creates a LinkedIn post draft that requires human approval
- `approve_linkedin_post`: Moves a LinkedIn post from pending approval to approved status

### 4. File System Watcher Agent
**Purpose**: Monitors local file system for changes and new files
- **Role**: File-based input processing
- **Skills**:
  - File system monitoring (watchdog patterns)
  - File type detection and categorization
  - Metadata extraction
  - File movement and organization
- **Capabilities**: Detects file drops, creates metadata files, moves to appropriate folders
- **Configuration**: Monitors specified directories for new files

### 5. Inbox Router Agent
**Purpose**: Routes incoming files to appropriate action queues
- **Role**: File routing and classification
- **Skills**:
  - Content analysis and classification
  - Sensitive content detection (password, credential, private, confidential, secret, token)
  - File routing logic
  - Priority assignment
- **Capabilities**: Moves files from /Inbox to /Needs_Action, /Pending_Approval, or /Done based on content
- **Configuration**: Uses keyword analysis for sensitive content detection

## Business Logic Agents

### 6. Approval Workflow Agent
**Purpose**: Manages human-in-the-loop approval processes
- **Role**: Approval request handling
- **Skills**:
  - Approval file generation
  - Approval status tracking
  - Escalation management
  - Security threshold enforcement
  - Sensitive action classification
- **Capabilities**: Creates approval files in /Pending_Approval, monitors for human approval
- **Configuration**: Handles payments, sensitive communications, and critical decisions

### 7. Plan Creation Agent
**Purpose**: Generates detailed plans for complex tasks using SDD (Spec-Driven Development)
- **Role**: Task planning and organization
- **Skills**:
  - Task decomposition
  - Plan.md generation with SDD compliance
  - Step-by-step workflow creation
  - Progress tracking
  - Specification generation
- **Capabilities**: Creates SDD-compliant plan files, breaks down complex tasks
- **Configuration**: Generates plans for multi-step processes with proper specification adherence

### 8. Auto-Needs-to-Done Agent
**Purpose**: Automates simple file processing from Needs_Action to Done
- **Role**: Simple task execution
- **Skills**:
  - Simple file processing
  - Pattern recognition
  - Automated completion
  - Status tracking
  - Duplicate file cleanup
- **Capabilities**: Processes non-sensitive tasks directly from /Needs_Action to /Done
- **Configuration**: Handles routine, low-risk tasks

### 9. Process Action Agent
**Purpose**: Executes specific actions based on file content
- **Role**: Action execution
- **Skills**:
  - Action execution
  - API integration
  - Error handling
  - Result logging
  - Multi-step workflow execution
- **Capabilities**: Performs specific actions based on task files
- **Configuration**: Integrates with MCP servers for external actions

## Reporting Agents

### 10. Scheduler Agent
**Purpose**: Manages periodic tasks and scheduled operations
- **Role**: Task scheduling
- **Skills**:
  - Cron-style scheduling
  - Periodic task execution
  - Time-based triggers
  - Recurring job management
  - Business audit scheduling
- **Capabilities**: Runs daily briefings, weekly audits, monthly reports
- **Configuration**: Handles all time-based automation

### 11. Monday Morning CEO Briefing Agent
**Purpose**: Generates weekly business reports and CEO briefings transforming the AI from a chatbot into a proactive business partner
- **Role**: Business analytics and reporting
- **Skills**:
  - Data aggregation from multiple sources
  - Business metrics calculation (revenue, bottlenecks, KPIs)
  - Report generation with standard format
  - Trend analysis
  - Proactive suggestion generation
- **Capabilities**: Creates Monday Morning CEO Briefing files with revenue, bottlenecks, and suggestions
- **Configuration**: Runs weekly (typically Sunday night), analyzes Business_Goals.md, checks Tasks/Done folder, and analyzes Bank_Transactions.md

### 12. Accounting Audit Agent
**Purpose**: Monitors and audits business financials
- **Role**: Financial oversight
- **Skills**:
  - Transaction analysis
  - Subscription monitoring
  - Cost optimization
  - Revenue tracking
  - Subscription usage detection
- **Capabilities**: Audits bank transactions, identifies unused subscriptions, tracks monthly costs
- **Configuration**: Monitors /Accounting/ for transaction analysis, flags unused services

## Specialized MCP Agents

### 13. Email MCP Agent
**Purpose**: Handles email sending and management via Model Context Protocol
- **Role**: Email execution
- **Skills**:
  - Email composition
  - Secure sending
  - Attachment handling
  - Delivery tracking
  - Bulk send management
- **Capabilities**: Sends approved emails, handles attachments, tracks delivery status
- **Configuration**: Requires approval for new contacts and bulk sends, auto-sends to known contacts

### 14. Browser MCP Agent
**Purpose**: Handles web-based actions via Model Context Protocol
- **Role**: Web automation
- **Skills**:
  - Browser automation
  - Form filling
  - Click automation
  - Session management
  - Payment processing
- **Capabilities**: Performs web-based tasks like payment processing, form submissions
- **Configuration**: Used for banking and payment portals

### 15. WhatsApp MCP Agent (Silver Tier)
**Purpose**: Handles WhatsApp communication via Model Context Protocol
- **Role**: WhatsApp automation
- **Skills**:
  - WhatsApp Web automation
  - Message sending and receiving
  - Contact management
  - Business communication
- **Capabilities**: Sends approved WhatsApp messages, handles business communications
- **Configuration**: Used for business communications requiring human verification

## Platinum Tier Agents

### 16. Cloud Sync Agent (Platinum Tier)
**Purpose**: Manages synchronization between cloud and local AI employees
- **Role**: Cross-domain sync and coordination
- **Skills**:
  - Vault synchronization
  - Conflict resolution
  - Domain ownership management
  - Git-based sync
- **Capabilities**: Syncs files between cloud and local agents while maintaining security boundaries
- **Configuration**: Only syncs markdown/state, never syncs secrets (.env, tokens, payment creds)

### 17. Work-Zone Specialization Agent (Platinum Tier)
**Purpose**: Manages work distribution between cloud and local agents
- **Role**: Domain ownership and delegation
- **Skills**:
  - Task distribution
  - Claim-by-move pattern implementation
  - Work ownership tracking
  - Local/cloud role management
- **Capabilities**: Ensures cloud handles email/social while local handles payments/whatsapp
- **Configuration**: Implements single-writer rule for Dashboard.md (local-only), cloud writes updates to /Updates/

## Agent Communication Protocol

### File-Based Communication
All agents communicate through the Obsidian vault file system:
- `/Inbox/` - New items for processing
- `/Needs_Action/` - Items requiring action
- `/Plans/` - Detailed plans and workflows
- `/Pending_Approval/` - Items requiring human approval
- `/Approved/` - Approved items for execution
- `/Rejected/` - Rejected items
- `/Done/` - Completed items
- `/Logs/` - Audit logs
- `/Briefings/` - Generated reports
- `/Accounting/` - Financial records
- `/Updates/` - System updates and signals
- `/Approved/` - Human-approved actions
- `/Rejected/` - Human-rejected actions

### Standard File Format
```markdown
---
type: [email|whatsapp|payment|approval_request|briefing|file_drop]
from: [sender] (for emails)
to: [recipient] (for emails)
subject: [subject] (for emails)
received: [datetime]
priority: [high|medium|low]
status: [pending|in_progress|completed|failed]
gmail_id: [Gmail message ID] (for emails)
labels: [Gmail labels] (for emails)
created: [2026-01-07T10:30:00Z] (for approvals)
amount: [500.00] (for payments)
recipient: [Client A] (for payments)
---
```

### Communication Patterns
1. **Trigger Pattern**: Watchers create files in /Needs_Action
2. **Planning Pattern**: Reasoning agent creates /Plans/PLAN_*.md
3. **Approval Pattern**: Files moved from /Pending_Approval to /Approved
4. **Completion Pattern**: Files moved from /Needs_Action to /Done
5. **Claim-by-Move Pattern**: First agent moves item to /In_Progress/<agent>/ owns it

## Security & Safety Features

- **Auto-Approve Thresholds**: Based on risk level and historical patterns
- **Always Require Approval**: For new contacts, payments over $500, sensitive content
- **Audit Logging**: All actions logged with timestamp, actor, and result
- **Credential Isolation**: Sensitive credentials stored separately (.env), never synced
- **Rate Limiting**: Maximum actions per hour (e.g., max 10 emails, max 3 payments)
- **Dry Run Mode**: All action scripts support --dry-run flag

## Agent Skills Framework
All AI functionality should be implemented as [Agent Skills](https://platform.claude.com/docs/en/agents-and-tools/agent-skills/overview) according to the Claude Code Agent Skills specification.

## Permissions and Boundaries
| Action Category | Auto-Approve Threshold | Always Require Approval |
| :---- | :---- | :---- |
| Email replies | To known contacts | New contacts, bulk sends |
| Payments | < $50 recurring | All new payees, > $100 |
| Social media | Scheduled posts | Replies, DMs |
| File operations | Create, read | Delete, move outside vault |

## Error Handling & Recovery
- **Transient Errors**: Exponential backoff retry
- **Authentication**: Alert human, pause operations
- **Logic Errors**: Human review queue
- **Data Errors**: Quarantine + alert
- **System Errors**: Watchdog + auto-restart