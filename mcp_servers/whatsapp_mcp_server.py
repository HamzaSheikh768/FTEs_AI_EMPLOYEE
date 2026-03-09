"""
MCP Server for WhatsApp Watcher functionality
Exposes WhatsApp monitoring and sending capabilities as MCP tools
"""
import os
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field, ConfigDict, field_validator
from mcp.server.fastmcp import FastMCP
from mcp.server.transport_security import TransportSecuritySettings

# Initialize FastMCP with stateless HTTP transport
transport_security = TransportSecuritySettings(
    allowed_hosts=[
        "127.0.0.1:*",
        "localhost:*",
        "[::1]:*",
        "whatsapp-mcp:*",
        "0.0.0.0:*",
    ],
)

mcp = FastMCP("whatsapp_mcp", transport_security=transport_security)


class AuthenticatedInput(BaseModel):
    """Base model with auth fields for all tools."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="User ID performing the action")
    access_token: Optional[str] = Field(
        None,
        description="JWT access token (optional in dev mode)"
    )


class SendMessageInput(AuthenticatedInput):
    """Input model for sending WhatsApp messages."""
    recipient: str = Field(..., description="Contact name or phone number")
    message: str = Field(..., min_length=1, max_length=4000, description="Message content")
    attachment_path: Optional[str] = Field(
        default=None,
        description="Path to attachment file (image, document, etc.)"
    )

    @field_validator('attachment_path')
    @classmethod
    def validate_attachment(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        path = Path(v)
        if not path.exists():
            raise ValueError(f"Attachment file not found: {v}")
        # Check file size (limit to 16MB for WhatsApp)
        if path.stat().st_size > 16 * 1024 * 1024:
            raise ValueError("Attachment file too large (max 16MB)")
        return v


class CheckMessagesInput(AuthenticatedInput):
    """Input model for checking WhatsApp messages."""
    max_messages: int = Field(default=20, ge=1, le=50, description="Maximum messages to check")
    unread_only: bool = Field(default=True, description="Check only unread messages")
    contact_filter: Optional[str] = Field(
        default=None,
        description="Filter messages from specific contact"
    )


class SearchContactsInput(AuthenticatedInput):
    """Input model for searching WhatsApp contacts."""
    query: str = Field(..., min_length=2, max_length=100, description="Search query")
    limit: int = Field(default=10, ge=1, le=50, description="Maximum contacts to return")


class WhatsAppClient:
    """WhatsApp client with approval workflow."""

    def __init__(self):
        self.api_url = "http://localhost:8002"  # WhatsApp service URL
        self.dev_mode = os.getenv("WHATSAPP_DEV_MODE", "false").lower() == "true"
        self.service_token = os.getenv("WHATSAPP_SERVICE_TOKEN")
        self.vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))
        self.dry_run = os.getenv("WHATSAPP_DRY_RUN", "false").lower() == "true"

        # Keywords that require approval
        self.sensitive_keywords = [
            "payment", "invoice", "bank", "transfer", "money",
            "contract", "legal", "agreement", "sign", "confidential",
            "password", "login", "credential", "ssn", "social security"
        ]

    def _get_headers(self, user_id: str, access_token: Optional[str] = None) -> Dict[str, str]:
        """Get appropriate headers based on authentication mode."""
        headers: Dict[str, str] = {"Content-Type": "application/json"}

        if self.service_token:
            headers["Authorization"] = f"Bearer {self.service_token}"
            headers["X-User-ID"] = user_id
        elif access_token:
            headers["Authorization"] = f"Bearer {access_token}"
        elif self.dev_mode:
            headers["X-User-ID"] = user_id
            headers["X-Service"] = "whatsapp-mcp"

        return headers

    def _requires_approval(self, message: str) -> bool:
        """Check if message contains sensitive keywords."""
        message_lower = message.lower()
        return any(keyword in message_lower for keyword in self.sensitive_keywords)

    async def send_message(self, params: SendMessageInput) -> Dict[str, Any]:
        """Send a WhatsApp message with optional approval."""
        import httpx

        # Check for sensitive content
        requires_approval = self._requires_approval(params.message)

        if requires_approval and not self.dry_run:
            # Create approval request
            approval_dir = self.vault_path / "Pending_Approval"
            approval_dir.mkdir(parents=True, exist_ok=True)

            message_id = f"whatsapp_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{params.user_id}"

            approval_file = approval_dir / f"{message_id}.md"
            approval_content = f"""# WhatsApp Message Approval Required

