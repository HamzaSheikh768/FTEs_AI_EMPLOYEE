# Specification: Silver Tier - Functional Assistant

## Feature Overview

**Feature Name**: Silver Tier - Functional Assistant
**Tier**: Silver
**Status**: Functional Assistant Implementation
**Description**: Extends the Bronze Tier Personal AI Employee with additional watchers, MCP server capabilities, human-in-the-loop approval workflows, LinkedIn business posting, and scheduling functionality. This tier transforms the basic file routing system into a functional assistant that can handle multiple input sources and execute external actions with appropriate approval workflows.

**Dependency**: Bronze Tier must be complete (core vault structure, basic file routing, Agent Skills framework in place)
**Governed By**: `constitution.md` — all rules defined there apply here.

## User Scenarios & Testing

### Primary Scenarios

1. **Multi-Source Watcher Monitoring**
   - As a user, I want multiple watchers monitoring different sources simultaneously
   - Given the system has Gmail and File System watchers active
   - When new emails arrive AND files are dropped to monitored folders
   - Then both sources create appropriate action files in `/Inbox/`
   - And Claude processes both types of files according to business rules

2. **LinkedIn Business Post Automation**
   - As a business owner, I want the AI to post business content to LinkedIn
   - Given I have business goals requiring marketing
   - When the system identifies content worth promoting
   - Then the system creates a LinkedIn post plan in `/Plans/`
   - And waits for approval before posting to LinkedIn
   - And logs the post activity to `/Logs/`

3. **Human-in-the-Loop Approval Workflow**
   - As a user, I want sensitive actions to require my approval
   - Given an email needs to be sent or a payment needs to be made
   - When Claude prepares the action
   - Then the system creates an approval request in `/Pending_Approval/`
   - And waits for me to move the file to `/Approved/` or `/Rejected/`
   - And only executes after I approve

4. **Plan Creation and Management**
   - As a user, I want detailed plans created for complex tasks
   - Given a complex task requires multiple steps
   - When Claude processes the task
   - Then a `/Plans/{task_id}_Plan.md` file is created
   - And the plan includes all required steps with status tracking
   - And each step is tracked until completion

5. **Scheduled Task Execution**
   - As a user, I want automated tasks to run on schedule
   - Given I have recurring business tasks
   - When the scheduled time arrives
   - Then the system triggers the appropriate workflow
   - And logs the scheduled execution attempt

### Edge Cases

- What happens when multiple watchers trigger simultaneously?
- How does the system prioritize different types of tasks?
- What if an MCP server is unavailable when needed?
- How does the system handle approval requests that expire?
- What if scheduled tasks conflict with manual operations?

## Functional Requirements

### FR-1: Multiple Watcher Implementation
**Requirement**: Implement at least two additional watcher scripts beyond the Bronze Tier FileSystemWatcher
- **Gmail Watcher**: Monitor Gmail account for new messages based on filters
- **LinkedIn Watcher**: Monitor LinkedIn for messages/notifications requiring attention
- All watchers must use hook-based credential injection (no `.env` files)
- Each watcher creates appropriately formatted files in `/Inbox/` with proper YAML frontmatter

### FR-2: LinkedIn Business Post Functionality
**Requirement**: Implement capability to automatically generate and post business content to LinkedIn
- Analyze business goals and recent activity to identify content worth promoting
- Create LinkedIn post drafts in proper format
- Implement approval workflow for all social media posts
- Execute posting only after human approval
- Log all social media activity to audit trail

### FR-3: Claude Reasoning Loop with Plan Creation
**Requirement**: Implement Claude's ability to create detailed Plan.md files for complex tasks
- When Claude encounters a task requiring multiple steps, create a Plan.md file in `/Plans/`
- Include step-by-step breakdown with checkboxes for progress tracking
- Update plan status as steps are completed
- Link plan to original task and final completion file
- Implement proper error handling if steps fail

### FR-4: MCP Server Implementation
**Requirement**: Implement at least one working MCP server for external actions
- **Email MCP Server**: Send emails via Gmail API with proper authentication
- MCP server must follow Model Context Protocol standards
- Server handles authentication via hooks (no credentials in files)
- Include proper error handling and status reporting
- Support both draft and send operations

### FR-5: Human-in-the-Loop Approval Workflow
**Requirement**: Implement comprehensive approval system for sensitive actions
- Create approval request files in `/Pending_Approval/` for sensitive actions
- Wait for human to move files to `/Approved/` or `/Rejected/`
- Implement timeout mechanism for pending approvals
- Support different approval levels based on action type and value
- Log all approval decisions to audit trail

### FR-6: Scheduling System
**Requirement**: Implement basic scheduling functionality
- Support cron-like scheduling for recurring tasks
- Allow scheduling of specific actions at specific times
- Handle missed scheduled tasks appropriately
- Log scheduled task execution attempts
- Support both one-time and recurring schedules

