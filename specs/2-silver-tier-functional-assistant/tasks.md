# Implementation Tasks: Silver Tier - Functional Assistant

## Phase 1: Enhanced Watchers Setup

### Task 1.1: Create GmailWatcher.SKILL.md
- **Description**: Generate the GmailWatcher skill file using skills-create-pro
- **Files**: .claude/skills/GmailWatcher.SKILL.md
- **Dependencies**: Bronze Tier completed, Gmail API credentials ready
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Confirm skill file exists and follows schema from spec
  - Verify skill declares all required fields: name, description, inputs, outputs, trigger_conditions, hook_dependencies, approval_required
  - Check that approval_required is set appropriately based on email sensitivity

### Task 1.2: Set up Gmail API authentication via hooks
- **Description**: Create hook configuration for Gmail API credentials
- **Files**: .claude/hook/gmail_credentials.hook
- **Dependencies**: Task 1.1 completed
- **Priority**: High
- **Effort**: Low
- **Test**:
  - Verify hook file exists with proper structure
  - Confirm it can inject Gmail credentials at runtime
  - Check that no credentials are stored in plain text

### Task 1.3: Implement Gmail polling functionality
- **Description**: Create the actual Gmail polling script that will be used by the skill
- **Files**: .claude/skills/gmail_watcher_impl.py
- **Dependencies**: Tasks 1.1 and 1.2 completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Run script to verify it can authenticate with Gmail API
  - Confirm it can detect new emails based on filters
  - Verify it creates properly formatted files in /Inbox/EMAIL_*.md
  - Test rate limiting compliance

### Task 1.4: Create LinkedInPoster.SKILL.md
- **Description**: Generate the LinkedInPoster skill file using skills-create-pro
- **Files**: .claude/skills/LinkedInPoster.SKILL.md
- **Dependencies**: Bronze Tier completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Confirm skill file exists and follows schema
  - Verify skill declares all required fields
  - Check that approval_required is set to true (required for posting)

### Task 1.5: Set up Playwright for LinkedIn automation
- **Description**: Install and configure Playwright for LinkedIn interactions
- **Files**: requirements-playwright.txt, playwright setup code
- **Dependencies**: Task 1.4 completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Confirm Playwright can launch browser successfully
  - Verify it can navigate to LinkedIn login
  - Test session persistence across runs

### Task 1.6: Test LinkedIn draft creation functionality
- **Description**: Implement and test LinkedIn post draft creation with proper approval workflow
- **Files**: .claude/skills/linkedin_poster_impl.py
- **Dependencies**: Tasks 1.4 and 1.5 completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Verify LinkedIn post drafts can be created
  - Confirm draft files go to Pending_Approval/ with proper format
  - Test compliance with LinkedIn terms of service
  - Validate human-readable content in draft files

## Phase 2: MCP Server Development

### Task 2.1: Create Email MCP server using Node.js
- **Description**: Set up the foundation for the Email MCP server
- **Files**: mcp/email-mcp/package.json, mcp/email-mcp/index.js
- **Dependencies**: Node.js installed, Bronze Tier completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Verify MCP server can start and register with Claude Code
  - Confirm it follows MCP protocol specifications
  - Test basic connectivity from Claude Code

### Task 2.2: Implement send_email capability with Gmail API
- **Description**: Add the core email sending functionality to the MCP server
- **Files**: mcp/email-mcp/tools/send_email.js
- **Dependencies**: Task 2.1 completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Test sending a sample email via the tool
  - Verify Gmail API integration works correctly
  - Confirm authentication works with credentials
  - Test error handling for failed sends

### Task 2.3: Set up MCP server authentication via hooks
- **Description**: Configure the MCP server to receive credentials securely via hooks
- **Files**: mcp/email-mcp/auth.js, hook integration
- **Dependencies**: Task 2.2 completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Verify credentials are injected at runtime, not stored
  - Confirm server can authenticate with Gmail API using injected credentials
  - Test that no credentials are visible in process memory/logs
  - Validate security of credential injection process

### Task 2.4: Test MCP server connection from Claude Code
- **Description**: Verify Claude Code can properly interact with the new MCP server
- **Files**: Claude Code configuration for MCP
- **Dependencies**: Tasks 2.1, 2.2, 2.3 completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Confirm Claude can discover MCP tools
  - Test calling send_email tool from Claude
  - Verify proper error handling in Claude responses
  - Validate response format matches expectations

### Task 2.5: Create EmailMCP.SKILL.md
- **Description**: Generate the skill that enables Claude to use the Email MCP server
- **Files**: .claude/skills/EmailMCP.SKILL.md
- **Dependencies**: Tasks 2.1-2.4 completed
- **Priority**: High
- **Effort**: Low
- **Test**:
  - Confirm skill exists and references MCP server correctly
  - Verify skill properly describes the MCP capabilities
  - Test that Claude recognizes and can use the skill

## Phase 3: Approval Workflow Implementation

