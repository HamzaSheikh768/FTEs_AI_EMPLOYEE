# Gold Tier: Odoo Community 19+ Setup Guide

**Project:** Panaversity Personal AI Employee  
**Tier:** Gold  
**Component:** Odoo Accounting & Business Integration  
**Date:** 2026-03-02

---

## Step 1: Install Odoo Community 19+ Using Docker

### Prerequisites

- Docker Desktop installed and running
- At least 4GB RAM available for Odoo
- Port 8069 available (Odoo default)
- Port 5432 available (PostgreSQL)

### Create Docker Compose File

Create a new directory for Odoo:

```bash
mkdir odoo-community
cd odoo-community
```

Create `docker-compose.yml`:

```yaml
version: '3.8'

services:
  odoo:
    image: odoo:19.0
    container_name: odoo-community-19
    depends_on:
      - postgres
    ports:
      - "8069:8069"
    environment:
      - ODOO_SERVER_WIDE_MODULES=web,base,account,project,sale,purchase,hr,crm
      - ODOO_DATABASE=ai_employee_business
      - ODOO_DB_PASSWORD=odoo_db_password_123
      - ODOO_ADMIN_PASSWORD=odoo_admin_password_456
      - HOST=postgres
      - PORT=5432
      - USER=odoo
      - PASSWORD=odoo_db_password_123
    volumes:
      - odoo-web-data:/var/lib/odoo
      - ./odoo-config:/etc/odoo
      - ./odoo-addons:/mnt/extra-addons
    restart: unless-stopped
    networks:
      - odoo-network

  postgres:
    image: postgres:15
    container_name: odoo-postgres-15
    environment:
      - POSTGRES_DB=postgres
      - POSTGRES_USER=odoo
      - POSTGRES_PASSWORD=odoo_db_password_123
    volumes:
      - odoo-db-data:/var/lib/postgresql/data
    restart: unless-stopped
    networks:
      - odoo-network

volumes:
  odoo-web-data:
  odoo-db-data:

networks:
  odoo-network:
    driver: bridge
```

### Create Directory Structure

```bash
mkdir odoo-config
mkdir odoo-addons
```

### Start Odoo

```bash
docker-compose up -d
```

**Wait 2-3 minutes** for Odoo to initialize (first startup is slow).

### Access Odoo

Open browser and navigate to:
```
http://localhost:8069
```

**Default Credentials:**
- **Database:** `ai_employee_business`
- **Email:** `admin`
- **Password:** `admin`

---

## Step 2: Create Database (Already configured in docker-compose)

The database `ai_employee_business` is automatically created on first run.

To verify:

```bash
docker exec -it odoo-postgres-15 psql -U odoo -c "\l"
```

You should see `ai_employee_business` in the list.

---

## Step 3: Create API Key for Admin User

### Method 1: Via Odoo UI (Recommended)

1. **Login to Odoo** at `http://localhost:8069`
   - Email: `admin`
   - Password: `admin`

2. **Enable Developer Mode:**
   - Go to Settings
   - Scroll to bottom
   - Click "Activate the developer mode"

3. **Create API Key:**
   - Go to Settings → Users & Companies → Users
   - Click on "Admin" user
   - Go to "User Preferences" tab
   - Click "New API Key"
   - Enter description: "AI Employee Integration"
   - Copy the generated API key

4. **Save to .env:**

Add these lines to your `.env` file:

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=ai_employee_business
ODOO_USERNAME=admin
ODOO_API_KEY=your_copied_api_key_here
ODOO_DB_PASSWORD=odoo_db_password_123
```

### Method 2: Via Command Line (Alternative)

```bash
# Generate API key using Odoo shell
docker exec -it odoo-community-19 odoo shell -d ai_employee_business

# In Python shell:
from odoo import http
env = http.root._db.cursor()
user = env['res.users'].search([('login', '=', 'admin')], limit=1)
api_key = env['res.api.key'].create({
    'name': 'AI Employee Integration',
    'user_id': user.id,
    'key': env['res.api.key']._generate_key()
})
print(f"API Key: {api_key.key}")
env.commit()
env.close()
```

---

## Step 4: Odoo MCP Server Skeleton

### Create MCP Server File

Create `mcp_servers/odoo_mcp.py`:

```python
#!/usr/bin/env python3
"""
Odoo MCP Server for Personal AI Employee - Gold Tier
Connects to Odoo Community 19+ via JSON-RPC for accounting and business operations
"""

