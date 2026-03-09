# Silver Tier Quick Start Guide

## 🚀 Getting Started with Silver Tier

### Prerequisites
- Python 3.8+
- Node.js 16+
- Git

### 1. Install Dependencies

```bash
# Install Python dependencies
pip install -r requirements-silver.txt
pip install -r requirements-google.txt
pip install -r requirements-playwright.txt

# Install Node.js dependencies
npm install

# Install Playwright browsers
playwright install
```

### 2. Configure Credentials

Create `.env` file (do NOT commit):
```env
# Gmail Configuration
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# LinkedIn Configuration
LINKEDIN_USERNAME=your_username
LINKEDIN_PASSWORD=your_password

# WhatsApp Configuration
WHATSAPP_DRY_RUN=true

# Browser/Payment Configuration
BROWSER_DRY_RUN=true

# Calendar Configuration
CALENDAR_DRY_RUN=true

# Vault Path
VAULT_PATH=AI_Employee_Vault
```

### 3. Start the System

```bash
# Start all MCP servers and orchestrator
python automated_orchestrator.py
```

### 4. Verify System Status

Check the dashboard:
```bash
cat AI_Employee_Vault/Dashboard.md
```

## 📋 Available Commands

### Using Skills
```bash
# Monitor file system
/filesystem-watcher

# Route inbox items
/inbox-router

# Complete tasks
/task-completer

# Monitor Gmail
/gmail-watcher

# Post to LinkedIn
/linkedin-poster
```

### MCP Server Operations
```bash
# Test Gmail MCP
python -c "from mcp_servers.gmail_mcp_server import EmailWatcherMCP; print('Gmail MCP OK')"

# Test LinkedIn MCP
python -c "from mcp_servers.linkedin_mcp_server import LinkedInPosterMCP; print('LinkedIn MCP OK')"

# Test WhatsApp MCP
python -c "from mcp_servers.whatsapp_mcp_server import WhatsAppMCP; print('WhatsApp MCP OK')"

# Test Browser/Payment MCP
python -c "from mcp_servers.browser_payment_mcp_server import BrowserPaymentMCP; print('Browser/Payment MCP OK')"

# Test Calendar MCP
python -c "from mcp_servers.calendar_mcp_server import CalendarMCP; print('Calendar MCP OK')"
```

## 🔧 Vault Workflow

### Human-in-the-Loop (HITL) Process
1. Actions requiring approval appear in `/Pending_Approval/`
2. Review the approval file
3. Move to `/Approved/` to execute OR `/Rejected/` to cancel
4. System automatically processes approved actions

### Directory Structure
```
AI_Employee_Vault/
├── Inbox/              # New items arrive here
├── Pending_Approval/   # Awaiting human approval
├── Approved/          # Approved actions
├── Rejected/          # Rejected actions
├── Done/              # Completed tasks
├── Logs/              # Daily logs
└── Dashboard.md       # System status
```

## 🛡️ Security Features

- All sensitive operations require approval
- Credentials injected via hooks (never in .env)
- Comprehensive audit logging
- Dry run mode for testing

## 📞 Support

1. Check `/Logs/` for error messages
2. Verify MCP server status in dashboard
3. Ensure all dependencies installed
4. Review approval workflow for pending items

## 🎯 Next Steps

1. Explore Gold Tier features
2. Customize workflows for your needs
3. Set up additional integrations
4. Configure automation schedules

---
*Silver Tier Personal AI Employee - Ready for Production*