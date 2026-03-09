# Implementation Plan: Bronze Tier - Personal AI Employee

## 1. Scope and Dependencies

### In Scope
- Create vault directory structure (Inbox, Needs_Action, Done, Logs)
- Generate required skill files using `skills-create-pro`:
  - GmailWatcher or FileSystemWatcher skill
  - InboxRouter skill
  - TaskCompleter skill
  - Logging skill
- Implement vault read/write verification process
- Create dashboard file and update mechanism
- Set up audit logging system

### Out of Scope
- Silver/Gold tier features
- External API integrations beyond Gmail/filesystem
- Complex business logic beyond basic routing
- Advanced UI components beyond markdown files

### External Dependencies
- Claude Code environment with access to project
- Working `skills-create-pro` command
- `.claude/hook/` directory for credential injection
- OS keychain for credential storage (for Gmail)

## 2. Key Decisions and Rationale

### Decision 1: File System Structure
- **Options Considered**: Using existing vault structure vs creating new
- **Trade-offs**: Existing structure maintains consistency; new would allow more control
- **Rationale**: Use the existing AI_Employee_Vault structure as specified in constitution

### Decision 2: Watcher Selection
- **Options Considered**: GmailWatcher vs FileSystemWatcher
- **Trade-offs**: Gmail requires OAuth setup; FileSystem is simpler but less powerful
- **Rationale**: Start with FileSystemWatcher as it's simpler to implement and test

### Decision 3: Skill Creation Approach
- **Options Considered**: Manual skill files vs using `skills-create-pro`
- **Trade-offs**: Manual gives full control; automated ensures compliance with standards
- **Rationale**: Use `skills-create-pro` as required by constitution

## 3. Implementation Architecture

### 3.1 Directory Structure
```
AI_Employee_Vault/
├── Inbox/                    # Raw captured items
├── Needs_Action/            # Claude processes these
├── Done/                    # Completed tasks
├── Logs/                    # Audit trail files (YYYY-MM-DD.md)
├── Dashboard.md             # Live status surface
└── Company_Handbook.md      # Human-authored rules
└── Business_Goals.md        # Human-authored priorities
```

### 3.2 Skill Architecture

#### Skill 1: FileSystemWatcher.SKILL.md
- **Implementation**: Monitors a designated drop folder for new files
- **Technology**: File system polling or inotify
- **Credentials**: Path configured via hook injection
- **Output**: Creates metadata files in `/Inbox/FILE_{name}.md`

#### Skill 2: InboxRouter.SKILL.md
- **Implementation**: Monitors `/Inbox/` for new files and moves to `/Needs_Action/`
- **Technology**: File system monitoring, YAML parsing
- **Output**: Updates dashboard counters

#### Skill 3: TaskCompleter.SKILL.md
- **Implementation**: Moves files from `/Needs_Action/` to `/Done/` after processing
- **Technology**: File operations, logging
- **Output**: Audit log entries and dashboard updates

#### Skill 4: AuditLogger.SKILL.md
- **Implementation**: Maintains append-only log files
- **Technology**: File I/O operations with append mode
- **Output**: Daily log files in `/Logs/` directory

## 4. Implementation Tasks

### Phase 1: Foundation Setup
1. Verify vault directory structure exists
2. Create missing directories if needed
3. Create initial Dashboard.md file
4. Verify Claude Code read/write access

### Phase 2: Skill Creation
5. Generate FileSystemWatcher.SKILL.md using `skills-create-pro`
6. Generate InboxRouter.SKILL.md using `skills-create-pro`
7. Generate TaskCompleter.SKILL.md using `skills-create-pro`
8. Generate AuditLogger.SKILL.md using `skills-create-pro`

### Phase 3: Hook Setup
9. Create filesystem_watch.hook template for path injection
10. Document hook usage in README

### Phase 4: Verification and Testing
11. Execute system self-verification sequence
12. Test full routing flow: `/Inbox` → `/Needs_Action` → `/Done`
13. Verify logging works correctly
14. Check dashboard updates

