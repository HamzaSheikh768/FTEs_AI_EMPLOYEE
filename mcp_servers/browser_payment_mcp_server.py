#!/usr/bin/env python3
"""
Browser/Payment MCP Server for Personal AI Employee
Exposes browser automation capabilities for payment portals and web forms
Integrates with Playwright for web automation
"""

import os
import sys
import json
import traceback
import importlib.util
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional

from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel, Field

import tempfile
import time


class BrowserActionRequest(BaseModel):
    """Request parameters for browser actions"""
    url: str = Field(description="URL to navigate to")
    actions: List[Dict[str, Any]] = Field(description="List of actions to perform")
    screenshot_path: Optional[str] = Field(default=None, description="Optional screenshot save path")


class PaymentRequest(BaseModel):
    """Request parameters for payment actions"""
    portal_url: str = Field(description="Payment portal URL")
    amount: float = Field(description="Payment amount")
    recipient: str = Field(description="Payment recipient/beneficiary")
    reference: Optional[str] = Field(default=None, description="Payment reference")
    notes: Optional[str] = Field(default=None, description="Payment notes")


class FormFillRequest(BaseModel):
    """Request parameters for form filling"""
    url: str = Field(description="Form URL")
    fields: Dict[str, str] = Field(description="Field names and values to fill")
    submit_selector: Optional[str] = Field(default=None, description="CSS selector for submit button")


def navigate_and_fill_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for browser navigation and form filling"""
    url = request.get("url")
    actions = request.get("actions", [])
    screenshot_path = request.get("screenshot_path")

    if not url:
        return {
            "success": False,
            "error": "url is required"
        }

    try:
        # Import browser automation implementation       
        spec = importlib.util.spec_from_file_location(
            "browser_automation_impl",
            "watcher/browser_automation_impl.py"
        )
        if spec is None or spec.loader is None:
            return {
                "success": False,
                "error": "Failed to load browser_automation_impl module"
            }
        browser_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(browser_module)

        # Initialize browser automation
        automation = browser_module.BrowserAutomation(
            vault_path="AI_Employee_Vault"
        )

        # Setup browser
        if not automation.setup_browser(headless=True):
            return {
                "success": False,
                "error": "Failed to setup browser"
            }

        # Navigate and perform actions
        result = automation.navigate_and_act(url, actions)

        # Take screenshot if requested
        if screenshot_path:
            automation.take_screenshot(screenshot_path)

        return {
            "success": result,
            "actions_performed": len(actions),
            "timestamp": datetime.now().isoformat()
        }

    except Exception as e:
        print(f"Error in navigate_and_fill: {e}")
        traceback.print_exc()
        return {
            "success": False,
            "error": f"Error performing browser actions: {str(e)}"
        }


def prepare_payment_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for preparing payments (draft only)"""
    portal_url = request.get("portal_url")
    amount = request.get("amount")
    recipient = request.get("recipient")
    reference = request.get("reference")
    notes = request.get("notes")

    if not all([portal_url, amount, recipient]):
        return {
            "success": False,
            "payment_id": "",
            "error": "portal_url, amount, and recipient are required"
        }

    try:
        # Create payment approval request
        payment_id = f"PAYMENT_{int(time.time())}_{recipient.replace(' ', '_') if recipient else 'unknown'}"

        # Create approval file in vault
        approval_content = f"""---
type: payment_approval
action: prepare_payment
portal_url: {portal_url}
amount: {amount}
recipient: {recipient}
reference: {reference or ''}
created: {datetime.now().isoformat()}
status: pending_approval
expires: {datetime.now().replace(hour=23, minute=59, second=59).isoformat()}
---

## Payment Approval Request

**Portal:** {portal_url}
**Amount:** ${amount}
**Recipient:** {recipient}
**Reference:** {reference or 'None'}
**Notes:** {notes or 'None'}

## Action Required
Move this file to:
- `/Approved/` to proceed with payment preparation
- `/Rejected/` to cancel this payment

## Security Check
- Verify recipient details
- Confirm amount is correct
- Check for sufficient funds
"""

        # Save to Pending_Approval
        vault_path = Path("AI_Employee_Vault")
        pending_path = vault_path / "Pending_Approval"
        pending_path.mkdir(parents=True, exist_ok=True)

        approval_file = pending_path / f"{payment_id}.md"
        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return {
            "success": True,
            "payment_id": payment_id,
            "status": "pending_approval",
            "message": f"Payment approval request created: {payment_id}"
        }

    except Exception as e:
        print(f"Error in prepare_payment: {e}")
        return {
            "success": False,
            "payment_id": "",
            "error": f"Error creating payment request: {str(e)}"
        }


