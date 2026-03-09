#!/usr/bin/env python3
"""
Odoo MCP Server for Personal AI Employee - Gold Tier
Connects to Odoo Community 19+ via JSON-RPC for accounting and business operations

Tools Exposed:
- odoo_create_invoice: Create customer/vendor invoices
- odoo_read_partner: Read customer/vendor information
- odoo_create_task: Create project tasks
- odoo_get_revenue_summary: Get revenue reports
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()  # Load environment variables from .env file

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

try:
    import requests
except ImportError:
    print("Installing required package: requests")
    os.system("pip install requests")
    import requests


# Load environment variables from project root .env
project_root = Path(__file__).parent.parent.parent
env_path = project_root / ".env"
load_dotenv(dotenv_path=env_path)

# Setup logging
logs_dir = Path("AI_Employee_Vault/Logs")
logs_dir.mkdir(parents=True, exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(logs_dir / 'odoo_mcp.log'),
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
        db_password: str = ""
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
        logger.info(f"API Key configured: {'Yes' if api_key else 'No'}")

    def _json_rpc(self, endpoint: str, method: str, params: Optional[Dict[str, Any]] = None) -> Optional[Dict[str, Any]]:
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

        logger.debug(f"Making JSON-RPC call to {url}")

        try:
            response = self.session.post(url, json=payload, headers=headers, timeout=30)
            response.raise_for_status()
            result = response.json()

            if 'error' in result:
                logger.error(f"Odoo JSON-RPC error: {result['error']}")
                raise Exception(f"Odoo API Error: {result['error'].get('message', 'Unknown error')}")

            return result.get('result')

        except requests.exceptions.RequestException as e:
            logger.error(f"Request failed: {e}")
            raise Exception(f"Connection to Odoo failed: {str(e)}")

    def authenticate(self) -> bool:
        """Authenticate with Odoo using API key or DB password"""
        try:
            # Try authentication via common.authenticate
            params = {
                "service": "common",
                "method": "authenticate",
                "args": [
                    self.database,
                    self.username,
                    self.api_key,
                    {"base": self.db_password} if self.db_password else {}
                ]
            }
            result = self._json_rpc("jsonrpc", "call", params)

            if result and 'uid' in result:
                self.uid = result['uid']
                logger.info(f"[OK] Successfully authenticated as user {self.uid}")
                return True
            else:
                logger.warning("Authentication returned no UID")
                return False

        except Exception as e:
            logger.error(f"API key auth failed: {e}")
            # Try legacy authentication with DB password
            return self._authenticate_legacy()

    def _authenticate_legacy(self) -> bool:
        """Legacy authentication using DB password"""
        try:
            if not self.db_password:
                logger.error("DB password required for legacy auth")
                return False

            params = {
                "service": "common",
                "method": "login",
                "args": [
                    self.database,
                    self.username,
                    self.db_password
                ]
            }
            result = self._json_rpc("jsonrpc", "call", params)

            if result:
                self.uid = result
                logger.info(f"[OK] Successfully authenticated (legacy) as user {self.uid}")
                return True

            return False

        except Exception as e:
            logger.error(f"Legacy authentication failed: {e}")
            return False

    def execute_kw(
        self,
        model: str,
        method: str,
        args: Optional[List[Any]] = None,
        kwargs: Optional[Dict[str, Any]] = None
    ) -> Any:
        """Execute Odoo model method via JSON-RPC"""
        if not self.uid:
            logger.warning("Cannot execute: not authenticated")
            raise Exception("Not authenticated. Call authenticate() first.")

        logger.debug(f"Executing {method} on {model}")

        params = {
            "service": "object",
            "method": "execute_kw",
            "args": [
                self.database,
                self.uid,
                self.api_key,
                model,
                method,
                args if args is not None else [],
                kwargs if kwargs is not None else {}
            ]
        }
        result = self._json_rpc("jsonrpc", "call", params)

        return result

    # ============ Business Methods ============

    def create_invoice(
        self,
        partner_id: int,
        invoice_type: str = "out_invoice",
        lines: Optional[List[Dict[str, Any]]] = None,
        invoice_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new customer invoice"""
        logger.info(f"Creating invoice for partner {partner_id}")

        from datetime import date
        invoice_vals = {
            "move_type": invoice_type,
            "partner_id": partner_id,
            "invoice_date": invoice_date or date.today().isoformat(),
        }

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

        invoice_id = self.execute_kw("account.move", "create", [invoice_vals])
        logger.info(f"Invoice created with ID: {invoice_id}")

        invoice_data = self.execute_kw("account.move", "read", [[invoice_id], ["name"]])

        return {
            "invoice_id": invoice_id,
            "invoice_number": invoice_data[0].get("name") if invoice_data else "Draft",
            "status": "created"
        }

    def read_partner(self, partner_id: Optional[int] = None, email: Optional[str] = None) -> Dict[str, Any]:
        """Read partner (customer/vendor) information"""
        logger.info(f"Reading partner: ID={partner_id}, Email={email}")

        domain = []
        if partner_id:
            domain.append(("id", "=", partner_id))
        elif email:
            domain.append(("email", "=", email))
        else:
            raise Exception("Either partner_id or email must be provided")

        partner_ids = self.execute_kw("res.partner", "search", [domain])

        if not partner_ids:
            return {"error": "Partner not found"}

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
        user_id: Optional[int] = None,
        description: Optional[str] = None,
        priority: str = "normal"
    ) -> Dict[str, Any]:
        """Create a new project task"""
        logger.info(f"Creating task '{name}' in project {project_id}")

        task_vals = {
            "name": name,
            "project_id": project_id,
            "description": description or "",
            "priority": priority,
            "user_ids": [(4, user_id)] if user_id else []
        }

        task_id = self.execute_kw("project.task", "create", [task_vals])
        logger.info(f"Task created with ID: {task_id}")

        return {
            "task_id": task_id,
            "task_name": name,
            "project_id": project_id,
            "status": "created"
        }

    def get_revenue_summary(
        self,
        start_date: Optional[str] = None,
        end_date: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get revenue summary for a period"""
        if not end_date:
            end_date = datetime.now().strftime("%Y-%m-%d")
        if not start_date:
            start_date = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        logger.info(f"Getting revenue summary from {start_date} to {end_date}")

        domain = [
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("state", "=", "posted"),
            ("invoice_date", ">=", start_date),
            ("invoice_date", "<=", end_date)
        ]

        invoice_ids = self.execute_kw("account.move", "search", [domain])

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
                for inv in invoices_data[:10]
            ]
        }

    def create_partner(
        self,
        name: str,
        email: Optional[str] = None,
        phone: Optional[str] = None,
        is_customer: bool = True,
        is_supplier: bool = False
    ) -> Dict[str, Any]:
        """Create a new partner (customer/vendor) in Odoo"""
        logger.info(f"Creating partner: {name}")

        partner_vals = {
            "name": name,
            "email": email or "",
            "phone": phone or "",
            "customer_rank": 1 if is_customer else 0,
            "supplier_rank": 1 if is_supplier else 0,
        }

        partner_id = self.execute_kw("res.partner", "create", [partner_vals])
        logger.info(f"Partner created with ID: {partner_id}")

        return {
            "partner_id": partner_id,
            "name": name,
            "email": email,
            "status": "created"
        }

    def search_invoices(
        self,
        partner_id: Optional[int] = None,
        state: str = "posted",
        invoice_type: str = "out_invoice",
        limit: int = 10
    ) -> Dict[str, Any]:
        """Search invoices in Odoo"""
        logger.info(f"Searching invoices: state={state}, type={invoice_type}")

        domain = [
            ("move_type", "=", invoice_type),
            ("state", "=", state)
        ]

        if partner_id:
            domain.append(("partner_id", "=", "partner_id"))

        # Add limit to search
        invoice_ids = self.execute_kw("account.move", "search", [domain])

        if not invoice_ids:
            return {"invoices": [], "count": 0}

        # Apply limit when reading
        invoice_ids = invoice_ids[:limit]

        invoices_data = self.execute_kw(
            "account.move",
            "read",
            [invoice_ids, ["name", "invoice_date", "amount_total", "amount_residual", "state", "partner_id"]]
        )

        return {
            "invoices": invoices_data,
            "count": len(invoices_data)
        }

    def get_monthly_revenue(
        self,
        month: Optional[int] = None,
        year: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get monthly revenue summary"""
        from datetime import datetime, timedelta

        if not month or not year:
            now = datetime.now()
            month = now.month
            year = now.year

        logger.info(f"Getting revenue for {month}/{year}")

        # Calculate start and end dates
        start_date = f"{year}-{month:02d}-01"
        if month == 12:
            end_date = f"{year + 1}-01-01"
        else:
            end_date = f"{year}-{month + 1:02d}-01"

        domain = [
            ("move_type", "in", ["out_invoice", "out_refund"]),
            ("state", "=", "posted"),
            ("invoice_date", ">=", start_date),
            ("invoice_date", "<", end_date)
        ]

        invoice_ids = self.execute_kw("account.move", "search", [domain])

        if not invoice_ids:
            return {
                "month": month,
                "year": year,
                "total_revenue": 0,
                "invoices_count": 0,
                "invoices": []
            }

        invoices_data = self.execute_kw(
            "account.move",
            "read",
            [invoice_ids, ["name", "invoice_date", "amount_total", "state"]]
        )

        total_revenue = sum(inv.get("amount_total", 0) for inv in invoices_data)

        return {
            "month": month,
            "year": year,
            "total_revenue": total_revenue,
            "invoices_count": len(invoices_data),
            "invoices": invoices_data[:10]  # Limit to 10 for summary
        }

    def post_journal_entry(
        self,
        name: str,
        date: str,
        lines: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Post a journal entry in Odoo"""
        logger.info(f"Creating journal entry: {name}")

        # Create move lines
        move_lines = []
        for line in lines:
            move_lines.append((0, 0, {
                "account_id": line.get("account_id"),
                "debit": line.get("debit", 0),
                "credit": line.get("credit", 0),
                "name": line.get("name", name),
                "partner_id": line.get("partner_id")
            }))

        move_vals = {
            "name": name,
            "date": date,
            "line_ids": move_lines,
            "journal_id": lines[0].get("journal_id", 1) if lines else 1,
            "state": "draft"
        }

        move_id = self.execute_kw("account.move", "create", [move_vals])
        logger.info(f"Journal entry created with ID: {move_id}")

        # Post the entry
        self.execute_kw("account.move", "action_post", [[move_id]])
        logger.info(f"Journal entry posted: {move_id}")

        return {
            "move_id": move_id,
            "name": name,
            "status": "posted"
        }

    def create_product(
        self,
        name: str,
        list_price: float = 0.0,
        product_type: str = "service",
        default_code: Optional[str] = None
    ) -> Dict[str, Any]:
        """Create a new product in Odoo"""
        logger.info(f"Creating product: {name}")

        product_vals = {
            "name": name,
            "list_price": list_price,
            "type": product_type,
            "default_code": default_code or "",
        }

        product_id = self.execute_kw("product.template", "create", [product_vals])
        logger.info(f"Product created with ID: {product_id}")

        return {
            "product_id": product_id,
            "name": name,
            "price": list_price,
            "status": "created"
        }

    def create_payment(
        self,
        invoice_id: int,
        amount: float,
        payment_date: str,
        payment_method: str = "manual"
    ) -> Dict[str, Any]:
        """Register payment for an invoice"""
        logger.info(f"Creating payment for invoice {invoice_id}, amount: {amount}")

        payment_vals = {
            "move_id": invoice_id,
            "amount": amount,
            "payment_date": payment_date,
            "payment_method": payment_method,
        }

        # Create payment register wizard
        payment_register_id = self.execute_kw("account.payment.register", "create", [payment_vals])

        # Create payment from wizard
        payment_result = self.execute_kw(
            "account.payment.register",
            "action_create_payments",
            [[payment_register_id]]
        )

        logger.info(f"Payment created: {payment_result}")

        return {
            "payment_id": payment_result.get("res_id") if payment_result else None,
            "invoice_id": invoice_id,
            "amount": amount,
            "status": "created"
        }

    def get_account_balance(
        self,
        account_code: str,
        partner_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """Get account balance"""
        logger.info(f"Getting balance for account: {account_code}")

        # Search for account
        account_ids = self.execute_kw(
            "account.account",
            "search",
            [[("code", "=", account_code)]]
        )

        if not account_ids:
            return {"error": f"Account {account_code} not found"}

        # Get account details
        account_data = self.execute_kw(
            "account.account",
            "read",
            [account_ids, ["name", "code", "balance"]]
        )

        return {
            "account_code": account_code,
            "account_name": account_data[0].get("name") if account_data else "",
            "balance": account_data[0].get("balance", 0) if account_data else 0,
            "partner_id": partner_id
        }


# Global Odoo client instance
_odoo_client: Optional[OdooClient] = None


def get_odoo_client() -> Optional[OdooClient]:
    """Get or create Odoo client instance"""
    global _odoo_client

    if _odoo_client is None:
        odoo_url = os.getenv("ODOO_URL", "http://localhost:8069")
        odoo_db = os.getenv("ODOO_DATABASE", "ai_employee_business")
        odoo_user = os.getenv("ODOO_USERNAME", "admin")
        odoo_api_key = os.getenv("ODOO_API_KEY", "")
        odoo_db_password = os.getenv("ODOO_DB_PASSWORD", "")

        _odoo_client = OdooClient(
            url=odoo_url,
            database=odoo_db,
            username=odoo_user,
            api_key=odoo_api_key,
            db_password=odoo_db_password
        )

        if not _odoo_client.authenticate():
            logger.warning("[WARN] Odoo authentication failed")
            return None

    return _odoo_client


# ============ MCP Tool Functions ============

def odoo_create_invoice(
    partner_id: int,
    invoice_type: str = "out_invoice",
    lines: Optional[List[Dict[str, Any]]] = None,
    invoice_date: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new invoice in Odoo"""
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
    partner_id: Optional[int] = None,
    email: Optional[str] = None
) -> Dict[str, Any]:
    """Read partner information from Odoo"""
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
    user_id: Optional[int] = None,
    description: Optional[str] = None,
    priority: str = "normal"
) -> Dict[str, Any]:
    """Create a new task in Odoo project"""
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
    start_date: Optional[str] = None,
    end_date: Optional[str] = None
) -> Dict[str, Any]:
    """Get revenue summary from Odoo"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.get_revenue_summary(start_date, end_date)
        if result:
            total_revenue = result.get('total_revenue', 0)
            logger.info(f"Revenue summary retrieved: {total_revenue}")
        return result

    except Exception as e:
        logger.error(f"Error getting revenue summary: {e}")
        return {"error": str(e)}


def odoo_create_partner(
    name: str,
    email: Optional[str] = None,
    phone: Optional[str] = None,
    is_customer: bool = True,
    is_supplier: bool = False
) -> Dict[str, Any]:
    """Create a new partner in Odoo"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.create_partner(name, email, phone, is_customer, is_supplier)
        logger.info(f"Partner created: {result}")
        return result

    except Exception as e:
        logger.error(f"Error creating partner: {e}")
        return {"error": str(e)}