import os
import sys
import json
import logging
import requests
from typing import Dict, Any, List, Optional
from pathlib import Path
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('AI_Employee_Vault/Logs/odoo_mcp.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class OdooClient:
    """Odoo JSON-RPC Client for API communication"""
    
    def __init__(
        self,
        url: str,
        database: str,
        username: str,
        api_key: str,
        db_password: str = None
    ):
        self.url = url.rstrip('/')
        self.database = database
        self.username = username
        self.api_key = api_key
        self.db_password = db_password
        self.uid = None
        self.session = requests.Session()
        
        logger.info(f"Initializing Odoo client for {url}")
        logger.info(f"Database: {database}, Username: {username}")
    
    def _json_rpc(self, endpoint: str, method: str, params: Dict[str, Any] = None) -> Dict[str, Any]:
        """Make JSON-RPC call to Odoo"""
        url = f"{self.url}/{endpoint}"
        
        payload = {
            "jsonrpc": "2.0",
            "method": method,
            "params": params or {},
            "id": 1
        }
        
        headers = {
            "Content-Type": "application/json"
        }
        
        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()
            
            if 'error' in result:
                logger.error(f"Odoo JSON-RPC error: {result['error']}")
                raise Exception(f"Odoo API Error: {result['error'].get('message', 'Unknown error')}")
            
            return result.get('result', {})
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Connection to Odoo failed: {str(e)}")
    
    def authenticate(self) -> bool:
        """Authenticate with Odoo using API key"""
        try:
            # Try to authenticate using /web/session/authenticate
            result = self._json_rpc(
                "jsonrpc",
                "call",
                {
                    "service": "common",
                    "method": "authenticate",
                    "args": [
                        self.database,
                        self.username,
                        self.api_key,
                        {"base": self.db_password} if self.db_password else {}
                    ]
                }
            )
            
            if result and 'uid' in result:
                self.uid = result['uid']
                logger.info(f"Successfully authenticated as user {self.uid}")
                return True
            else:
                logger.warning("Authentication returned no UID")
                return False
                
        except Exception as e:
            logger.error(f"Authentication failed: {e}")
            # Try alternative authentication method
            return self._authenticate_legacy()
    
    def _authenticate_legacy(self) -> bool:
        """Legacy authentication using DB password"""
        try:
            if not self.db_password:
                logger.error("DB password required for legacy auth")
                return False
            
            result = self._json_rpc(
                "jsonrpc",
                "call",
                {
                    "service": "common",
                    "method": "login",
                    "args": [
                        self.database,
                        self.username,
                        self.db_password
                    ]
                }
            )
            
            if result:
                self.uid = result
                logger.info(f"Successfully authenticated (legacy) as user {self.uid}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"Legacy authentication failed: {e}")
            return False
    
    def execute_kw(
        self,
        model: str,
        method: str,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None
    ) -> Any:
        """Execute Odoo model method"""
        if not self.uid:
            raise Exception("Not authenticated. Call authenticate() first.")
        
        params = {
            "model": model,
            "method": method,
            "args": args or [],
            "kwargs": kwargs or {}
        }
        
        result = self._json_rpc(
            "jsonrpc",
            "call",
            {
                "service": "object",
                "method": "execute_kw",
                "args": [
                    self.database,
                    self.uid,
                    self.api_key,
                    model,
                    method,
                    args or [],
                    kwargs or {}
                ]
            }
        )
        
        return result
    
    # ============ Business Methods ============
    
    def create_invoice(
        self,
        partner_id: int,
        invoice_type: str = "out_invoice",
        lines: List[Dict[str, Any]] = None,
        invoice_date: str = None
    ) -> Dict[str, Any]:
        """
        Create a new customer invoice
        
        Args:
            partner_id: Customer/partner ID
            invoice_type: Type (out_invoice, in_invoice, out_refund, in_refund)
            lines: Invoice lines with product_id, quantity, price_unit
            invoice_date: Invoice date (YYYY-MM-DD)
        
        Returns:
            Dict with invoice_id and invoice_number
        """
        logger.info(f"Creating invoice for partner {partner_id}")
        
        # Prepare invoice values
        invoice_vals = {
            "move_type": invoice_type,
            "partner_id": partner_id,
            "invoice_date": invoice_date or fields.Date.today(),
        }
        
        # Add invoice lines if provided
        if lines:
            invoice_lines = []
            for line in lines:
                invoice_lines.append((0, 0, {
                    "product_id": line.get("product_id"),
                    "quantity": line.get("quantity", 1),
                    "price_unit": line.get("price_unit", 0),
                    "name": line.get("name", "Service")
                }))
            invoice_vals["invoice_line_ids"] = invoice_lines
        
        # Create invoice
        invoice_id = self.execute_kw(
            "account.move",
            "create",
            [invoice_vals]
        )
        
        logger.info(f"Invoice created with ID: {invoice_id}")
        
        # Get invoice number
        invoice_data = self.execute_kw(
            "account.move",
            "read",
            [[invoice_id], ["name"]]
        )
        
        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice_data[0].get("name") if invoice_data else "Draft",
            "status": "created"
        }
    
    def read_partner(self, partner_id: int = None, email: str = None) -> Dict[str, Any]:
        """
        Read partner (customer/vendor) information
        
        Args:
            partner_id: Partner ID to read
            email: Email to search partner by
        
        Returns:
            Partner data dict
        """
        logger.info(f"Reading partner: ID={partner_id}, Email={email}")
        
        # Search for partner
        domain = []
        if partner_id:
            domain.append(("id", "=", partner_id))
        elif email:
            domain.append(("email", "=", email))
        else:
            raise Exception("Either partner_id or email must be provided")
        
        partner_ids = self.execute_kw(
            "res.partner",
            "search",
            [domain]
        )
        
        if not partner_ids:
            return {"error": "Partner not found"}
        
        # Read partner data
        partner_data = self.execute_kw(
            "res.partner",
            "read",
            [partner_ids, ["name", "email", "phone", "street", "city", "country_id", "vat"]]
        )
        
        return partner_data[0] if partner_data else {}
    
    def create_task(
        self,
        name: str,
        project_id: int,
        user_id: int = None,
        description: str = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """
        Create a new project task
        
        Args:
            name: Task name
            project_id: Project ID
            user_id: Assigned user ID
            description: Task description
            priority: Priority (normal, low, high)
        
        Returns:
            Dict with task_id and task_name
        """
        logger.info(f"Creating task '{name}' in project {project_id}")
        
        task_vals = {
            "name": name,
            "project_id": project_id,
            "description": description or "",
            "priority": priority,
            "user_ids": [(4, user_id)] if user_id else []
        }
        
        task_id = self.execute_kw(
            "project.task",
            "create",
            [task_vals]
        )
        
        logger.info(f"Task created with ID: {task_id}")
        
        return {
            "task_id": task_id,
            "task_name": name,
            "project_id": project_id,
            "status": "created"
        }
    
    def get_revenue_summary(
        self,
        start_date: str = None,
        end_date: str = None
    ) -> Dict[str, Any]:
        """
        Get revenue summary for a period
        
        Args:
            start_date: Start date (YYYY-MM-DD), defaults to first of current month
            end_date: End date (YYYY-MM-DD), defaults to today
        
        Returns:
            Revenue summary dict with total, invoices count, etc.
        """
        from datetime import datetime, timedelta
        
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")
        
        logger.info(f"Getting revenue summary from {start_date} to {end_date}")
        
        # Search for posted invoices in date range
        domain = [
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("state", "=", "posted"),
            ("invoice_date", ">=", start_date),
            ("invoice_date", "<=", end_date)
        ]
        
        invoice_ids = self.execute_kw(
            "account.move",
            "search",
            [domain]
        )
        
        # Read invoice amounts
        invoices_data = self.execute_kw(
            "account.move",
            "read",
            [invoice_ids, ["amount_total", "amount_residual", "name", "invoice_date"]]
        )
        
        total_revenue = sum(inv.get("amount_total", 0) for inv in invoices_data)
        total_outstanding = sum(inv.get("amount_residual", 0) for inv in invoices_data)
        
        return {
            "period": f"{start_date} to {end_date}",
            "total_revenue": total_revenue,
            "total_outstanding": total_outstanding,
            "total_paid": total_revenue - total_outstanding,
            "invoices_count": len(invoices_data),
            "invoices": [
                {
                    "number": inv.get("name"),
                    "date": inv.get("invoice_date"),
                    "total": inv.get("amount_total"),
                    "paid": inv.get("amount_total") - inv.get("amount_residual"),
                    "outstanding": inv.get("amount_residual")
                }
                for inv in invoices_data[:10]  # Limit to 10 for summary
            ]
        }


# Initialize Odoo client
odoo_client: Optional[OdooClient] = None


def get_odoo_client() -> OdooClient:
    """Get or create Odoo client instance"""
    global odoo_client
    
    if odoo_client is None:
        odoo_url = os.getenv("ODOO_URL", "http://localhost:8069")
        odoo_db = os.getenv("ODOO_DATABASE", "ai_employee_business")
        odoo_user = os.getenv("ODOO_USERNAME", "admin")
        odoo_api_key = os.getenv("ODOO_API_KEY", "")
        odoo_db_password = os.getenv("ODOO_DB_PASSWORD", "")
        
        odoo_client = OdooClient(
            url=odoo_url,
            database=odoo_db,
            username=odoo_user,
            api_key=odoo_api_key,
            db_password=odoo_db_password
        )
        
        # Authenticate
        if not odoo_client.authenticate():
            logger.warning("Odoo authentication failed")
    
    return odoo_client


# ============ MCP Tool Functions ============

def odoo_create_invoice(
    partner_id: int,
    invoice_type: str = "out_invoice",
    lines: List[Dict[str, Any]] = None,
    invoice_date: str = None
) -> Dict[str, Any]:
    """
    Create a new invoice in Odoo
    
    Args:
        partner_id: Customer/partner ID
        invoice_type: Type of invoice
        lines: Invoice lines
        invoice_date: Invoice date
    
    Returns:
        Invoice creation result
    """
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}
        
        result = client.create_invoice(partner_id, invoice_type, lines, invoice_date)
        logger.info(f"Invoice created: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating invoice: {e}")
        return {"error": str(e)}


def odoo_read_partner(
    partner_id: int = None,
    email: str = None
) -> Dict[str, Any]:
    """
    Read partner information from Odoo
    
    Args:
        partner_id: Partner ID
        email: Partner email
    
    Returns:
        Partner data
    """
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}
        
        result = client.read_partner(partner_id, email)
        logger.info(f"Partner data retrieved: {result.get('name', 'Unknown')}")
        return result
        
    except Exception as e:
        logger.error(f"Error reading partner: {e}")
        return {"error": str(e)}


