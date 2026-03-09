---
name: odoo-accounting
description: |
  Creates invoices, manages partners, and handles accounting operations in Odoo ERP.
  This skill integrates with Odoo Online (ai-employee-business1.odoo.com) via JSON-RPC.
  Use this skill when you need to create invoices from email/WhatsApp data, manage customers,
  track payments, or get financial reports from Odoo.
allowed-tools: Bash, Read, Write, Glob, Grep
model: claude-sonnet-4-6
---

# Odoo Accounting Skill

## Purpose
Creates invoices from email/WhatsApp data and manages accounting operations in Odoo ERP via MCP server.

## When to Use This Skill
- When an email or WhatsApp message contains invoice/billing information
- When a customer requests an invoice to be created
- When you need to search for existing invoices in Odoo
- When you need to get monthly revenue reports
- When you need to create or update partner (customer/vendor) information
- When you need to register payments against invoices

## Inputs
- **source_data**: Email or WhatsApp message content containing invoice details
- **partner_name**: Customer name (required if creating new partner)
- **partner_email**: Customer email (optional, for matching or creating partner)
- **items**: List of invoice line items with description, quantity, and price
- **invoice_type**: Type of invoice (out_invoice for customer, in_invoice for vendor)
- **invoice_date**: Invoice date in YYYY-MM-DD format (defaults to today)

## Outputs
- Creates invoice in Odoo and returns invoice number and ID
- Creates or updates partner if needed
- Logs all actions to `/Logs/odoo_accounting.log`
- Creates audit trail file in `/Done/INVOICE_{id}.md`

## Hook Dependencies
- `.claude/hook/odoo_credentials.hook` - Contains Odoo API credentials
- MCP Server: `odoo` - Registered in mcp.json

## Approval Required
No - Invoice creation is automated for Gold Tier

## DRY_RUN Support
Yes - Logs intent to create invoice but doesn't call Odoo API

## Implementation

### Before Implementation
Gather context to ensure successful implementation:

| Source | Gather |
|--------|--------|
| **Codebase** | Existing Odoo MCP tools, invoice formats, vault structure |
| **Conversation** | Email/WhatsApp content with invoice details |
| **Skill References** | Odoo API documentation, invoice creation patterns |
| **User Guidelines** | Project-specific invoicing rules, pricing |

Ensure all required context is gathered before implementing.

### Workflow
```
1. Receive email/WhatsApp message with billing information
2. Parse message to extract:
   - Customer name and email
   - Invoice items (description, quantity, price)
   - Any special notes or terms
3. Search for existing partner by email/name
4. If partner not found, create new partner
5. Create invoice in Odoo with extracted line items
6. Log invoice creation to system logs
7. Create audit trail file in /Done/
8. Return invoice number and status to user
```

### Invoice Data Schema
Extract from email/WhatsApp:

```yaml
partner_name: "Customer Company Name"
partner_email: "customer@example.com"
items:
  - name: "Web Development Services"
    quantity: 10
    price_unit: 5000.00
  - name: "Hosting Setup"
    quantity: 1
    price_unit: 2000.00
invoice_date: "2026-03-05"
notes: "Payment due within 30 days"
```

### Odoo Invoice Creation Payload
The skill calls the Odoo MCP tool with:

```python
{
    "partner_id": 123,  # Found or created partner ID
    "invoice_type": "out_invoice",
    "lines": [
        {
            "product_id": None,  # Optional
            "quantity": 10,
            "price_unit": 5000.00,
            "name": "Web Development Services"
        },
        {
            "product_id": None,
            "quantity": 1,
            "price_unit": 2000.00,
            "name": "Hosting Setup"
        }
    ],
    "invoice_date": "2026-03-05"
}
```

### Response Format
```json
{
    "invoice_id": 456,
    "invoice_number": "INV/2026/0001",
    "partner_id": 123,
    "partner_name": "Customer Company Name",
    "total_amount": 52000.00,
    "status": "created",
    "draft": true
}
```

### Error Handling
- If Odoo is unreachable: Log error, return error message, suggest retry
- If partner not found and can't create: Log error, ask for more information
- If invoice creation fails: Log error with details, suggest manual creation
- If email/WhatsApp parsing fails: Log error, ask for clarification

### Logging
All actions are logged to:
- Console: Real-time status updates
- File: `AI_Employee_Vault/Logs/odoo_mcp.log`
- Audit: `AI_Employee_Vault/Done/INVOICE_{id}.md`

### Example Usage

#### Example 1: Create Invoice from Email
```
Email Content:
"Hi, please send invoice for 10 hours of web development at $50/hour.
Thanks, John from ABC Corp (john@abccorp.com)"

Skill Action:
1. Parse email: Extract customer (John, ABC Corp, john@abccorp.com)
2. Extract items: 10 hours × $50 = $500
3. Search for partner by email
4. Create partner if not found
5. Create invoice with line item
6. Return: "Invoice INV/2026/0001 created for $500"
```

#### Example 2: Create Invoice from WhatsApp
```
WhatsApp Message:
"Need invoice for:
- Logo Design: $1000
- Business Cards: $500
Customer: XYZ Ltd"

Skill Action:
1. Parse WhatsApp: Extract customer (XYZ Ltd)
2. Extract items: Logo Design ($1000), Business Cards ($500)
3. Search for partner by name
4. Create invoice with 2 line items
5. Return: "Invoice INV/2026/0002 created for $1500"
```

### Security Considerations
- Never log full customer email addresses in plain text
- Mask sensitive financial data in logs
- Use Odoo API key for authentication (stored in .env)
- All invoice operations are logged for audit trail

### Integration Points
- **Gmail Watcher**: Triggers invoice creation from billing emails
- **WhatsApp Watcher**: Triggers invoice creation from WhatsApp messages
- **Orchestrator**: Coordinates invoice creation workflow
- **Audit Logger**: Maintains audit trail of all invoice operations