def odoo_search_invoices(
    partner_id: Optional[int] = None,
    state: str = "posted",
    invoice_type: str = "out_invoice",
    limit: int = 10
) -> Dict[str, Any]:
    """Search invoices in Odoo"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.search_invoices(partner_id, state, invoice_type, limit)
        logger.info(f"Invoices found: {result.get('count', 0)}")
        return result

    except Exception as e:
        logger.error(f"Error searching invoices: {e}")
        return {"error": str(e)}


def odoo_get_monthly_revenue(
    month: Optional[int] = None,
    year: Optional[int] = None
) -> Dict[str, Any]:
    """Get monthly revenue summary"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.get_monthly_revenue(month, year)
        logger.info(f"Monthly revenue: {result.get('total_revenue', 0)}")
        return result

    except Exception as e:
        logger.error(f"Error getting monthly revenue: {e}")
        return {"error": str(e)}


def odoo_post_journal_entry(
    name: str,
    date: str,
    lines: List[Dict[str, Any]]
) -> Dict[str, Any]:
    """Post a journal entry in Odoo"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.post_journal_entry(name, date, lines)
        logger.info(f"Journal entry posted: {result}")
        return result

    except Exception as e:
        logger.error(f"Error posting journal entry: {e}")
        return {"error": str(e)}


def odoo_create_product(
    name: str,
    list_price: float = 0.0,
    product_type: str = "service",
    default_code: Optional[str] = None
) -> Dict[str, Any]:
    """Create a new product in Odoo"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.create_product(name, list_price, product_type, default_code)
        logger.info(f"Product created: {result}")
        return result

    except Exception as e:
        logger.error(f"Error creating product: {e}")
        return {"error": str(e)}


