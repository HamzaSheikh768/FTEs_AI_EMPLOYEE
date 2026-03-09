# Silver Tier MCP Servers Documentation

## Overview

The Silver Tier of the Personal AI Employee includes the following MCP servers for enhanced functionality:

### 1. **WhatsApp MCP Server** (`whatsapp_mcp_server.py`)
- **Port**: 8002
- **Purpose**: Send and monitor WhatsApp messages
- **Dependencies**: WhatsApp Web automation via Playwright

#### Available Tools:
- `send_whatsapp_message`: Send messages to contacts
- `search_whatsapp_contacts`: Search for contacts
- `check_whatsapp_unread`: Check for unread messages

#### Key Features:
- Human-in-the-loop approval for sensitive messages
- Automatic detection of urgent messages
- Integration with vault approval workflow
- Session persistence for WhatsApp Web

#### Usage Example:
```python
# Send a message
await whatsapp_mcp.send_whatsapp_message({
    "recipient": "John Doe",
    "message": "Hello! This is a test message from AI Employee."
})
```

### 2. **Browser/Payment MCP Server** (`browser_payment_mcp_server.py`)
- **Port**: 8003
- **Purpose**: Automate browser interactions and payment portals
- **Dependencies**: Playwright for browser automation

#### Available Tools:
- `browser_action`: Perform browser automation
- `prepare_payment`: Prepare payment for approval
- `fill_form`: Fill and submit web forms

#### Key Features:
- Draft-only payment preparation (requires approval)
- Support for complex form filling
- Sensitive URL detection and approval
- Screenshot capabilities for verification

#### Usage Example:
```python
# Prepare a payment
await browser_mcp.prepare_payment({
    "portal_url": "https://bank.example.com/transfer",
    "amount": 100.00,
    "recipient": "Vendor Name",
    "reference": "INV-2024-001"
})
```

### 3. **Calendar MCP Server** (`calendar_mcp_server.py`)
- **Port**: 8004
- **Purpose**: Manage calendar events and scheduling
- **Dependencies**: Local JSON storage for events

#### Available Tools:
- `create_calendar_event`: Create new events
- `query_calendar_events`: Query events by date range
- `update_calendar_event`: Update existing events
- `delete_calendar_event`: Delete events

#### Key Features:
- Approval workflow for events with attendees
- Daily schedule generation
- Reminder management
- Integration with vault logging

#### Usage Example:
```python
# Create a meeting
await calendar_mcp.create_calendar_event({
    "title": "Team Meeting",
    "start_time": "2024-02-28T10:00:00",
    "end_time": "2024-02-28T11:00:00",
    "attendees": ["team@example.com"],
    "location": "Conference Room A"
})
```

### 4. **Email MCP Server** (`email_watcher_server.py`) - Already Created
- **Port**: 8000
- **Purpose**: Email monitoring and management
- **Status**: ✅ Implemented

### 5. **LinkedIn Poster MCP Server** (`linkedin_poster_server.py`) - Already Created
- **Port**: 8001
- **Purpose**: LinkedIn posting automation
- **Status**: ✅ Implemented

## Installation and Setup

### Prerequisites
```bash
# Install MCP server dependencies
pip install -r mcp_servers/requirements.txt

# Install Playwright browsers
playwright install
```

### Environment Variables
Create `.env` file in project root:
```env
# WhatsApp settings
WHATSAPP_DRY_RUN=false

# Browser automation settings
BROWSER_DRY_RUN=false

# Calendar settings
CALENDAR_DRY_RUN=false

# General settings
VAULT_PATH=AI_Employee_Vault
```

### Running the Servers

#### Individual Servers:
```bash
# WhatsApp MCP Server
python mcp_servers/whatsapp_mcp_server.py

# Browser/Payment MCP Server
python mcp_servers/browser_payment_mcp_server.py

# Calendar MCP Server
python mcp_servers/calendar_mcp_server.py
```

#### All Servers (using orchestrator):
The orchestrator automatically starts all MCP servers when launched.

## Security Features

### Human-in-the-Loop (HITL)
All sensitive operations require approval:
- WhatsApp messages with payment/legal keywords
- All payment preparations
- Calendar events with external attendees
- Access to sensitive URLs (banking, admin, etc.)

### Approval Workflow
1. System creates approval file in `/Pending_Approval/`
2. Human reviews and moves to `/Approved/` or `/Rejected/`
3. System executes only approved actions
4. All actions logged to `/Logs/`

### Dry Run Mode
Set environment variable or use `--dry-run` flag to test without execution:
```bash
DRY_RUN=true python mcp_servers/whatsapp_mcp_server.py
```

## Integration with Vault System

### Directory Structure
```
AI_Employee_Vault/
├── Pending_Approval/    # Approval requests
├── Approved/           # Approved actions
├── Rejected/           # Rejected actions
├── Logs/               # Action logs
├── Calendar/           # Calendar events
└── Inbox/              # Incoming messages
```

### Logging Format
```
[YYYY-MM-DDTHH:MM:SS] | MCP_SERVER_NAME | ACTION | DETAILS
```

## Testing the MCP Servers

### WhatsApp Testing
```bash
# Test WhatsApp functionality
python watcher/whatsapp_watcher_impl.py --check-messages
python watcher/whatsapp_watcher_impl.py --send-message "Test message" --recipient "Test Contact"
```

### Browser Automation Testing
```bash
# Test browser automation
python watcher/browser_automation_impl.py --url "https://example.com"
```

### Calendar Testing
```bash
# Test calendar functionality
python watcher/calendar_impl.py --create-event
python watcher/calendar_impl.py --today
```

## API Reference

### WhatsApp MCP API
```json
{
  "tool": "send_whatsapp_message",
  "arguments": {
    "recipient": "Contact Name or Phone",
    "message": "Message content",
    "attachment_path": "/path/to/file.pdf"
  }
}
```

### Browser/Payment MCP API
```json
{
  "tool": "browser_action",
  "arguments": {
    "url": "https://example.com/form",
    "actions": [
      {
        "type": "fill",
        "selector": "#username",
        "value": "user123"
      },
      {
        "type": "click",
        "selector": "#submit"
      }
    ],
    "screenshot_path": "/path/to/screenshot.png"
  }
}
```

### Calendar MCP API
```json
{
  "tool": "create_calendar_event",
  "arguments": {
    "title": "Meeting Title",
    "start_time": "2024-02-28T10:00:00",
    "end_time": "2024-02-28T11:00:00",
    "description": "Meeting description",
    "attendees": ["email@example.com"],
    "location": "Conference Room",
    "reminder_minutes": 15
  }
}
```

## Troubleshooting

### Common Issues
1. **WhatsApp Login Fails**: Check WhatsApp Web accessibility, may need to scan QR code manually
2. **Browser Automation Fails**: Ensure Playwright browsers are installed
3. **Calendar Events Not Saving**: Check vault directory permissions
4. **MCP Server Won't Start**: Check port availability and dependencies

### Debug Mode
Enable verbose logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Next Steps

### Gold Tier Additions
- Odoo Accounting MCP Server
- Facebook/Instagram MCP Servers
- Twitter (X) MCP Server

### Platinum Tier Additions
- Cloud Sync MCP Server
- A2A Communication MCP Server

## Support
For issues and questions:
1. Check `/Logs/` for error messages
2. Review approval files in `/Pending_Approval/`
3. Verify environment variables
4. Check MCP server status in orchestrator logs