# Personal AI Employee - Digital FTE (Full-Time Equivalent)

## Overview
The Personal AI Employee is a sophisticated autonomous Digital FTE (Full-Time Equivalent) system that automates complex business processes through file-based workflows, MCP integrations, and AI-powered decision making. The system is built with a tiered architecture progressing from Bronze to Platinum capabilities.

## 🚀 Tiers Overview

### Bronze Tier - Foundation
- **FileSystemWatcher**: Monitors file system for task triggers
- **InboxRouter**: Routes items from `/Inbox/` to `/Needs_Action/`
- **TaskCompleter**: Moves completed tasks to `/Done/`
- **AuditLogger**: Maintains comprehensive audit trail
- **Basic File-Based Workflow**: Core system for task processing
- **Vault Structure**: Standard directories for task management

### Silver Tier - Core Capabilities
- **GmailWatcher**: Monitors Gmail for new messages and triggers
- **LinkedInPoster**: Automated LinkedIn content posting
- **EmailMCP**: Send emails via MCP server integration
- **WhatsAppWatcher**: Monitors WhatsApp for messages
- **Enhanced Workflow**: More sophisticated task routing and processing
- **Multi-Channel Integration**: Email, social, messaging platform support

### Gold Tier - Advanced Integration
- **CEO Briefing Generator**: Weekly automated business briefings
- **Advanced Ralph Wiggum Loop**: Sophisticated file-movement processing
- **Multi-Service MCP Integration**: Email, LinkedIn, Odoo, X/Twitter, Meta, WhatsApp
- **Comprehensive Audit Logging**: JSON-formatted system actions
- **Error Recovery & Graceful Degradation**: Auto-restart and reduced functionality
- **Master Orchestrator**: One-click system startup
- **Cross-Domain Coordination**: Multi-system integration capabilities

### Platinum Tier - Autonomy
- **Watchdog**: System health monitoring and maintenance
- **CloudSyncAgent**: Cloud-local synchronization
- **A2AMessenger**: Agent-to-agent communication
- **CEOBriefingGenerator**: Advanced business intelligence reporting
- **SchedulerCron**: Advanced time-based task scheduling
- **FinanceWatcher**: Financial transaction monitoring

## 📁 Vault Directory Structure
```
AI_Employee_Vault/
├── Inbox/                    # Raw captured items (Bronze+)
├── Needs_Action/             # Claude processes these (Bronze+)
├── Plans/                    # Generated action plans (Bronze+)
├── Pending_Approval/         # Human-in-the-loop gate (Bronze+)
├── Approved/                 # Ready to execute (Bronze+)
├── Done/                     # Completed tasks (Bronze+)
├── Rejected/                 # Declined tasks (Bronze+)
├── Briefings/                # Weekly CEO briefings (Gold+)
├── Error_Logs/              # Failed task logs (Bronze+)
├── Logs/                     # Audit trail files (YYYY-MM-DD.md) (Bronze+)
├── Dashboard.md             # Live status surface (Bronze+)
├── Company_Handbook.md      # Human-authored rules (Bronze+)
└── Business_Goals.md        # Human-authored priorities (Bronze+)
```

## ⚡ Quick Start (Gold Tier)

### Prerequisites
- Python 3.8+
- Required packages (see requirements/)
- Valid API credentials for all connected services

### Setup
1. Clone the repository
2. Install dependencies: `pip install -r requirements/requirements.txt`
3. Configure your `.env` file with all necessary credentials
4. Run the master orchestrator: `python automated_orchestrator.py`

### Running the System
```bash
# Start the complete autonomous system (Gold Tier)
python automated_orchestrator.py
```

The master orchestrator will:
- Load all credentials from `.env`
- Start all MCP servers (email, linkedin, odoo, x, meta, whatsapp, etc.)
- Start all watchers (gmail, filesystem, linkedin, whatsapp, etc.)
- Invoke Claude Code with Ralph Wiggum loop
- Run periodic scheduling (every 120s check /Needs_Action)
- Handle Plan.md creation, posting, Odoo sync, CEO briefing
- Use headless mode for browser-based MCPs
- Add watchdog to restart crashed processes
- Log everything to /Logs/orchestrator.log
- Handle graceful shutdown on Ctrl+C