### FR-7: Enhanced Agent Skills Framework
**Requirement**: Create all new functionality as Agent Skills following Silver Tier requirements
- GmailWatcher.SKILL.md
- LinkedInPoster.SKILL.md
- PlanCreator.SKILL.md
- HITLApproval.SKILL.md
- EmailMCP.SKILL.md
- SchedulerCron.SKILL.md
- All skills must follow constitution requirements

### FR-8: Enhanced Vault Structure Utilization
**Requirement**: Make full use of all vault directories established in Silver Tier requirements
- Proper use of `/Plans/` directory for multi-step task plans
- Proper use of `/Pending_Approval/`, `/Approved/`, `/Rejected/` directories
- Maintain proper file flow through the complete lifecycle
- Update Dashboard.md with comprehensive status information

## Non-Functional Requirements

### NFR-1: Security & Privacy
- No `.env` files accessed by any component
- All credentials via `.claude/hook/` only
- All sensitive actions require explicit approval
- Audit trail maintained for all actions
- Approval requests include appropriate context for decision

### NFR-2: Performance
- Multiple watchers must not interfere with each other
- MCP server response time under 5 seconds
- Approval workflow should not block system operation
- Scheduled tasks should not create resource contention
- System should handle up to 50 pending approval requests gracefully

### NFR-3: Reliability
- Watchers must recover from temporary API outages
- MCP servers should implement proper retry logic
- Scheduled tasks should have error recovery
- Approval workflow should handle system restarts gracefully
- All operations must be idempotent where possible

### NFR-4: Audit & Monitoring
- All actions logged with timestamp, actor, action, status
- Approval decisions explicitly logged with decision maker identification
- MCP server operations logged with success/failure status
- Scheduled task execution results logged
- System health indicators available through Dashboard.md

## Key Entities

### Entity: Watcher (Extended)
- **Attributes**: name, source_type, poll_interval, credentials_hook, output_format
- **Relationships**: Creates action files in `/Inbox/`, communicates via vault
- **Constraints**: Must use hook-based credential injection, follow YAML schema

### Entity: Plan
- **Attributes**: task_id, steps, status, created_timestamp, completed_steps
- **Relationships**: Links to original task and completion record
- **Constraints**: Must be in `/Plans/` directory, use markdown with checkboxes

### Entity: Approval Request
- **Attributes**: action_type, details, created_timestamp, expiry_time, status
- **Relationships**: Moves between `/Pending_Approval/`, `/Approved/`, `/Rejected/`
- **Constraints**: Must follow approval schema, include clear action information

### Entity: MCP Server
- **Attributes**: name, protocol, authentication_method, capabilities
- **Relationships**: Interacts with Claude Code via MCP protocol
- **Constraints**: Must follow MCP standards, handle authentication securely

### Entity: Scheduled Task
- **Attributes**: trigger_time, action, status, last_execution, recurrence_pattern
- **Relationships**: Triggers other system components
- **Constraints**: Must handle timing precision and system state appropriately

## Success Criteria

### Primary Success Metrics
- [ ] All Bronze Tier functionality continues to operate during Silver Tier implementation
- [ ] At least 2 additional watchers implemented and operational (Gmail + LinkedIn)
- [ ] LinkedIn posting functionality implemented with approval workflow
- [ ] Plan.md generation working for multi-step tasks
- [ ] MCP server successfully sending emails through Gmail
- [ ] Human-in-the-loop approval system operational
- [ ] Scheduling system running recurring tasks
- [ ] All new functionality implemented as Agent Skills per requirements

### Integration Success Metrics
- [ ] Multiple watchers operate concurrently without interference
- [ ] Approval workflow integrates with all sensitive actions
- [ ] MCP server integrates seamlessly with Claude Code
- [ ] Scheduling system coordinates properly with other system components
- [ ] Dashboard shows comprehensive system status including new features

### Quality Success Metrics
- [ ] All Silver Tier requirements from requirements document satisfied
- [ ] Constitution rules fully followed (no .env access, proper hooks)
- [ ] All new skills created via skills-create-pro (no inline scripting)
- [ ] Audit logging comprehensive and properly formatted
- [ ] Security requirements met for all new functionality

## Dependencies & Assumptions

### Dependencies
- Bronze Tier implementation complete and operational
- Claude Code with MCP server support
- Working skills-create-pro command for generating skill files
- Gmail API access and credentials via hooks
- LinkedIn API access and credentials via hooks
- Existing vault structure from Bronze Tier

### Assumptions
- User has provided API credentials through hooks
- Network access available for external API calls
- User will review and approve generated skill files before activation
- MCP server environment properly configured
- Basic understanding of cron scheduling patterns for user configuration