def odoo_create_payment(
    invoice_id: int,
    amount: float,
    payment_date: str,
    payment_method: str = "manual"
) -> Dict[str, Any]:
    """Register payment for an invoice"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.create_payment(invoice_id, amount, payment_date, payment_method)
        logger.info(f"Payment created: {result}")
        return result

    except Exception as e:
        logger.error(f"Error creating payment: {e}")
        return {"error": str(e)}


def odoo_get_account_balance(
    account_code: str,
    partner_id: Optional[int] = None
) -> Dict[str, Any]:
    """Get account balance"""
    try:
        client = get_odoo_client()
        if not client:
            return {"error": "Odoo client not initialized"}

        result = client.get_account_balance(account_code, partner_id)
        logger.info(f"Account balance: {result}")
        return result

    except Exception as e:
        logger.error(f"Error getting account balance: {e}")
        return {"error": str(e)}


# ============ Main Entry Point ============

def main():
    """Main function for testing Odoo MCP server"""
    import argparse

    parser = argparse.ArgumentParser(description="Odoo MCP Server for Personal AI Employee")
    parser.add_argument("--test", action="store_true", help="Run connection test")
    parser.add_argument("--revenue", action="store_true", help="Get revenue summary")
    parser.add_argument("--partner", type=str, help="Get partner by email")
    parser.add_argument("--create-invoice", type=int, help="Create invoice for partner ID")
    parser.add_argument("--create-task", type=str, help="Create task (format: name,project_id)")

    args = parser.parse_args()

    print("=" * 60)
    print("ODOO MCP SERVER - Gold Tier Test")
    print("=" * 60)

    if args.test:
        print("")
        print("[INFO] Testing Odoo connection...")
        client = get_odoo_client()
        if client and client.uid:
            print("")
            print("[OK] CONNECTED to Odoo!")
            print(f"   URL: {client.url}")
            print(f"   Database: {client.database}")
            print(f"   User ID: {client.uid}")
            print("")
            print("[OK] Odoo MCP Server is ready!")
        else:
            print("")
            print("[ERROR] Failed to connect to Odoo")
            print("   Check your .env configuration:")
            print("   - ODOO_URL=http://localhost:8069")
            print("   - ODOO_DATABASE=ai_employee_business")
            print("   - ODOO_USERNAME=admin")
            print("   - ODOO_API_KEY=<your_api_key>")
            print("   - ODOO_DB_PASSWORD=your_db_password")

    if args.revenue:
        print("")
        print("[INFO] Getting revenue summary...")
        result = odoo_get_revenue_summary()
        print(json.dumps(result, indent=2))

    if args.partner:
        print("")
        print(f"[INFO] Looking up partner: {args.partner}")
        result = odoo_read_partner(email=args.partner)
        print(json.dumps(result, indent=2))

    if args.create_invoice:
        print("")
        print(f"[INFO] Creating invoice for partner {args.create_invoice}...")
        result = odoo_create_invoice(args.create_invoice)
        print(json.dumps(result, indent=2))

    if args.create_task:
        parts = args.create_task.split(',')
        if len(parts) >= 2:
            name = parts[0]
            project_id = int(parts[1])
            print("")
            print(f"[INFO] Creating task '{name}' in project {project_id}...")
            result = odoo_create_task(name, project_id)
            print(json.dumps(result, indent=2))
        else:
            print("Invalid format. Use: --create-task 'Task Name,project_id'")

    print("")
    print("=" * 60)


if __name__ == "__main__":
    main()