## 🎯 Tier-Specific Functionality

### Bronze Tier - Foundation Features
- **File System Watcher**: Monitors specific directories for new files
- **Inbox Router**: Automatically routes new files to appropriate processing queues
- **Task Completion**: Moves processed files to completion directories
- **Audit Logging**: Basic logging of all system actions
- **Simple Workflow**: Basic file-based task processing

### Silver Tier - Core Capabilities
- **Gmail Integration**: Monitor and process Gmail messages automatically
- **LinkedIn Automation**: Automated posting and engagement
- **Email MCP**: Advanced email processing via Model Context Protocol
- **WhatsApp Monitoring**: Real-time messaging platform monitoring
- **Enhanced Routing**: More sophisticated task classification and routing

### Gold Tier - Advanced Integration
#### CEO Briefing Generator
- **Feature**: `ceo_briefing_generator.SKILL.md`
- **Function**: Generates weekly CEO briefings by aggregating business data from multiple sources
- **Schedule**: Automatically runs every Sunday at 11:59 PM
- **Output**: Saves to `AI_Employee_Vault/Briefings/` directory
- **Content Includes**:
  - Revenue this week
  - Current bottlenecks
  - Proactive suggestions
  - Upcoming deadlines
  - Business goals update
  - System health status

#### Ralph Wiggum Persistence Loop
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

#### MCP Server Integration
- **Email MCP Server** (Port 8000): Email monitoring and processing
- **LinkedIn MCP Server** (Port 8001): LinkedIn posting and monitoring
- **Odoo MCP Server** (Port 8002): Business management and accounting
- **WhatsApp MCP Server** (Port 8003): WhatsApp messaging automation
- **X/Twitter MCP Server** (Port 8004): Social media automation
- **Meta MCP Server** (Port 8005): Multi-platform social media
- **Browser Payment MCP** (Port 8006): Payment processing automation
- **Calendar MCP Server** (Port 8007): Calendar management

### Platinum Tier - Autonomous Capabilities
- **System Health Monitoring**: Continuous monitoring and maintenance
- **Cloud Synchronization**: Seamless cloud-local data sync
- **Agent-to-Agent Communication**: Advanced inter-agent communication
- **Advanced Scheduling**: Sophisticated time-based task management
- **Financial Monitoring**: Real-time financial transaction tracking

## 🛡️ Security & Compliance (All Tiers)

### Security Principles
1. **Local-first**: Sensitive data stays in vault
2. **No .env access**: Credentials via hooks only
3. **Minimal collection**: Capture only necessary data
4. **Transparency**: AI actions marked as "AI-assisted"
5. **Opt-out honored**: Respect human-only requests
6. **Encryption**: Vault encryption (owner responsibility)

### Human-in-the-Loop (HITL) Rules
| Action Type | HITL Required | Tiers |
|------------|--------------|--------|
| Send email / DM | ✅ Yes | Silver+ |
| Post to social media | ✅ Yes | Silver+ |
| Make payment / transfer | ✅ Yes | Gold+ |
| Update calendar | ✅ Yes | Gold+ |
| Access financial data | ✅ Yes | Platinum+ |
| Read & classify inbox | ❌ No | Bronze+ |
| Create Plan.md | ❌ No | Bronze+ |
| Write to /Logs/ | ❌ No | Bronze+ |
| Generate Dashboard.md | ❌ No | Bronze+ |

## 🔧 Error Recovery & Graceful Degradation (Gold+)

### Recovery Protocol
1. Skill failure → Log to /Logs/ → Trigger on_error hook
2. Watcher crash → Watchdog restarts within 30 seconds
3. Missing skill → Invoke skill-creator-pro
4. Repeated failure (3x) → Escalate to /Pending_Approval/