def odoo_create_task(
    name: str,
    project_id: int,
    user_id: int = None,
    description: str = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """
    Create a new task in Odoo project
    
    Args:
        name: Task name
        project_id: Project ID
        user_id: Assigned user ID
        description: Task description
        priority: Task priority
    
    Returns:
        Task creation result
    """
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}
        
        result = client.create_task(name, project_id, user_id, description, priority)
        logger.info(f"Task created: {result}")
        return result
        
    except Exception as e:
        logger.error(f"Error creating task: {e}")
        return {"error": str(e)}


def odoo_get_revenue_summary(
    start_date: str = None,
    end_date: str = None
) -> Dict[str, Any]:
    """
    Get revenue summary from Odoo
    
    Args:
        start_date: Start date (YYYY-MM-DD)
        end_date: End date (YYYY-MM-DD)
    
    Returns:
        Revenue summary
    """
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}
        
        result = client.get_revenue_summary(start_date, end_date)
        logger.info(f"Revenue summary retrieved: {result.get('total_revenue', 0)}")
        return result
        
    except Exception as e:
        logger.error(f"Error getting revenue summary: {e}")
        return {"error": str(e)}


# ============ Main Entry Point ============

def main():
    """Main function for testing Odoo MCP server"""
    import argparse
    
    parser = argparse.ArgumentParser(description="Odoo MCP Server for Personal AI Employee")
    parser.add_argument("--test", action="store_true", help="Run connection test")
    parser.add_argument("--revenue", action="store_true", help="Get revenue summary")
    parser.add_argument("--partner", type=str, help="Get partner by email")
    
    args = parser.parse_args()
    
    if args.test:
        print("Testing Odoo connection...")
        client = get_odoo_client()
        if client and client.uid:
            print(f"✅ Connected to Odoo!")
            print(f"   URL: {client.url}")
            print(f"   Database: {client.database}")
            print(f"   User ID: {client.uid}")
        else:
            print("❌ Failed to connect to Odoo")
            print("   Check your .env configuration")
    
    if args.revenue:
        print("Getting revenue summary...")
        result = odoo_get_revenue_summary()
        print(json.dumps(result, indent=2))
    
    if args.partner:
        print(f"Looking up partner: {args.partner}")
        result = odoo_read_partner(email=args.partner)
        print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

