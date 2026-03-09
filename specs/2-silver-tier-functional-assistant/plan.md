# Implementation Plan: Silver Tier - Functional Assistant

## 1. Scope and Dependencies

### In Scope
- Implement Gmail Watcher skill and functionality
- Implement LinkedIn Poster skill and functionality
- Create MCP server for email sending
- Implement Plan creation functionality for complex tasks
- Set up Human-in-the-Loop approval workflow
- Implement scheduling system for recurring tasks
- Integrate all components with existing Bronze Tier system
- Create all new functionality as Agent Skills per constitution
- Ensure all security requirements are met

### Out of Scope
- Gold Tier features (cross-domain integration, CEO briefings)
- Platinum Tier features (cloud deployment)
- Actual business logic for LinkedIn content (this will be user-defined)
- Advanced error recovery beyond basic implementation

### External Dependencies
- Gmail API access and OAuth credentials via hooks
- LinkedIn API access (if available) or web automation approach
- Claude Code with MCP server support
- Node.js for MCP server implementation
- Cron/Task Scheduler access for scheduling features
- Existing Bronze Tier infrastructure

## 2. Key Decisions and Rationale

### Decision 1: LinkedIn Implementation Approach
- **Options Considered**: LinkedIn API vs web automation (Playwright)
- **Trade-offs**: API provides better long-term stability but has restrictions; web automation has risks but more flexibility
- **Rationale**: Start with web automation approach using Playwright (similar to WhatsApp watcher) as it's more feasible for hackathon timeline while respecting LinkedIn's terms of service

### Decision 2: MCP Server Technology
- **Options Considered**: Python FastMCP vs Node.js MCP SDK
- **Trade-offs**: Python might integrate better with existing Python components; Node.js has more MCP examples
- **Rationale**: Use Node.js MCP SDK for better ecosystem support and examples

### Decision 3: Scheduling System
- **Options Considered**: cron on Unix vs Task Scheduler on Windows vs custom Python scheduler
- **Trade-offs**: Native solutions are more reliable but less portable; custom solution is portable but requires more work
- **Rationale**: Implement cross-platform solution with Python scheduler for consistency, with native system integration possible later

### Decision 4: Approval Workflow Implementation
- **Options Considered**: File-based vs database-based approval tracking
- **Trade-offs**: File-based is consistent with vault architecture but might have locking issues; DB would be more robust
- **Rationale**: File-based approach maintains consistency with vault architecture and constitution

## 3. Implementation Architecture

### 3.1 Enhanced Skill Architecture

#### Skill 1: GmailWatcher.SKILL.md
- **Implementation**: Monitor Gmail account using Gmail API
- **Technology**: Google APIs Python Client library
- **Credentials**: Injected via hook (credentials file path)
- **Output**: Creates email files in `/Inbox/EMAIL_{id}.md` format

#### Skill 2: LinkedInPoster.SKILL.md
- **Implementation**: Create LinkedIn post drafts and post with approval
- **Technology**: Playwright for web automation
- **Credentials**: Session file path injected via hook
- **Output**: Creates post files in `/Pending_Approval/` requiring human approval

#### Skill 3: PlanCreator.SKILL.md
- **Implementation**: Generate detailed Plan.md files for complex tasks
- **Technology**: File I/O operations, Claude reasoning integration
- **Output**: Creates `/Plans/{task_id}_Plan.md` with step-by-step checklist

#### Skill 4: HITLApproval.SKILL.md
- **Implementation**: Manage approval workflow between vault directories
- **Technology**: File system monitoring, vault integration
- **Output**: Moves files between `/Pending_Approval/`, `/Approved/`, `/Rejected/`

#### Skill 5: EmailMCP.SKILL.md
- **Implementation**: Skill for using Email MCP server capabilities
- **Technology**: MCP protocol integration
- **Output**: Uses MCP server to send emails via Gmail

#### Skill 6: SchedulerCron.SKILL.md
- **Implementation**: Manage scheduled tasks and execution
- **Technology**: Python scheduling libraries
- **Output**: Triggers other system components at scheduled times