### Phase 5: Documentation
15. Update project documentation
16. Verify all constitution requirements are met

## 5. Non-Functional Requirements and Constraints

### Performance Requirements
- File operations must complete within 5 seconds
- Dashboard updates must be near real-time
- System must handle files up to 10MB without performance degradation

### Security Requirements
- No direct access to `.env` files allowed
- All credentials must be injected via hooks
- Log files must be append-only
- No sensitive data in logs without user consent

### Reliability Requirements
- System must recover from temporary failures
- Log retention minimum 90 days
- All operations must be idempotent

## 6. Data Flow and Processing

### Data Flow Diagram
```
[External File Drop]
    ↓
[FileSystemWatcher] → [Inbox/FILE_{id}.md]
    ↓
[InboxRouter] → [Needs_Action/FILE_{id}.md] + [Dashboard Update]
    ↓
[Claude Processing]
    ↓
[TaskCompleter] → [Done/FILE_{id}.md] + [Log Entry] + [Dashboard Update]
```

### Error Handling
- If file copy fails during watch: log error, continue monitoring
- If routing fails: keep in `/Inbox/`, log error, retry after 30s
- If completion fails: log error, leave in `/Needs_Action/`
- If dashboard update fails: continue, log error

## 7. Operational Readiness

### Logging and Monitoring
- System actions logged to `/Logs/{YYYY-MM-DD}.md`
- Dashboard shows current system status
- Error alerts appear on dashboard

### Runbooks
- Basic troubleshooting: check directory permissions
- Log file management: automatic rotation
- Credential refresh: hook-based injection process

### Deployment Strategy
- Tier 1 (human) creates basic structure
- Agent auto-completes Tiers 2-4 via skill creation
- Rollback: remove generated skill files and revert dashboard

## 8. Risk Analysis and Mitigation

### Risk 1: File Permission Issues
- **Impact**: System cannot read/write to vault directories
- **Probability**: Medium (common on shared systems)
- **Mitigation**: Pre-flight checks during setup; clear error messages
- **Blast Radius**: System functionality blocked until resolved

### Risk 2: Credential Injection Failure
- **Impact**: Watcher cannot access monitored locations
- **Probability**: Low
- **Mitigation**: Clear hook configuration documentation
- **Blast Radius**: Single watcher functionality

### Risk 3: Log File Growth
- **Impact**: Disk space exhaustion over time
- **Probability**: Medium
- **Mitigation**: Automatic log rotation and retention policy
- **Blast Radius**: System performance degradation

## 9. Testing Strategy

### Unit Tests
- File operation functions
- Dashboard update logic
- Log entry formatting

### Integration Tests
- End-to-end file routing: `/Inbox` → `/Needs_Action` → `/Done`
- Dashboard counter accuracy
- Audit log formatting and writing

### System Tests
- Full verification sequence execution
- Concurrent file processing
- Error recovery scenarios

## 10. Success Criteria Verification

### Verification Steps
1. Confirm all vault directories exist
2. Verify all 4 skill files created successfully
3. Execute end-to-end test: create test file → watch → route → complete → log
4. Confirm dashboard updates correctly
5. Verify log entry format matches requirements
6. Check that constitution rules are followed (no .env access, hook injection)

### Acceptance Criteria
- [ ] All directories created as specified
- [ ] All skills created using `skills-create-pro`
- [ ] End-to-end flow completed successfully
- [ ] Audit logs follow specified format
- [ ] Dashboard updates in real-time
- [ ] No `.env` files accessed during process
- [ ] Credentials properly injected via hooks
- [ ] Bronze tier completion log entry generated

## 11. Implementation Timeline

| Phase | Duration | Deliverables |
|-------|----------|--------------|
| Foundation Setup | 1 hour | Directory structure, dashboard |
| Skill Creation | 2 hours | 4 skill files generated |
| Hook Setup | 30 minutes | Hook templates |
| Verification | 2 hours | End-to-end testing |
| Documentation | 1 hour | Updated docs |

**Total estimated time**: 6.5 hours