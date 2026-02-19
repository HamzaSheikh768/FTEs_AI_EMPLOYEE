---
name: update-dashboard.md
Description: This skill updates the `Dashboard.md` file with real-time information about pending actions, recent activity, and quick stats. It provides a single source of truth for the current state of the AI Employee system.
---

# Update Dashboard

Refresh the Dashboard with current system status and activity.

## Instructions

1. **Gather Current Status**

   a. **Count Files in Each Folder**
      - Count `.md` files in `AI_Employee_Vault/Needs_Action/` (pending actions)
      - Count `.md` files in `AI_Employee_Vault/Plans/` (active plans)
      - Count `.md` files in `AI_Employee_Vault/Done/` (completed tasks)

   b. **Check Watcher Status**
      - Look for most recent log entry in today's log file
      - If last entry < 5 minutes ago: 🟢 Running
      - If last entry 5-15 minutes ago: 🟡 Slow
      - If last entry > 15 minutes ago: 🔴 Stopped

2. **Get Pending Actions List**
   - Read all files in `AI_Employee_Vault/Needs_Action/`
   - For each file with `status: pending` or `status: in_progress`:
     - Extract: filename, priority, detected timestamp
     - Format as list item with emoji indicator:
       - 🔴 High priority
       - 🟡 Medium priority
       - 🟢 Low priority

3. **Get Recent Activity**
   - Read all files in `AI_Employee_Vault/Done/`
   - Sort by completion timestamp (most recent first)
   - Take top 5 completed items
   - Format with completion timestamp and brief description

4. **Calculate Today's Stats**
   - Files Processed Today: Count log entries for today
   - Active Tasks: Count of pending + in_progress items
   - Completed This Week: Count Done folder items from past 7 days

5. **Update Dashboard.md**
   - Read current `AI_Employee_Vault/Dashboard.md`
   - Update the frontmatter `last_updated` field
   - Replace each section with fresh data:
     - System Status
     - Pending Actions
     - Recent Activity
     - Quick Stats

## Dashboard Template

Update Dashboard.md to match this structure:

```markdown
---
last_updated: [ISO timestamp]
---

# AI Employee Dashboard

## System Status
- Watcher Status: [🟢 Running / 🟡 Slow / 🔴 Stopped]
- Last Check: [timestamp of most recent log entry]

## Pending Actions
[List of pending items with priorities, or "No pending actions"]

## Recent Activity
[List of last 5 completed items, or "No recent activity"]

## Quick Stats
- Files Processed Today: [count]
- Active Tasks: [count]
- Completed This Week: [count]
```

## Success Criteria
- Dashboard.md is updated with current timestamp
- All counts are accurate
- Watcher status reflects latest activity
- Pending actions list is current
- Recent activity shows latest completions

## Example Output

After running `claude skill update-dashboard`:

```markdown
---
last_updated: 2026-01-10T14:30:00Z
---

# AI Employee Dashboard

## System Status
- Watcher Status: 🟢 Running
- Last Check: 2026-01-10T14:28:45Z

## Pending Actions
- 🔴 FILE_20260110_142301_invoice_client_a.md (detected 10 minutes ago)
- 🟡 FILE_20260110_140512_message_from_client.md (detected 45 minutes ago)

## Recent Activity
- [2026-01-10 14:15] Processed invoice for Client B - $2,500
- [2026-01-10 13:45] Created social media post draft
- [2026-01-10 11:20] Responded to client inquiry

## Quick Stats
- Files Processed Today: 8
- Active Tasks: 2
- Completed This Week: 15
```

## Related Skills
- Use `process-needs-action` to process the pending items listed
- Use `complete-task` to move items to Done folder