---
name: scheduler_cron
description: |
  Handles complex time-based task scheduling with support for cron expressions, manages task dependencies,
  schedules tasks across multiple time zones, supports conditional scheduling based on system state,
  provides scheduling conflict detection and resolution, and enables dynamic scheduling adjustments.
---

# Advanced Scheduler (Cron)

This skill should be used when implementing complex time-based task scheduling for the Personal AI Employee system. It provides advanced scheduling capabilities with cron expressions and dependency management.

## Purpose

Implements sophisticated scheduling system with the following capabilities:
- Support for complex scheduling patterns using cron expressions
- Handle dependencies between scheduled tasks
- Schedule tasks across multiple time zones
- Support for conditional scheduling based on system state
- Provide scheduling conflict detection and resolution
- Enable dynamic scheduling adjustments

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing scheduling patterns, cron expression libraries |
| **Conversation** | User's specific requirements for scheduling complexity, time zone needs |
| **Skill References** | Cron scheduling best practices, dependency management patterns |
| **User Guidelines** | Scheduling policies, time zone requirements |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Cron Expression Support
- Parse and execute complex cron expressions
- Support for all standard cron patterns (seconds, minutes, hours, days, months, weekdays)
- Handle extended cron features (step values, ranges, multiple values)
- Validate cron expressions for correctness

### Task Dependency Management
- Define and manage dependencies between scheduled tasks
- Execute dependent tasks in correct order
- Handle failures in dependency chains
- Support for parallel execution of non-dependent tasks

### Multi-Timezone Scheduling
- Schedule tasks for different time zones
- Handle daylight saving time transitions
- Convert times between time zones
- Support for user-specific time zone preferences

### Conditional Scheduling
- Schedule tasks based on system state conditions
- Implement custom scheduling triggers
- Support for system load-based scheduling
- Handle resource availability constraints

### Conflict Detection and Resolution
- Detect scheduling conflicts between tasks
- Implement conflict resolution strategies
- Prevent resource overallocation
- Optimize scheduling for system resources

### Dynamic Scheduling
- Modify schedules during runtime
- Add/remove tasks without system restart
- Adjust scheduling parameters dynamically
- Support for user-initiated scheduling changes

## Data Sources Integration

### Schedule Configuration
- Task definitions with scheduling requirements
- Time zone configuration data
- System state and resource availability information
- Historical scheduling performance data

### Execution Context
- System clock for time-based triggers
- Resource availability monitors
- Task dependency graphs
- Error and performance logs

## Output Format

The skill generates:
- Scheduled task execution logs to `/Logs/`
- Schedule conflict reports to `/Logs/`
- Performance metrics to `/Platinum/Health_Metrics/`
- Task dependency graphs to `/Platinum/Advanced_Reports/`

## Error Handling

- If cron expression invalid: logs error and skips invalid task
- If dependency fails: handles according to dependency strategy (wait/retry/abort)
- If resource unavailable: delays task or uses alternative resources
- If conflict detected: resolves according to configured strategy

## Configuration

The skill requires:
- Cron expression parsing library
- Time zone database
- Task dependency tracking system
- Resource availability monitoring