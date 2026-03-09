---
name: gold_tier_orchestrator
description: |
  Orchestrates the complete Gold Tier Personal AI Employee system including Ralph Wiggum loop,
  CEO briefing generation, comprehensive audit logging, error recovery, and graceful degradation.
  Coordinates all system components for unified operation.
---

# Gold Tier Orchestrator

This skill should be used when orchestrating the complete Gold Tier Personal AI Employee system. It coordinates all components including the Ralph Wiggum loop, CEO briefing generation, audit logging, and error recovery for unified system operation.

## Purpose

Orchestrates the complete Gold Tier system with these capabilities:
- Advanced Ralph Wiggum persistence loop for file-movement based processing
- Automated CEO briefing generation on Sundays
- Comprehensive audit logging for all actions
- Error recovery and graceful degradation
- Component monitoring and health checks
- Unified system operation

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing orchestrator patterns, component interfaces |
| **Conversation** | User's specific requirements for system coordination, scheduling needs |
| **Skill References** | System orchestration patterns, component integration best practices |
| **User Guidelines** | Project-specific orchestration requirements, monitoring policies |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### System Initialization
- Starts all watcher processes (Gmail, filesystem, LinkedIn)
- Initializes scheduler with CEO briefing timing
- Sets up audit logging system
- Configures error recovery mechanisms

### Ralph Wiggum Loop Coordination
- Monitors the complete file-based workflow
- Processes Inbox → Needs_Action → Plans → Approval → Execution → Logging → Dashboard → LOOP
- Handles human-in-the-loop approval processes
- Maintains system state consistency

### CEO Briefing Generation
- Schedules weekly briefing generation for Sunday 11:59 PM
- Coordinates data aggregation from multiple sources
- Generates comprehensive business briefings
- Saves to Briefings directory

### Audit Logging Management
- Logs all system actions in JSON format
- Maintains audit trail in /Logs/{YYYY-MM-DD}.md
- Tracks component health and status
- Records error conditions and recovery

### Error Recovery & Degradation
- Monitors component health
- Implements automatic recovery from failures
- Applies graceful degradation when components fail
- Maintains system stability

### Component Monitoring
- Checks health of all running services
- Restarts failed components
- Maintains service availability
- Updates dashboard with system status

## Data Sources Integration

### Core Components
- **Watchers**: Gmail, filesystem, LinkedIn, inbox processing
- **Scheduler**: Task scheduling and timing
- **MCP Servers**: External service integration
- **Skills**: All specialized capabilities
- **Vault**: File-based workflow coordination
- **Logs**: Audit trail and monitoring

### File Directories
- All standard vault directories (Inbox, Needs_Action, etc.)
- Briefings: CEO briefing storage
- Logs: Audit trail maintenance

## Output Format

The orchestrator maintains:
- Coordinated system operation across all components
- Regular CEO briefings in Briefings folder
- Comprehensive audit logs in Logs folder
- Updated dashboard with system status
- Healthy component operation with automatic recovery

## Error Handling

- If orchestrator fails: System components continue but lose coordination
- If scheduling fails: Briefings may not generate automatically
- If audit logging fails: System continues but loses audit trail
- If recovery mechanisms fail: Manual intervention required

## Configuration

The skill requires:
- Access to all vault directories
- Process management permissions for starting/stopping services
- Network access for MCP servers and external APIs
- File system permissions for all operations
- Proper credential injection via hooks