class BrowserPaymentMCP:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.fastmcp = FastMCP("Browser Payment MCP Server")

        # Register tools

        # Create tool instances with proper parameters
        browser_action_tool = Tool(
            name="browser_action",
            description="Perform browser automation actions",
            parameters=BrowserActionRequest.model_json_schema()
        )

        payment_tool = Tool(
            name="prepare_payment",
            description="Prepare a payment for approval (draft only)",
            parameters=PaymentRequest.model_json_schema()
        )

        form_fill_tool = Tool(
            name="fill_form",
            description="Fill and submit web forms",
            parameters=FormFillRequest.model_json_schema()
        )

        # Add tools to the FastMCP instance
        self.fastmcp.add_tool(browser_action_tool)
        self.fastmcp.add_tool(payment_tool)
        self.fastmcp.add_tool(form_fill_tool)

        # Add _tool_names for test compatibility
        self.fastmcp._tool_names = ["browser_action", "prepare_payment", "fill_form"]

    async def browser_action(self, request: BrowserActionRequest) -> Dict[str, Any]:
        """Perform browser automation actions"""
        try:

            # Check for sensitive operations
            if self._is_sensitive_url(request.url):
                # Create approval request for sensitive operations
                approval_id = await self._create_browser_approval(request)
                return {
                    "success": True,
                    "status": "pending_approval",
                    "approval_id": approval_id
                }

            # Import browser automation implementation
            spec = importlib.util.spec_from_file_location(
                "browser_automation_impl",
                "watcher/browser_automation_impl.py"
            )
            if spec is None or spec.loader is None:
                return {
                    "success": False,
                    "error": "Failed to load browser_automation_impl module"
                }
            browser_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(browser_module)

            # Initialize browser automation
            automation = browser_module.BrowserAutomation(
                vault_path=str(self.vault_path)
            )

            # Setup browser
            if not automation.setup_browser(headless=True):
                return {
                    "success": False,
                    "error": "Failed to setup browser"
                }

            # Navigate and perform actions
            result = automation.navigate_and_act(request.url, request.actions)

            # Take screenshot if requested
            if request.screenshot_path:
                automation.take_screenshot(request.screenshot_path)

            # Log the action
            await self._log_browser_action(request)

            return {
                "success": result,
                "actions_performed": len(request.actions),
                "timestamp": datetime.now().isoformat()
            }

        except Exception as e:
            print(f"Error in browser_action: {e}")

            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }

    async def prepare_payment(self, request: PaymentRequest) -> Dict[str, Any]:
        """Prepare a payment for approval"""
        try:
            payment_id = f"PAYMENT_{int(time.time())}_{request.recipient.replace(' ', '_')}"

            # Create approval file in vault
            approval_content = f"""---
type: payment_approval
action: prepare_payment
portal_url: {request.portal_url}
amount: {request.amount}
recipient: {request.recipient}
reference: {request.reference or ''}
created: {datetime.now().isoformat()}
status: pending_approval
expires: {datetime.now().replace(hour=23, minute=59, second=59).isoformat()}
---

## Payment Approval Request

**Portal:** {request.portal_url}
**Amount:** ${request.amount}
**Recipient:** {request.recipient}
**Reference:** {request.reference or 'None'}
**Notes:** {request.notes or 'None'}

## Security Check
- Verify recipient details
- Confirm amount is correct
- Check for sufficient funds

## Action Required
Move this file to:
- `/Approved/` to proceed with payment preparation
- `/Rejected/` to cancel this payment
"""

            # Save to Pending_Approval
            pending_path = self.vault_path / "Pending_Approval"
            pending_path.mkdir(parents=True, exist_ok=True)

            approval_file = pending_path / f"{payment_id}.md"
            with open(approval_file, 'w', encoding='utf-8') as f:
                f.write(approval_content)

            # Log the payment request
            await self._log_payment_request(request, payment_id)

            return {
                "success": True,
                "payment_id": payment_id,
                "status": "pending_approval",
                "message": f"Payment approval request created: {payment_id}"
            }

        except Exception as e:
            print(f"Error in prepare_payment: {e}")
            return {
                "success": False,
                "payment_id": "",
                "error": str(e)
            }

    async def fill_form(self, request: FormFillRequest) -> Dict[str, Any]:
        """Fill and submit a web form"""
        try:

            # Build actions from form fields
            actions = []
            for field_name, field_value in request.fields.items():
                actions.append({
                    "type": "fill",
                    "selector": f"input[name='{field_name}'], #{field_name}, [data-testid='{field_name}']",
                    "value": field_value
                })

            # Add submit action if specified
            if request.submit_selector:
                actions.append({
                    "type": "click",
                    "selector": request.submit_selector
                })

            # Use browser_action to fill the form
            browser_request = BrowserActionRequest(
                url=request.url,
                actions=actions
            )

            result = await self.browser_action(browser_request)

            return result

        except Exception as e:
            print(f"Error in fill_form: {e}")
            return {
                "success": False,
                "error": str(e)
            }

    def _is_sensitive_url(self, url: str) -> bool:
        """Check if URL is for a sensitive operation"""
        sensitive_domains = [
            "bank", "payment", "paypal", "stripe", "transfer",
            "login", "signin", "auth", "account", "profile",
            "admin", "settings", "security"
        ]

        url_lower = url.lower()
        return any(domain in url_lower for domain in sensitive_domains)

    async def _create_browser_approval(self, request: BrowserActionRequest) -> str:
        """Create approval request for sensitive browser actions"""
        approval_id = f"BROWSER_APPROVAL_{int(time.time())}"

        approval_content = f"""---
type: browser_approval
action: navigate_and_act
url: {request.url}
created: {datetime.now().isoformat()}
status: pending_approval
expires: {datetime.now().replace(hour=23, minute=59, second=59).isoformat()}
---

## Browser Action Approval Request

**URL:** {request.url}
**Actions:** {json.dumps(request.actions, indent=2)}

## Security Warning
This action involves accessing a sensitive URL. Please review carefully.

## Action Required
Move this file to:
- `/Approved/` to proceed with browser action
- `/Rejected/` to cancel this action
"""

        # Save to Pending_Approval
        pending_path = self.vault_path / "Pending_Approval"
        pending_path.mkdir(parents=True, exist_ok=True)

        approval_file = pending_path / f"{approval_id}.md"
        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return approval_id

    async def _log_browser_action(self, request: BrowserActionRequest) -> None:
        """Log browser actions to vault"""
        log_entry = {
            "url": request.url,
            "actions_count": len(request.actions),
            "screenshot": request.screenshot_path
        }

        await self._write_log("browser_action", log_entry)

    async def _log_payment_request(self, request: PaymentRequest, payment_id: str) -> None:
        """Log payment requests to vault"""
        log_entry = {
            "payment_id": payment_id,
            "amount": request.amount,
            "recipient": request.recipient,
            "portal": request.portal_url
        }

        await self._write_log("payment_request", log_entry)

    async def _write_log(self, action_type: str, details: Dict[str, Any]) -> None:
        """Write log entry to vault"""
        log_entry = f"[{datetime.now().isoformat()}] | Browser/Payment MCP | {action_type} | {json.dumps(details)}\n"

        logs_path = self.vault_path / "Logs"
        logs_path.mkdir(parents=True, exist_ok=True)

        log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def serve(self, host: str = "localhost", port: int = 8003):
        """Start the MCP server"""
        return self.fastmcp.run(transport="stdio", show_banner=False)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Browser Payment MCP Server")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8003, help="Port to bind to")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")

    args = parser.parse_args()

    # Set dry run mode if specified
    if args.dry_run:
        os.environ["BROWSER_DRY_RUN"] = "true"

    server = BrowserPaymentMCP(vault_path=args.vault_path)

    print(f"Starting Browser/Payment MCP Server on {args.host}:{args.port}")
    print(f"Vault path: {args.vault_path}")
    print(f"Dry run mode: {args.dry_run}")

    try:
        server.serve(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nBrowser/Payment MCP Server stopped.")


if __name__ == "__main__":
    main()