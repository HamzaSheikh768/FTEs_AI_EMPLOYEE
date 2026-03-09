# Bronze Agent Configuration

## Agent Identity
- **Name**: Bronze Tier Personal AI Employee
- **Tier**: Bronze
- **Purpose**: Execute Bronze Tier functionality (File System Watcher, Inbox Routing, Task Completion, Audit Logging)
- **Owner**: Personal AI Employee System
- **Created**: 2026-02-20

## Registered Skills
This agent has access to the following Bronze Tier skills:

1. **FileSystemWatcher**
   - File: `FileSystemWatcher.SKILL.md`
   - Purpose: Monitors a designated folder for file drops and creates action items
   - Trigger: File system events in the configured watch folder
   - Output: Creates metadata files in `/Inbox/`

2. **InboxRouter**
   - File: `InboxRouter.SKILL.md`
   - Purpose: Routes items from `/Inbox/` to `/Needs_Action/` for processing
   - Trigger: New files detected in `/Inbox/`
   - Output: Files moved to `/Needs_Action/` with status updates

3. **TaskCompleter**
   - File: `TaskCompleter.SKILL.md`
   - Purpose: Processes completed tasks and moves them from `/Needs_Action/` to `/Done/`
   - Trigger: Task completion criteria met in `/Needs_Action/`
   - Output: Files moved to `/Done/` with logging

4. **AuditLogger**
   - File: `AuditLogger.SKILL.md`
   - Purpose: Maintains audit trail of all system actions
   - Trigger: Any system action requiring logging
   - Output: Appends entries to `/Logs/{YYYY-MM-DD}.md`

## Operational Parameters
- **DRY_RUN**: true (no external API calls during Bronze tier)
- **Polling Interval**: 120 seconds (for FileSystemWatcher)
- **Dashboard Updates**: Real-time
- **Error Handling**: Log to `/Logs/` and continue operation

## Execution Policy
- All file operations follow the Ralph Wiggum Pattern (read from `/Inbox/`, process in `/Needs_Action/`, complete to `/Done/`)
- All logging follows ISO-8601 timestamp format
- Dashboard updates occur after each significant action
- No `.env` file access allowed per constitution.md
- All credentials injected via hooks from `.claude/hook/`

## Dependencies
- Requires `filesystem_watch.hook` for folder path configuration
- Requires vault directory structure (Inbox, Needs_Action, Done, Logs)
- Requires Company_Handbook.md and Business_Goals.md (Tier 1)
- Requires constitution.md for governance rules