### 3.2 MCP Server Architecture

#### Email MCP Server
- **Technology**: Node.js with @modelcontextprotocol/sdk
- **Capabilities**: send_email, draft_email, get_sent_status
- **Authentication**: Credentials injected via hook at runtime
- **Integration**: Claude Code MCP client connects to server

### 3.3 Integration Architecture

#### Approval Workflow Integration
```
Complex Action Identified
  ↓
Claude creates approval file in /Pending_Approval/
  ↓
HITLApproval skill monitors folder
  ↓
Human moves file to /Approved/
  ↓
Action executes via MCP server
  ↓
Completion logged to /Logs/
```

#### Plan Creation Integration
```
Multi-step Task Identified
  ↓
PlanCreator skill generates /Plans/{id}_Plan.md
  ↓
Claude follows plan steps sequentially
  ↓
Progress tracked via markdown checkboxes
  ↓
Completed plan moved to /Done/ when finished
```

## 4. Implementation Tasks

### Phase 1: Enhanced Watchers Setup
1. Create GmailWatcher.SKILL.md using skills-create-pro
2. Implement Gmail API authentication via hooks
3. Test Gmail polling functionality
4. Create LinkedInPoster.SKILL.md using skills-create-pro
5. Set up Playwright for LinkedIn automation
6. Test LinkedIn draft creation functionality

### Phase 2: MCP Server Development
7. Create Email MCP server using Node.js
8. Implement send_email capability with Gmail API
9. Set up MCP server authentication via hooks
10. Test MCP server connection from Claude Code
11. Create EmailMCP.SKILL.md for using the server

### Phase 3: Approval Workflow Implementation
12. Create HITLApproval.SKILL.md using skills-create-pro
13. Implement file monitoring for approval directories
14. Test approval workflow with sample tasks
15. Set up approval timeout mechanisms
16. Create approval logging functionality

### Phase 4: Plan Creation System
17. Create PlanCreator.SKILL.md using skills-create-pro
18. Implement Plan.md template system
19. Test plan creation for multi-step tasks
20. Integrate plan checking with Claude workflows
21. Set up plan status tracking

### Phase 5: Scheduling System
22. Create SchedulerCron.SKILL.md using skills-create-pro
23. Implement Python-based scheduling system
24. Test scheduled task execution
25. Set up recurring task management
26. Integrate with existing vault workflows

### Phase 6: Integration and Testing
27. Test full workflow: Gmail → Plan → Approval → Action → Log
28. Test LinkedIn posting workflow with approval
29. Verify all Agent Skills work properly
30. Test error handling and recovery
31. Update Dashboard.md with new metrics
32. Validate all constitution requirements

## 5. Non-Functional Requirements and Constraints

### Performance Requirements
- Gmail polling should not exceed API rate limits (typically 500 requests/day/user)
- MCP server response time should be under 5 seconds
- Approval workflow should not block system operation
- Scheduling system should handle up to 100 scheduled tasks

### Security Requirements
- All credentials stored in hooks, never in files or code
- MCP server authentication via hooks only
- Approval system prevents unauthorized actions
- LinkedIn automation complies with terms of service
- All sensitive actions require explicit approval

### Reliability Requirements
- Watchers should recover from temporary API outages
- MCP server should handle connection failures gracefully
- Scheduled tasks should be resilient to system restarts
- Approval system should preserve state across restarts

## 6. Data Flow and Processing

### Multi-Source Watcher Flow
```
Gmail API → GmailWatcher → /Inbox/EMAIL_{id}.md
LinkedIn notifications → LinkedInWatcher → /Inbox/LINKEDIN_{id}.md
File system → FileSystemWatcher → /Inbox/FILE_{id}.md
All converge → Claude processes from /Needs_Action/
```

### Approval-Critical Flow
```
Action identified as sensitive
  ↓
Claude creates approval request in /Pending_Approval/
  ↓
HITLApproval skill monitors and logs the request
  ↓
Human reviews and moves to /Approved/ or /Rejected/
  ↓
If Approved: MCP server executes the action
  ↓
Result logged and task completed
```