### Graceful Degradation (Gold+)
- Odoo API down: Generate briefing with "Revenue data unavailable" notice
- LinkedIn API unavailable: Skip engagement metrics in briefings
- Gmail API down: Queue emails locally for later processing
- System logs inaccessible: Continue with reduced logging capability

## 📊 Logging & Monitoring (Bronze+)

### Audit Trail
All system actions are logged in JSON format with:
- Timestamp
- Action type
- Status (SUCCESS, ERROR, PENDING)
- Agent identification
- Detailed parameters
- Error traces when applicable

### Dashboard Updates
- Real-time system status
- Task completion rates
- Error monitoring
- Performance metrics

## 🤖 Autonomous Operation (Platinum)

The Personal AI Employee operates autonomously 24/7 with capabilities that increase with each tier:
- **Bronze**: Basic file-based task processing
- **Silver**: Multi-channel integration and processing
- **Gold**: Advanced business intelligence and automated reporting
- **Platinum**: True autonomy with self-monitoring and cross-agent coordination

## 📚 Skill Framework (All Tiers)

All functionality is implemented as Agent Skills:

### Bronze Tier Skills
| Skill | Purpose | Tier |
|-------|---------|------|
| **FileSystemWatcher** | Monitors file system for new tasks | Bronze |
| **InboxRouter** | Routes tasks from Inbox to Needs_Action | Bronze |
| **TaskCompleter** | Moves completed tasks to Done folder | Bronze |
| **AuditLogger** | Maintains audit trail | Bronze |

### Silver Tier Skills
| Skill | Purpose | Tier |
|-------|---------|------|
| **GmailWatcher** | Monitors Gmail for new messages | Silver |
| **LinkedInPoster** | Creates and posts LinkedIn content | Silver |
| **EmailMCP** | Send emails via MCP server | Silver |
| **WhatsAppWatcher** | Monitor WhatsApp for messages | Silver |

### Gold Tier Skills
| Skill | Purpose | Tier |
|-------|---------|------|
| **ceo_briefing_generator** | Generates weekly CEO briefings | Gold |
| **ralph_wiggum_loop** | Implements file-movement based workflow | Gold |
| **comprehensive_audit_logger** | Provides JSON audit logging | Gold |
| **error_recovery_graceful_degradation** | Implements recovery strategies | Gold |
| **gold_tier_orchestrator** | Coordinates all system components | Gold |

### Platinum Tier Skills
| Skill | Purpose | Tier |
|-------|---------|--------|
| **Watchdog** | System health monitoring | Platinum |
| **CloudSyncAgent** | Cloud-local synchronization | Platinum |
| **A2AMessenger** | Agent-to-agent communication | Platinum |
| **CEOBriefingGenerator** | Advanced business reports | Platinum |

## 🎖️ Tier Progression

### Bronze Tier Achievement
- ✅ File-based workflow system
- ✅ Basic task processing
- ✅ Audit logging
- ✅ Vault structure

### Silver Tier Achievement
- ✅ Multi-channel integration
- ✅ Gmail monitoring
- ✅ LinkedIn automation
- ✅ Enhanced workflow

### Gold Tier Achievement
- ✅ Advanced Ralph Wiggum loop (file-movement based) in orchestrator
- ✅ Comprehensive audit logging (every action in JSON)
- ✅ Error recovery + graceful degradation
- ✅ Architecture diagram + lessons learned documentation
- ✅ All functionality as Agent Skills
- ✅ One-click start orchestrator
- ✅ CEO briefing generation system
- ✅ Multi-service MCP integrations

### Platinum Tier Achievement
- ✅ System autonomy
- ✅ Health monitoring
- ✅ Cloud synchronization
- ✅ Agent-to-agent communication

## 📞 Support

For issues and questions, please check the logs in `AI_Employee_Vault/Logs/` and the orchestrator log in `Logs/orchestrator.log`.

---

*Built with Claude Code for Panaversity Hackathon 0 - All Tiers Implemented*