## Message Details
- **Message ID**: {message_id}
- **User**: {params.user_id}
- **Recipient**: {params.recipient}
- **Created**: {datetime.now().isoformat()}
- **Requires Approval**: Contains sensitive keywords

## Content
{params.message}

## Attachment
{params.attachment_path or 'None'}

## Metadata
```json
{{
    "message_id": "{message_id}",
    "user_id": "{params.user_id}",
    "recipient": "{params.recipient}",
    "attachment_path": "{params.attachment_path or ''}",
    "sensitive_keywords": [kw for kw in {json.dumps(self.sensitive_keywords)} if kw in "{params.message.lower()}"]
}}
```

## Approval Required
Move this file to `Approved/` to send the message or `Rejected/` to cancel.
"""

            with open(approval_file, "w", encoding="utf-8") as f:
                f.write(approval_content)

            await self._log_to_vault(params.user_id, "message_approval_required", {
                "message_id": message_id,
                "recipient": params.recipient,
                "reason": "sensitive_content"
            })

            return {
                "success": False,
                "message": "Message contains sensitive content and requires approval",
                "message_id": message_id,
                "approval_file": str(approval_file),
                "requires_approval": True
            }

        # Send message directly
        headers = self._get_headers(params.user_id, params.access_token)
        message_data = {
            "recipient": params.recipient,
            "message": params.message,
            "attachment_path": params.attachment_path
        }

        if self.dry_run:
            await self._log_to_vault(params.user_id, "message_sent_dry_run", message_data)
            return {
                "success": True,
                "message": "Message sent (dry run)",
                "dry_run": True
            }

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/whatsapp/send",
                    headers=headers,
                    json=message_data
                )
                response.raise_for_status()
                result = response.json()

                await self._log_to_vault(params.user_id, "message_sent", {
                    "recipient": params.recipient,
                    "message_id": result.get("message_id")
                })

                return {
                    "success": True,
                    "message": "Message sent successfully",
                    "message_id": result.get("message_id")
                }

        except httpx.HTTPStatusError as e:
            if e.response.status_code == 404:
                return {"success": False, "message": "Recipient not found"}
            return {"success": False, "message": f"Failed to send message: {e.response.status_code}"}
        except Exception as e:
            return {"success": False, "message": f"Unexpected error: {str(e)}"}

    async def check_messages(self, params: CheckMessagesInput) -> Dict[str, Any]:
        """Check WhatsApp messages."""
        import httpx

        headers = self._get_headers(params.user_id, params.access_token)

        query_params = {
            "max_messages": params.max_messages,
            "unread_only": params.unread_only
        }
        if params.contact_filter:
            query_params["contact_filter"] = params.contact_filter

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/api/whatsapp/messages",
                    headers=headers,
                    params=query_params
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": f"Failed to check messages: {str(e)}"}

    async def search_contacts(self, params: SearchContactsInput) -> Dict[str, Any]:
        """Search WhatsApp contacts."""
        import httpx

        headers = self._get_headers(params.user_id, params.access_token)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/api/whatsapp/contacts/search",
                    headers=headers,
                    params={"query": params.query, "limit": params.limit}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            return {"error": f"Failed to search contacts: {str(e)}"}

    async def _log_to_vault(self, user_id: str, action: str, data: Dict[str, Any]):
        """Log actions to vault for audit."""
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"

        log_entry = (
            f"[{datetime.now().isoformat()}] | WHATSAPP_MCP | {action} | "
            f"User: {user_id} | Data: {json.dumps(data, default=str)}\n"
        )

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


# Initialize client
whatsapp_client = WhatsAppClient()


@mcp.tool(
    name="whatsapp_send_message",
    annotations={
        "title": "Send WhatsApp Message",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def whatsapp_send_message(params: SendMessageInput) -> str:
    """Send a WhatsApp message.

    This tool sends a message via WhatsApp. Messages containing sensitive
    keywords will require approval before sending. Supports file attachments.

    Args:
        params: SendMessageInput containing recipient and message content

    Returns:
        str: JSON-formatted response with send status or approval requirement
    """
    result = await whatsapp_client.send_message(params)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="whatsapp_check_messages",
    annotations={
        "title": "Check WhatsApp Messages",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def whatsapp_check_messages(params: CheckMessagesInput) -> str:
    """Check WhatsApp messages.

    This tool retrieves WhatsApp messages based on criteria. Can filter
    by unread status and specific contacts.

    Args:
        params: CheckMessagesInput with filtering criteria

    Returns:
        str: JSON-formatted list of messages
    """
    result = await whatsapp_client.check_messages(params)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="whatsapp_search_contacts",
    annotations={
        "title": "Search WhatsApp Contacts",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def whatsapp_search_contacts(params: SearchContactsInput) -> str:
    """Search WhatsApp contacts.

    This tool searches for WhatsApp contacts by name or phone number.

    Args:
        params: SearchContactsInput with search query and limit

    Returns:
        str: JSON-formatted list of matching contacts
    """
    result = await whatsapp_client.search_contacts(params)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="whatsapp_get_pending_approvals",
    annotations={
        "title": "Get Pending WhatsApp Approvals",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def whatsapp_get_pending_approvals(
    user_id: str,
    access_token: Optional[str] = None
) -> str:
    """Get pending WhatsApp message approvals.

    This tool retrieves all WhatsApp messages awaiting approval in the vault.

    Args:
        user_id: User ID performing the action
        access_token: JWT access token (optional in dev mode)

    Returns:
        str: JSON-formatted list of pending message approvals
    """
    pending_dir = whatsapp_client.vault_path / "Pending_Approval"
    messages = []

    if pending_dir.exists():
        for file_path in pending_dir.glob("whatsapp_*.md"):
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()

            # Extract basic info
            lines = content.split('\n')
            message_info = {"file": str(file_path), "content_preview": ""}

            for line in lines:
                if line.startswith("- **Message ID**"):
                    message_info["message_id"] = line.split(": ")[1]
                elif line.startswith("- **User**"):
                    message_info["user"] = line.split(": ")[1]
                elif line.startswith("- **Recipient**"):
                    message_info["recipient"] = line.split(": ")[1]
                elif line.startswith("- **Created**"):
                    message_info["created"] = line.split(": ")[1]
                elif line.startswith("## Content"):
                    # Extract content preview
                    idx = lines.index(line) + 1
                    content_lines = []
                    while idx < len(lines) and not lines[idx].startswith("##"):
                        content_lines.append(lines[idx])
                        idx += 1
                    content_text = "\n".join(content_lines).strip()
                    message_info["content_preview"] = (
                        content_text[:100] + "..." if len(content_text) > 100 else content_text
                    )

            messages.append(message_info)

    return json.dumps({"messages": messages}, indent=2)


# Health check endpoint
class HealthMiddleware:
    """Middleware to add health check endpoint."""

    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        if scope["type"] == "http" and scope["path"] == "/health":
            from starlette.responses import JSONResponse
            response = JSONResponse({"status": "healthy"})
            await response(scope, receive, send)
            return
        await self.app(scope, receive, send)


# Create the app with CORS
if __name__ == "__main__":
    from starlette.middleware.cors import CORSMiddleware

    # Import any additional tool modules here
    # import whatsapp_mcp.tools.additional  # noqa: F401

    # Get FastMCP's streamable HTTP app
    _mcp_app = mcp.streamable_http_app()

    # Add health check
    app = HealthMiddleware(_mcp_app)

    # Add CORS wrapper
    app = CORSMiddleware(
        app,
        allow_origins=["*"],
        allow_methods=["GET", "POST", "OPTIONS"],
        allow_headers=["*"],
        expose_headers=["Mcp-Session-Id"],
    )

    # Run the server
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8002,
        reload=False,
    )


# Wrapper class for compatibility with test suite
class WhatsAppMCP:
    """Wrapper class for WhatsApp MCP server."""

    def __init__(self):
        self.mcp = mcp
        self.fastmcp = mcp
        self.client = whatsapp_client
        self.tools = ["whatsapp_send_message", "whatsapp_check_messages", "whatsapp_search_contacts", "whatsapp_get_pending_approvals"]
        # Add _tool_names for test compatibility
        self.fastmcp._tool_names = self.tools