### Task 3.1: Create HITLApproval.SKILL.md
- **Description**: Generate the Human-in-the-Loop Approval skill using skills-create-pro
- **Files**: .claude/skills/HITLApproval.SKILL.md
- **Dependencies**: Bronze Tier completed
- **Priority**: High
- **Effort**: Low
- **Test**:
  - Confirm skill file follows required schema
  - Verify approval_required is set appropriately
  - Check that skill describes directory monitoring capabilities

### Task 3.2: Implement file monitoring for approval directories
- **Description**: Create the monitoring functionality for approval workflows
- **Files**: .claude/skills/approval_monitor.py
- **Dependencies**: Task 3.1 completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Verify monitoring detects file movement between approval directories
  - Test that monitored files trigger appropriate actions
  - Confirm no files are missed during monitoring
  - Validate handling of concurrent file operations

### Task 3.3: Test approval workflow with sample tasks
- **Description**: End-to-end testing of the approval workflow using sample sensitive actions
- **Files**: Test files that require approval
- **Dependencies**: Tasks 3.1 and 3.2 completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Create approval request file in Pending_Approval/
  - Move file to Approved/ and verify action executes
  - Move file to Rejected/ and verify action is cancelled
  - Test timeout handling for unprocessed requests

### Task 3.4: Set up approval timeout mechanisms
- **Description**: Implement automatic handling of approval requests that exceed time limits
- **Files**: Approval timeout logic in monitoring code
- **Dependencies**: Task 3.3 completed
- **Priority**: Medium
- **Effort**: Low
- **Test**:
  - Create approval request that exceeds timeout
  - Verify system handles timeout appropriately
  - Confirm timeout behavior is logged correctly
  - Test that timed-out requests don't block the system

### Task 3.5: Create approval logging functionality
- **Description**: Implement comprehensive logging for all approval decisions
- **Files**: Approval logging in /Logs/ and Dashboard.md
- **Dependencies**: Task 3.4 completed
- **Priority**: Medium
- **Effort**: Low
- **Test**:
  - Verify all approval decisions are logged with proper details
  - Confirm logs follow the required format with timestamps
  - Test that Dashboard.md reflects approval status where appropriate

## Phase 4: Plan Creation System

### Task 4.1: Create PlanCreator.SKILL.md
- **Description**: Generate the Plan Creation skill using skills-create-pro
- **Files**: .claude/skills/PlanCreator.SKILL.md
- **Dependencies**: Bronze Tier completed
- **Priority**: High
- **Effort**: Low
- **Test**:
  - Confirm skill file exists and follows schema
  - Verify skill declares proper inputs/outputs for plan creation
  - Check that skill describes plan template functionality

### Task 4.2: Implement Plan.md template system
- **Description**: Create the templates and logic for generating Plan.md files
- **Files**: Plan templates in /Plans/ system
- **Dependencies**: Task 4.1 completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Verify plan templates can generate proper Plan.md files
  - Test that plans include proper YAML frontmatter
  - Confirm plans have actionable steps with checkboxes
  - Validate that plans link back to original tasks

### Task 4.3: Test plan creation for multi-step tasks
- **Description**: End-to-end testing of plan creation with complex, multi-step tasks
- **Files**: Sample multi-step tasks, resulting Plan.md files
- **Dependencies**: Task 4.2 completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Create sample complex task that needs planning
  - Verify Claude generates appropriate plan
  - Test that generated plans are actionable and complete
  - Confirm plans include proper tracking mechanisms

### Task 4.4: Integrate plan checking with Claude workflows
- **Description**: Ensure Claude properly follows and updates plan steps
- **Files**: Claude workflows that interact with plans
- **Dependencies**: Task 4.3 completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Run Claude on a task with an existing plan
  - Verify Claude checks off completed steps
  - Test that Claude progresses through plan steps sequentially
  - Confirm plan status is updated in real-time

### Task 4.5: Set up plan status tracking
- **Description**: Implement tracking of plan completion and progress
- **Files**: Plan status tracking in Dashboard.md and logs
- **Dependencies**: Task 4.4 completed
- **Priority**: Medium
- **Effort**: Low
- **Test**:
  - Verify Dashboard.md shows plan progress
  - Confirm logs capture plan execution events
  - Test that completed plans are properly moved to /Done/
  - Validate that abandoned plans are handled appropriately

## Phase 5: Scheduling System

### Task 5.1: Create SchedulerCron.SKILL.md
- **Description**: Generate the Scheduling skill using skills-create-pro
- **Files**: .claude/skills/SchedulerCron.SKILL.md
- **Dependencies**: Bronze Tier completed
- **Priority**: High
- **Effort**: Low
- **Test**:
  - Confirm skill exists and describes scheduling capabilities
  - Verify skill declares proper inputs for scheduling tasks
  - Check that skill includes timezone handling if needed

### Task 5.2: Implement Python-based scheduling system
- **Description**: Create the core scheduling functionality using Python
- **Files**: .claude/skills/scheduler_impl.py
- **Dependencies**: Task 5.1 completed
- **Priority**: High
- **Effort**: High
- **Test**:
  - Verify scheduler can register and track scheduled tasks
  - Test that scheduled tasks execute at correct times
  - Confirm scheduler handles recurring tasks properly
  - Validate error handling for failed scheduled tasks