### Plan-Driven Flow
```
Complex task identified
  ↓
PlanCreator creates /Plans/{id}_Plan.md with steps
  ↓
Claude executes each step, updating plan checkboxes
  ↓
Progress tracked until all steps complete
  ↓
Plan moved to /Done/ with reference to results
```

## 7. Operational Readiness

### Logging and Monitoring
- All new actions logged to `/Logs/{YYYY-MM-DD}.md`
- Approval decisions explicitly logged with timestamp and action
- MCP server operations logged with success/failure
- Dashboard updated with new metrics and status indicators

### Runbooks
- Gmail Watcher setup and authentication
- LinkedIn poster configuration and compliance
- MCP server deployment and maintenance
- Approval workflow troubleshooting
- Scheduled task management

### Deployment Strategy
- Tier 2 (Silver) auto-completes via skill creation
- MCP servers deployed separately from core system
- Rollback: Disable skills without affecting Bronze Tier

## 8. Risk Analysis and Mitigation

### Risk 1: Gmail API Limitations
- **Impact**: Rate limiting or API changes breaking functionality
- **Probability**: Medium (API terms change periodically)
- **Mitigation**: Implement proper rate limiting, error handling, and quota management
- **Blast Radius**: Gmail Watcher functionality only

### Risk 2: LinkedIn Terms of Service Violation
- **Impact**: Account suspension due to automation
- **Probability**: Medium (LinkedIn actively prevents automation)
- **Mitigation**: Implement human-like delays, respect limits, consider alternative approaches
- **Blast Radius**: LinkedIn functionality only

### Risk 3: MCP Server Security
- **Impact**: Credentials exposed or unauthorized actions
- **Probability**: Low but high severity if occurs
- **Mitigation**: Proper hook-based authentication, request validation, minimal permissions
- **Blast Radius**: Could affect email system

### Risk 4: Approval Workflow Bottleneck
- **Impact**: System becomes unusable if too many approvals required
- **Probability**: Medium (depends on user settings)
- **Mitigation**: Proper classification of what requires approval, user-configurable thresholds
- **Blast Radius**: Affects all sensitive actions

## 9. Testing Strategy

### Unit Tests
- Individual skill functionality
- MCP server capability functions
- File operation functions
- Scheduling logic

### Integration Tests
- End-to-end watcher flows
- Approval workflow from creation to execution
- Plan creation and completion
- MCP server integration with Claude Code

### System Tests
- Multi-source concurrent operation
- Error recovery scenarios
- Security validation (no credential leaks)
- Performance under load

## 10. Success Criteria Verification

### Verification Steps
1. Confirm all 6 new skills created via skills-create-pro
2. Test Gmail Watcher successfully monitoring emails
3. Test LinkedIn poster creating drafts with approval workflow
4. Verify MCP server sending emails through Gmail
5. Confirm approval workflow working for sensitive actions
6. Test Plan creation and tracking for multi-step tasks
7. Validate scheduling system executing tasks correctly
8. Verify all functionality follows constitution (no .env access, proper hooks)

### Acceptance Criteria
- [ ] Gmail Watcher creates email files in Inbox
- [ ] LinkedIn poster drafts content for approval
- [ ] MCP server successfully sends emails
- [ ] Approval workflow properly routes files and enables actions
- [ ] Plan creation works for multi-step tasks
- [ ] Scheduling system executes tasks as configured
- [ ] All new functionality implemented as Agent Skills
- [ ] Constitution requirements followed (no .env files, hooks for credentials)
- [ ] Dashboard updated with Silver Tier features

## 11. Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Enhanced Watchers Setup | 6 hours | Gmail/LinkedIn watchers functional |
| MCP Server Development | 5 hours | Email MCP server operational |
| Approval Workflow | 4 hours | Complete approval system working |
| Plan Creation System | 3 hours | Plan generation and tracking |
| Scheduling System | 4 hours | Scheduling functionality |
| Integration & Testing | 8 hours | Full system validation |

**Total estimated time**: 30 hours