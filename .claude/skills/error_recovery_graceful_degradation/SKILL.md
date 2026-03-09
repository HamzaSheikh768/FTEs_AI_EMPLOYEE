---
name: error_recovery_graceful_degradation
description: |
  Implements error recovery mechanisms and graceful degradation strategies for the Personal AI Employee system.
  Ensures system stability and continued operation even when individual components fail.
---

# Error Recovery and Graceful Degradation

This skill should be used when implementing error recovery mechanisms and graceful degradation strategies for the Personal AI Employee system. It ensures system stability and continued operation even when individual components fail.

## Purpose

Implements comprehensive error recovery and graceful degradation with the following features:
- Automatic system recovery from component failures
- Graceful degradation when services are unavailable
- Error logging and monitoring
- Component restart mechanisms
- Fallback strategies for unavailable services

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing error handling patterns, recovery mechanisms |
| **Conversation** | User's specific requirements for system resilience, acceptable degradation levels |
| **Skill References** | Error recovery best practices, graceful degradation patterns |
| **User Guidelines** | Project-specific reliability requirements, acceptable downtime |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Recovery Protocol
1. **Skill failure** → Log to /Logs/ → Trigger on_error hook
2. **Watcher crash** → Watchdog restarts within 30 seconds
3. **Missing skill** → Invoke skill-creator-pro
4. **Repeated failure (3x)** → Escalate to /Pending_Approval/

### Error Detection
- Monitors system components for failures
- Detects unresponsive services
- Identifies repeated error patterns
- Tracks component health status

### Recovery Actions
- Restarts failed components automatically
- Recreates missing services
- Reloads failed configurations
- Clears error states

### Graceful Degradation
- Maintains core functionality when non-critical components fail
- Provides fallback mechanisms for unavailable services
- Continues operation with reduced features rather than failing completely
- Preserves data integrity during degradation

## Data Sources Integration

### Recovery Monitoring
- System logs for error detection
- Process status for component monitoring
- Health check endpoints for service availability
- Error logs for pattern analysis

## Output Format

The skill maintains system stability and produces:
- Restored system components
- Continued service availability with graceful degradation
- Comprehensive error logs for analysis
- Preserved data integrity

## Error Handling Strategies

### For Different Components
- **Gmail API down**: Queue emails locally, process when available
- **LinkedIn API unavailable**: Skip social media metrics in briefings
- **Odoo API down**: Generate briefing with "Revenue data unavailable" notice
- **Business_Goals.md missing**: Use template with "No goals defined" notice
- **System logs inaccessible**: Skip bottleneck analysis section
- **Social data unavailable**: Skip engagement metrics section

### Component-Specific Recovery
- **Watcher crash**: Restart within 30 seconds
- **Scheduler failure**: Resume scheduling after restart
- **MCP server unavailable**: Retry connections with exponential backoff
- **File system errors**: Use temporary directories if needed

## Configuration

The skill requires:
- Access to system monitoring capabilities
- Process management permissions
- Log file access for error analysis
- Component restart capabilities
- Health check configuration