### Task 5.3: Test scheduled task execution
- **Description**: Test the complete scheduling workflow with sample tasks
- **Files**: Scheduled task definitions and execution logs
- **Dependencies**: Task 5.2 completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Schedule a simple task to run in the future
  - Verify task executes at the scheduled time
  - Test that task execution is properly logged
  - Confirm scheduler can be managed during operation

### Task 5.4: Set up recurring task management
- **Description**: Implement support for recurring scheduled tasks
- **Files**: Recurring task configuration and management
- **Dependencies**: Task 5.3 completed
- **Priority**: Medium
- **Effort**: Medium
- **Test**:
  - Schedule a task to repeat daily/weekly
  - Verify task executes on the correct schedule
  - Test cancellation of recurring tasks
  - Confirm recurring tasks don't interfere with system performance

### Task 5.5: Integrate with existing vault workflows
- **Description**: Ensure scheduling system works with existing vault directory structure
- **Files**: Integration with /Inbox/, /Needs_Action/, etc.
- **Dependencies**: Task 5.4 completed
- **Priority**: Medium
- **Effort**: Low
- **Test**:
  - Verify scheduled tasks can trigger existing workflows
  - Test that scheduled tasks follow the same routing as manual tasks
  - Confirm scheduling system respects existing approval workflows
  - Validate that scheduled actions are properly logged

## Phase 6: Integration and Testing

### Task 6.1: Test full workflow: Gmail → Plan → Approval → Action → Log
- **Description**: End-to-end testing of complete workflow from Gmail detection to final logging
- **Files**: Complete workflow from /Inbox/ to /Done/ with all intermediate steps
- **Dependencies**: All previous tasks completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Trigger Gmail event and verify complete workflow
  - Confirm each step properly transitions to the next
  - Validate that all intermediate files are properly created and moved
  - Test that final logging captures the complete workflow

### Task 6.2: Test LinkedIn posting workflow with approval
- **Description**: End-to-end testing of LinkedIn posting from draft creation through approval to posting
- **Files**: LinkedIn draft in Pending_Approval/, approval, and posting log
- **Dependencies**: All previous tasks completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Create LinkedIn draft via workflow
  - Process through approval system
  - Verify post execution (in test environment)
  - Confirm all steps are properly logged

### Task 6.3: Verify all Agent Skills work properly
- **Description**: Comprehensive testing of all new Agent Skills created in Silver Tier
- **Files**: All new .claude/skills/*.SKILL.md files and their implementations
- **Dependencies**: All previous tasks completed
- **Priority**: Critical
- **Effort**: High
- **Test**:
  - Verify each skill follows proper specification
  - Test that Claude can successfully use each skill
  - Confirm all skills integrate properly with existing system
  - Validate that skills follow constitution requirements

### Task 6.4: Test error handling and recovery
- **Description**: Test system resilience under various error conditions
- **Files**: Error logs, recovery actions
- **Dependencies**: All previous tasks completed
- **Priority**: High
- **Effort**: Medium
- **Test**:
  - Simulate Gmail API errors and verify recovery
  - Test MCP server failure and recovery
  - Verify approval system handles errors gracefully
  - Confirm scheduler handles failed tasks appropriately

### Task 6.5: Update Dashboard.md with new metrics
- **Description**: Enhance Dashboard.md to show Silver Tier features and metrics
- **Files**: AI_Employee_Vault/Dashboard.md
- **Dependencies**: All other Silver Tier functionality completed
- **Priority**: Medium
- **Effort**: Low
- **Test**:
  - Verify Dashboard shows new Silver Tier metrics
  - Confirm approval queue status is visible
  - Test that scheduled tasks are reflected in dashboard
  - Validate that new watcher statuses are displayed

### Task 6.6: Validate all constitution requirements
- **Description**: Final validation that all Silver Tier implementation follows constitution rules
- **Files**: All Silver Tier implementation files
- **Dependencies**: All previous tasks completed
- **Priority**: Critical
- **Effort**: Medium
- **Test**:
  - Confirm no .env files are created or accessed anywhere
  - Verify all credentials flow through hooks only
  - Check that all new functionality is implemented as Agent Skills
  - Validate that no inline scripting was used, only proper skills

## Task Dependencies Summary
- Phase 1 tasks run with some parallelization (Gmail/LinkedIn watchers can be developed in parallel)
- Phase 2 depends on Node.js and MCP setup
- Phase 3 can run in parallel with Phase 2 after skill creation
- Phase 4 can run in parallel with Phase 2/3
- Phase 5 can run in parallel with other phases after skill creation
- Phase 6 requires all other phases completed

## Success Criteria for Each Phase
Phase 1: Both Gmail and LinkedIn watchers functional with proper skill files
Phase 2: MCP server operational and integrated with Claude Code
Phase 3: Complete approval workflow functional with logging
Phase 4: Plan creation and tracking working end-to-end
Phase 5: Scheduling system operational and integrated
Phase 6: Complete system validated and compliant with constitution