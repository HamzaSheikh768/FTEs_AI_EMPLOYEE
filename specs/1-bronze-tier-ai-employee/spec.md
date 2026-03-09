# Specification: Bronze Tier - Personal AI Employee

## Feature Overview

**Feature Name**: Bronze Tier - Personal AI Employee Foundation
**Tier**: Bronze
**Status**: Minimum Viable Deliverable
**Description**: Establish the foundational skeleton of the Personal AI Employee: a live Obsidian vault Claude Code can read from and write to, a single functioning Watcher that detects external events, and a basic folder routing system. Every piece of AI functionality must be delivered as a registered Agent Skill — no inline scripting.

**Dependency**: Tier 1 file system must be complete before this tier begins.
**Governed By**: `constitution.md` — all rules defined there apply here.

## User Scenarios & Testing

### Primary Scenarios

1. **Email Monitoring and Classification**
   - As a user, I want an AI employee to monitor my Gmail account and automatically classify incoming emails
   - Given I have configured Gmail credentials via hooks
   - When new emails arrive
   - Then the system should create `.md` files in the `/Inbox/` folder with proper metadata
   - And mark emails as requiring action based on content

2. **File Drop Monitoring**
   - As a user, I want an AI employee to monitor a designated folder for dropped files
   - Given I have configured a watch folder
   - When a new file is dropped in the watch folder
   - Then the system should create metadata files in `/Inbox/` and copy the original file
   - And mark the file for processing

3. **Task Routing and Processing**
   - As a user, I want incoming items to be automatically routed from `/Inbox/` to `/Needs_Action/`
   - Given I have items in the `/Inbox/` folder
   - When the routing system detects new items
   - Then the items should be moved to `/Needs_Action/` folder
   - And the dashboard should update with the new item count

4. **Task Completion and Logging**
   - As a user, I want completed tasks to be properly archived with audit trails
   - Given I have processed items in `/Needs_Action/` folder
   - When the completion process runs
   - Then items should be moved to `/Done/` folder
   - And log entries should be created in `/Logs/{YYYY-MM-DD}.md`

5. **Dashboard Monitoring**
   - As a user, I want to monitor the status of my AI employee through a dashboard
   - Given the system is running
   - When I view the dashboard
   - Then I should see the current status, task queue counts, and recent activity

### Edge Cases

- What happens when the system is offline during email/file drop events?
- How does the system handle very large files?
- What if the destination folder is full or has write permissions issues?
- How does the system handle files with special characters in names?

## Functional Requirements

### FR-1: Vault Structure Setup
**Requirement**: The system must create and maintain the required folder structure in the Obsidian vault
- Create `/Inbox/`, `/Needs_Action/`, `/Done/`, and `/Logs/` folders
- These folders must be accessible to Claude Code for read/write operations

### FR-2: Watcher Skill Creation
**Requirement**: The system must create at least one Watcher skill (Gmail or FileSystem) using `skills-create-pro`
- Choose between GmailWatcher or FileSystemWatcher based on user preference
- The chosen skill must poll or monitor at appropriate intervals
- All credentials must be injected via hooks, never stored in `.env` files

### FR-3: Inbox Routing System
**Requirement**: The system must route items from `/Inbox/` to `/Needs_Action/` folder
- Monitor `/Inbox/` for new files
- Move files to `/Needs_Action/` folder upon detection
- Update Dashboard.md with current counts

### FR-4: Task Completion System
**Requirement**: The system must move processed items from `/Needs_Action/` to `/Done/` folder
- Monitor `/Needs_Action/` for completed items
- Move completed items to `/Done/` folder
- Log completion events to daily log files

### FR-5: Audit Logging
**Requirement**: The system must maintain an append-only audit trail in `/Logs/`
- Log all system actions with ISO-8601 timestamp
- Include agent name, action type, status, and file reference
- Create daily log files in format `/Logs/YYYY-MM-DD.md`

