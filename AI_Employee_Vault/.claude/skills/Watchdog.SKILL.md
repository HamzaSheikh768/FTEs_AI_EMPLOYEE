---
name: watchdog
description: |
  Continuously monitors system health and performance, tracks system resource usage,
  monitors task completion rates and error rates, generates health reports and alerts,
  automatically restarts failed services, and logs health metrics to system logs.
---

# Watchdog

This skill should be used when monitoring system health and performance for the Personal AI Employee system. It provides continuous monitoring, automatic recovery, and health reporting capabilities.

## Purpose

Implements comprehensive system health monitoring with the following capabilities:
- Monitors all running processes and services
- Tracks system resource usage (CPU, memory, disk)
- Monitors task completion rates and error rates
- Generates health reports and alerts
- Automatically restarts failed services
- Logs health metrics to system logs

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing monitoring patterns, process management utilities |
| **Conversation** | User's specific requirements for health metrics, alert thresholds |
| **Skill References** | System monitoring best practices, resource tracking techniques |
| **User Guidelines** | Project-specific monitoring policies, security requirements |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### System Process Monitoring
- Tracks all running services and processes
- Monitors process health and responsiveness
- Detects hanging or unresponsive processes
- Records process start/stop events

### Resource Usage Tracking
- Monitors CPU usage across all processes
- Tracks memory consumption and leaks
- Checks disk space and I/O performance
- Monitors network connectivity and throughput

### Task Performance Monitoring
- Tracks task completion rates and success/failure ratios
- Monitors error rates and patterns
- Identifies performance bottlenecks
- Records task execution times and efficiency metrics

### Alert Generation
- Generates alerts based on configurable thresholds
- Sends notifications for critical system issues
- Logs warning and error conditions
- Provides detailed diagnostic information

### Automatic Recovery
- Automatically restarts failed services
- Recovers from common system errors
- Implements graceful degradation strategies
- Maintains system stability during failures

## Data Sources Integration

### Monitoring Inputs
- Running process list and status
- System resource metrics (CPU, memory, disk, network)
- Task execution logs and performance data
- Error logs and exception reports

### Output Locations
- `/Platinum/Health_Metrics/` - Health metrics and reports
- `/Logs/` - System audit logs
- System notifications and alerts

## Output Format

The skill generates:
- Health metrics in JSON format to `/Platinum/Health_Metrics/`
- Performance reports to `/Platinum/Health_Metrics/`
- System alerts to notification channels
- Process restart logs to `/Logs/`

## Error Handling

- If monitoring fails: logs error and attempts to restart monitoring service
- If automatic recovery fails: escalates to human operator
- If alert system fails: logs to backup notification channel
- If resource metrics unavailable: continues with available metrics

## Configuration

The skill requires:
- Access to system process information
- Permission to restart services
- Configuration for alert thresholds
- Notification channel setup