```

---

## Quick Reference

### Docker Commands

```bash
# Start Odoo
docker-compose up -d

# Stop Odoo
docker-compose down

# View logs
docker-compose logs -f odoo

# Restart Odoo
docker-compose restart odoo

# Access Odoo shell
docker exec -it odoo-community-19 odoo shell -d ai_employee_business
```

### Required .env Variables

```bash
# Odoo Configuration
ODOO_URL=http://localhost:8069
ODOO_DATABASE=ai_employee_business
ODOO_USERNAME=admin
ODOO_API_KEY=your_api_key_here
ODOO_DB_PASSWORD=odoo_db_password_123
```

### Test Commands

```bash
# Test Odoo connection
python mcp_servers/odoo_mcp.py --test

# Get revenue summary
python mcp_servers/odoo_mcp.py --revenue

# Lookup partner by email
python mcp_servers/odoo_mcp.py --partner "customer@example.com"
```

---

## Next Steps

After completing setup:

1. ✅ Verify Odoo is running at `http://localhost:8069`
2. ✅ Create API key and save to `.env`
3. ✅ Run test command to verify connection
4. ⏭️ Proceed to CEO Briefing integration

---

**Document Version:** 1.0  
**Last Updated:** 2026-03-02  
**Next Phase:** Gold Tier - CEO Briefing Generation
