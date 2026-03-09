---
name: cloud_sync_agent
description: |
  Synchronizes data seamlessly between cloud and local systems, handles conflicts and merge strategies,
  encrypts data during synchronization, maintains sync status and history, resumes interrupted sync operations,
  and supports multiple cloud providers (Dropbox, Google Drive, OneDrive, etc.).
---

# Cloud Sync Agent

This skill should be used when synchronizing data between cloud and local systems for the Personal AI Employee system. It provides seamless synchronization with conflict resolution and security features.

## Purpose

Implements comprehensive cloud-local synchronization with the following capabilities:
- Synchronizes vault files between local and cloud storage
- Handles conflicts and merge strategies
- Encrypts data during synchronization
- Maintains sync status and history
- Resumes interrupted sync operations
- Supports multiple cloud providers

## Before Implementation

Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing vault structure, file handling patterns |
| **Conversation** | User's specific requirements for sync frequency, conflict resolution preferences |
| **Skill References** | Cloud API integration patterns, encryption standards |
| **User Guidelines** | Security policies, cloud provider preferences |

Ensure all required context is gathered before implementing.

## Functionality

The skill performs these key operations:

### Data Synchronization
- Syncs files between local vault and cloud storage
- Maintains file integrity during transfers
- Tracks file versions and changes
- Handles large file transfers efficiently

### Conflict Resolution
- Detects file conflicts during sync
- Implements configurable merge strategies
- Maintains conflict logs and resolution history
- Preserves file history during resolution

### Security Implementation
- Encrypts data during synchronization
- Uses secure authentication protocols
- Implements access control and permissions
- Logs security events and access attempts

### Sync Management
- Maintains sync status and progress tracking
- Resumes interrupted sync operations
- Handles connection failures gracefully
- Provides sync performance metrics

### Multi-Provider Support
- Supports multiple cloud platforms (Dropbox, Google Drive, OneDrive)
- Provides consistent interface across providers
- Handles provider-specific limitations
- Implements provider failover capabilities

## Data Sources Integration

### Cloud Providers
- Dropbox API integration
- Google Drive API integration
- Microsoft OneDrive API integration
- Additional cloud provider APIs as needed

### Local Sources
- All vault directories (Inbox, Needs_Action, Plans, etc.)
- Configuration files and settings
- Log files and metrics
- Report and briefings directories

## Output Format

The skill generates:
- Sync status reports to `/Platinum/Sync_Logs/`
- Conflict resolution logs to `/Platinum/Sync_Logs/`
- Security audit logs to `/Logs/`
- Performance metrics to `/Platinum/Health_Metrics/`

## Error Handling

- If cloud API unavailable: retries with exponential backoff
- If sync interrupted: resumes from last checkpoint
- If encryption fails: aborts sync operation safely
- If conflict resolution fails: escalates to manual resolution

## Configuration

The skill requires:
- Cloud provider API credentials
- Encryption key management
- Sync schedule configuration
- Conflict resolution strategy configuration