### FR-6: Dashboard Maintenance
**Requirement**: The system must maintain a live dashboard at `/Dashboard.md`
- Update dashboard with system status and current task counts
- Show recent log entries
- Display any system alerts or errors

### FR-7: Vault Read/Write Verification
**Requirement**: The system must verify Claude Code can read from and write to the vault
- Execute a self-verification sequence
- Confirm all folder permissions are correct
- Test file creation and movement operations

## Non-Functional Requirements

### NFR-1: Security
- No direct access to `.env` files by any skill or agent
- Credentials must be injected via `.claude/hook/` only
- All skills must default to `DRY_RUN=true` until explicitly enabled

### NFR-2: Performance
- Watcher skills should poll every 120 seconds by default
- File operations should complete within 5 seconds
- Dashboard updates should happen in real-time

### NFR-3: Reliability
- Log entries must be retained for minimum 90 days
- System should recover automatically from temporary failures
- All operations must be idempotent where possible

### NFR-4: Audit Trail
- All logs must be append-only with no modification capability
- Log entries must follow exact format: `[ISO-8601] | AGENT:{name} | ACTION:{action} | STATUS:{status} | file:{filename}`
- No personal information should be logged without user consent

## Key Entities

### Entity: Watcher
- **Attributes**: skill_file, trigger_interval, input_source, output_destination, hook_dependency
- **Relationships**: Creates action files in `/Inbox/`
- **Constraints**: Must use hook-based credential injection

### Entity: Action File
- **Attributes**: type, source, timestamp, priority, status, content
- **Relationships**: Moves from `/Inbox/` → `/Needs_Action/` → `/Done/`
- **Constraints**: Must follow YAML frontmatter schema

### Entity: Log Entry
- **Attributes**: timestamp, agent, action, status, file_reference
- **Relationships**: Belongs to daily log file `/Logs/YYYY-MM-DD.md`
- **Constraints**: Append-only, immutable format

### Entity: Dashboard
- **Attributes**: generation_time, system_status, task_counts, recent_logs
- **Relationships**: Updated by all system components
- **Constraints**: Auto-generated, no manual editing allowed

## Success Criteria

### Primary Success Metrics
- [ ] Vault folder structure is created and accessible to Claude Code
- [ ] At least one Watcher skill (Gmail or FileSystem) is created and operational
- [ ] Inbox routing system successfully moves items from `/Inbox/` to `/Needs_Action/`
- [ ] Task completion system successfully moves items from `/Needs_Action/` to `/Done/`
- [ ] Audit logging system creates entries in `/Logs/YYYY-MM-DD.md` format
- [ ] Dashboard is created and updated with system status
- [ ] All four required skills (GmailWatcher/FileSystemWatcher, InboxRouter, TaskCompleter, and audit logging) are created via `skills-create-pro`
- [ ] Claude Code read/write verification completes successfully
- [ ] Bronze tier completion gate is reached with proper log entry

### Performance Metrics
- [ ] Watcher polling occurs at specified intervals (120 seconds by default)
- [ ] File routing completes within 5 seconds of detection
- [ ] System verifies vault access within 30 seconds of startup
- [ ] Dashboard updates occur in real-time (within 1 second of data change)

### Quality Metrics
- [ ] All operations follow the constitution.md rules (no `.env` access, credential injection via hooks)
- [ ] System generates proper audit trail with all required fields
- [ ] Dashboard shows accurate task queue counts
- [ ] No manual configuration files are created in the process

## Dependencies & Assumptions

### Dependencies
- Claude Code environment with access to the project directory
- Access to `.claude/skills/`, `.claude/hook/`, and `.claude/agents/` directories
- Working `skills-create-pro` command for generating skill files
- Existing `constitution.md` file with proper rules

### Assumptions
- The human has already created Tier 1 foundation (folder structure and human-authored documents)
- The AI employee has read permissions to the vault
- Required system commands (file operations, logging) are available
- The system can create and modify files in the vault directory
- The user has approved the creation of this automated system