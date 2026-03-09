---
name: a2a_messenger
description: |
  Facilitates communication between different agents in the system, coordinates complex multi-step processes,
  shares status and progress information, handles handoffs between different agents, supports message queuing
  and retries, and maintains communication logs.
---

# Agent-to-Agent Messenger

This skill should be used when enabling communication between different agents in the Personal AI Employee system. It provides messaging infrastructure for coordination and collaboration between agents.

## Purpose

Implements comprehensive agent-to-agent communication with the following capabilities:
- Send messages between different agents in the system
- Coordinate complex multi-step processes
- Share status and progress information
- Handle handoffs between different agents
- Support for message queuing and retries
- Maintain communication logs

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing MCP infrastructure, agent communication patterns |
| **Conversation** | User's specific requirements for message types, coordination protocols |
| **Skill References** | Message queue patterns, agent communication protocols |
| **User Guidelines** | Security policies, message format requirements |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Message Transmission
- Sends messages between different agents in the system
- Uses MCP infrastructure for reliable transmission
- Implements message queuing for offline agents
- Supports various message types and formats

### Process Coordination
- Coordinates complex multi-step processes across agents
- Manages dependencies between different agent tasks
- Synchronizes parallel agent activities
- Handles workflow state management

### Status Sharing
- Shares agent status and availability information
- Provides progress updates between collaborating agents
- Tracks task completion and success/failure status
- Maintains agent capability and load information

### Handoff Management
- Handles handoffs between different agents
- Manages task delegation and responsibility transfer
- Ensures smooth transitions during agent handoffs
- Maintains context and state during handoffs

### Message Reliability
- Implements retry mechanisms for failed messages
- Provides message delivery confirmation
- Handles message ordering and sequencing
- Ensures message integrity and authenticity

## Data Sources Integration

### Communication Channels
- MCP servers for message routing
- Message queues for reliable delivery
- Agent endpoints for direct communication
- Status monitoring systems for agent availability

### Message Content
- Task coordination messages
- Status update messages
- Error notification messages
- Handoff request and confirmation messages

## Output Format

The skill generates:
- Communication logs to `/Platinum/Agent_Communication/`
- Message delivery confirmations
- Agent status reports to `/Platinum/Health_Metrics/`
- Coordination workflow logs to `/Logs/`

## Error Handling

- If message delivery fails: queues message for retry with exponential backoff
- If agent unavailable: holds message until agent becomes available
- If MCP server down: uses alternative routing paths
- If authentication fails: logs security event and rejects message

## Configuration

The skill requires:
- MCP server configuration for message routing
- Message queue setup for reliability
- Agent identity and authentication system
- Communication protocol configuration