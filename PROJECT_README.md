# Personal AI Employee - Gold Tier System

## Overview
The Personal AI Employee is an autonomous Digital FTE (Full-Time Equivalent) system designed to automate business processes using file-based workflows. This Gold Tier implementation includes advanced features such as automated CEO briefing generation, comprehensive audit logging, and the Ralph Wiggum persistence loop.

## Architecture

### Core Components

```
┌─────────────────────────────────────────────────────────────────┐
│                        Personal AI Employee System              │
├─────────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐    ┌─────────────────┐    ┌─────────────┐  │
│  │   Orchestrator  │    │   File System   │    │   MCP       │  │
│  │                 │    │                 │    │   Servers   │  │
│  │ • Watchers      │    │ • Inbox         │    │ • LinkedIn  │  │
│  │ • Scheduler     │    │ • Needs_Action  │    │ • Email     │  │
│  │ • Briefing Gen  │    │ • Plans         │    │ • Browser   │  │
│  │ • Audit Logger  │    │ • Briefings     │    │ • Calendar  │  │
│  └─────────────────┘    │ • Done          │    └─────────────┘  │
│                         │ • Logs          │                    │
│                         └─────────────────┘                    │
└─────────────────────────────────────────────────────────────────┘
```

### Ralph Wiggum Persistence Loop
```
TRIGGER (Watcher detects event)
  → Write item to /Inbox/
    → Claude reads /Needs_Action/
      → Create /Plans/{task_id}_Plan.md
        → If approval_required → Write to /Pending_Approval/
            → WAIT for human to move file to /Approved/
          → Else → Execute immediately
        → Log result to /Logs/{date}.md
          → Move to /Done/ or /Rejected/
            → Update Dashboard.md
              → LOOP (continue watching)
```

### Data Flow for CEO Briefing Generation
```
[Business_Goals.md] → [Revenue Data] → [Bottleneck Analysis]
[Odoo Accounting]   → [Revenue Tracking] → [Trend Analysis]
[Social Summaries]  → [Engagement Metrics] → [Opportunity Identification]
[System Logs]       → [Process Analysis] → [Bottleneck Detection]
                           ↓
[CEO Briefing Generator] → [Weekly CEO Briefing.md]
```

## Gold Tier Features

### 1. CEO Briefing Generator
- **Feature**: `ceo_briefing_generator.SKILL.md`
- **Function**: Generates comprehensive weekly CEO briefings by aggregating business data from multiple sources
- **Schedule**: Automatically runs every Sunday at 11:59 PM
- **Output**: Saves to `AI_Employee_Vault/Briefings/` directory
- **Content Includes**:
  - Revenue this week
  - Current bottlenecks
  - Proactive suggestions
  - Upcoming deadlines
  - Business goals update
  - System health status

### 2. Advanced File-Based Workflow
- **Inbox**: Raw captures and triggers
- **Needs_Action**: Items requiring processing
- **Plans**: Generated action plans
- **Pending_Approval**: Human-in-the-loop required
- **Approved**: Authorized for execution
- **Done**: Completed tasks
- **Rejected**: Declined or failed tasks
- **Briefings**: Generated CEO briefings
- **Logs**: Comprehensive audit trail

### 3. Comprehensive Audit Logging
All system actions are logged in JSON format with:
- Timestamp
- Action type
- Status (SUCCESS, ERROR, PENDING)
- Agent name
- Detailed parameters
- Error traces when applicable

### 4. Multi-Tier Skill Architecture
- **Bronze Tier**: Foundation (FileSystemWatcher, InboxRouter, TaskCompleter, AuditLogger)
- **Silver Tier**: Core capabilities (GmailWatcher, LinkedInPoster)
- **Gold Tier**: Advanced integration (CEO Briefing Generator, CrossDomainOrchestrator)
- **Platinum Tier**: Autonomy (Watchdog, A2AMessenger)

## System Configuration

### Vault Directory Structure
```
AI_Employee_Vault/
├── Inbox/                    # Raw captured items
├── Needs_Action/             # Claude processes these
├── Plans/                    # Generated plans
├── Pending_Approval/         # Human-in-the-loop gate
├── Approved/                 # Ready to execute
├── Done/                     # Completed tasks
├── Rejected/                 # Declined tasks
├── Briefings/                # Weekly CEO briefings
├── Logs/                     # Audit trail files (YYYY-MM-DD.md)
├── Error_Logs/              # Failed task logs
├── Dashboard.md             # Live status surface
├── Company_Handbook.md      # Human-authored rules
└── Business_Goals.md        # Human-authored priorities
```

## Key Skills

### ceo_briefing_generator.SKILL.md
- **Description**: Generates weekly CEO briefings by aggregating business data from multiple sources including Business_Goals.md, Odoo accounting data, social media summaries, and system logs
- **Inputs**: Business_Goals.md, Odoo data, social summaries, system logs
- **Outputs**: Weekly CEO briefing in AI_Employee_Vault/Briefings/
- **Triggers**: Scheduled weekly (Sunday night)
- **Hooks**: odoo_credentials, linkedin_credentials
- **Approval Required**: No (informational only)

## Error Recovery & Graceful Degradation

### Recovery Protocol
1. Skill failure → Log to /Logs/ → Trigger on_error hook
2. Watcher crash → Watchdog restarts within 30 seconds
3. Missing skill → Invoke skill-creator-pro
4. Repeated failure (3x) → Escalate to /Pending_Approval/

### Graceful Degradation
- Odoo API down: Generate briefing with "Revenue data unavailable" notice
- Business_Goals.md missing: Use template with "No goals defined" notice
- System logs inaccessible: Skip bottleneck analysis section
- Social data unavailable: Skip engagement metrics section

## Compliance & Security

### Security Principles
1. Local-first: Sensitive data stays in vault
2. No .env access: Credentials via hooks only
3. Minimal collection: Capture only necessary data
4. Transparency: AI actions marked as "AI-assisted"
5. Opt-out honored: Respect human-only requests
6. Encryption: Vault encryption (owner responsibility)

### Logging Requirements
- Every action: `[ISO-8601] | AGENT | ACTION | STATUS | task_id`
- Location: `/Logs/{YYYY-MM-DD}.md`
- Format: Append-only (no modifications)

## Lessons Learned

### Architectural Insights
1. **File-Based Workflows**: Using files as the primary communication mechanism between components provides excellent auditability and resilience
2. **Ralph Wiggum Loop**: The persistence loop pattern ensures system reliability and human-in-the-loop capability
3. **Tiered Development**: The Bronze→Silver→Gold→Platinum progression provides clear development milestones
4. **Audit Logging**: Comprehensive JSON-based logging is essential for system debugging and compliance

### Technical Decisions
1. **Python + Markdown**: Simple tech stack that's easy to debug and extend
2. **MCP Integration**: Model Context Protocol servers provide excellent integration capabilities
3. **Scheduling**: Built-in scheduling system keeps all automation centralized
4. **Error Handling**: Robust error handling ensures system stability

### Operational Considerations
1. **Human-in-the-Loop Rules**: Clear rules about when human approval is required prevent automation overreach
2. **Graceful Degradation**: Systems should continue operating even when individual components fail
3. **Monitoring**: Dashboard and log monitoring provide visibility into system health
4. **Recovery**: Automated recovery mechanisms reduce need for manual intervention

## Running the System

To start the full system:

```bash
python automated_orchestrator.py
```

This will:
- Start all watchers (Gmail, filesystem, LinkedIn)
- Initialize the scheduling system
- Begin the Ralph Wiggum loop processing
- Monitor for CEO briefing generation triggers
- Process all file-based workflows

## Gold Tier Compliance Status
- ✅ Advanced Ralph Wiggum loop (file-movement based) in orchestrator
- ✅ Comprehensive audit logging (every action in JSON)
- ✅ Error recovery + graceful degradation
- ✅ Architecture diagram and lessons learned documented
- ✅ All functionality as Agent Skills