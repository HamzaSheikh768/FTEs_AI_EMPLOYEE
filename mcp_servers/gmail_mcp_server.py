"""
MCP Server for Gmail Watcher functionality
Exposes Gmail monitoring and sending capabilities as MCP tools
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
        "gmail-mcp:*",
        "0.0.0.0:*",
    ],
)

mcp = FastMCP("gmail_mcp", transport_security=transport_security)


class AuthenticatedInput(BaseModel):
    """Base model with auth fields for all tools."""
    model_config = ConfigDict(str_strip_whitespace=True)

    user_id: str = Field(..., description="User ID performing the action")
    access_token: Optional[str] = Field(
        None,
        description="JWT access token (optional in dev mode)"
    )


class CheckEmailsInput(AuthenticatedInput):
    """Input model for checking emails."""
    max_emails: int = Field(default=10, ge=1, le=50, description="Maximum number of emails to check")
    include_body: bool = Field(default=True, description="Whether to include email body in response")
    unread_only: bool = Field(default=True, description="Whether to check only unread emails")
    query: Optional[str] = Field(default=None, description="Gmail search query (e.g., 'from:example.com')")


class SendEmailInput(AuthenticatedInput):
    """Input model for sending emails."""
    to: str = Field(..., description="Recipient email address")
    subject: str = Field(..., min_length=1, max_length=200, description="Email subject")
    body: str = Field(..., min_length=1, description="Email body content")
    cc: Optional[str] = Field(default=None, description="CC recipients (comma-separated)")
    bcc: Optional[str] = Field(default=None, description="BCC recipients (comma-separated)")

    @field_validator('to', 'cc', 'bcc')
    @classmethod
    def validate_emails(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        emails = [e.strip() for e in v.split(',')]
        for email in emails:
            if '@' not in email or '.' not in email.split('@')[1]:
                raise ValueError(f"Invalid email address: {email}")
        return v


class EmailClient:
    """Gmail API client with authentication."""

    def __init__(self):
        self.api_url = "http://localhost:8000"  # Gmail service URL
        self.dev_mode = os.getenv("GMAIL_DEV_MODE", "false").lower() == "true"
        self.service_token = os.getenv("GMAIL_SERVICE_TOKEN")
        self.vault_path = Path(os.getenv("VAULT_PATH", "AI_Employee_Vault"))

    def _get_headers(self, user_id: str, access_token: Optional[str] = None) -> Dict[str, str]:
        """Get appropriate headers based on authentication mode."""
        headers: Dict[str, str] = {"Content-Type": "application/json"}

        if self.service_token:
            # Service-to-service authentication
            headers["Authorization"] = f"Bearer {self.service_token}"
            headers["X-User-ID"] = user_id
        elif access_token:
            # Forward user's JWT
            headers["Authorization"] = f"Bearer {access_token}"
        elif self.dev_mode:
            # Dev mode bypass
            headers["X-User-ID"] = user_id
            headers["X-Service"] = "gmail-mcp"

        return headers

    async def check_emails(self, params: CheckEmailsInput) -> Dict[str, Any]:
        """Check for emails based on criteria."""
        import httpx

        headers = self._get_headers(params.user_id, params.access_token)

        # Build query parameters
        query_params = {
            "max_emails": params.max_emails,
            "include_body": params.include_body,
            "unread_only": params.unread_only
        }
        if params.query:
            query_params["query"] = params.query

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.get(
                    f"{self.api_url}/api/emails/check",
                    headers=headers,
                    params=query_params
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"error": "Authentication failed. Please check your credentials."}
            elif e.response.status_code == 403:
                return {"error": "Access denied. Insufficient permissions."}
            return {"error": f"API request failed: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def send_email(self, params: SendEmailInput) -> Dict[str, Any]:
        """Send an email."""
        import httpx

        headers = self._get_headers(params.user_id, params.access_token)

        # Prepare email data
        email_data = {
            "to": params.to,
            "subject": params.subject,
            "body": params.body
        }
        if params.cc:
            email_data["cc"] = params.cc
        if params.bcc:
            email_data["bcc"] = params.bcc

        # Log to vault for audit
        await self._log_to_vault(params.user_id, "send_email", email_data)

        try:
            async with httpx.AsyncClient(timeout=30.0) as client:
                response = await client.post(
                    f"{self.api_url}/api/emails/send",
                    headers=headers,
                    json=email_data
                )
                response.raise_for_status()
                return response.json()
        except httpx.HTTPStatusError as e:
            if e.response.status_code == 401:
                return {"error": "Authentication failed. Please check your credentials."}
            elif e.response.status_code == 403:
                return {"error": "Access denied. Insufficient permissions."}
            return {"error": f"Failed to send email: {e.response.status_code}"}
        except Exception as e:
            return {"error": f"Unexpected error: {str(e)}"}

    async def _log_to_vault(self, user_id: str, action: str, data: Dict[str, Any]):
        """Log actions to vault for audit."""
        log_dir = self.vault_path / "Logs"
        log_dir.mkdir(parents=True, exist_ok=True)

        log_file = log_dir / f"{datetime.now().strftime('%Y-%m-%d')}.md"

        log_entry = (
            f"[{datetime.now().isoformat()}] | GMAIL_MCP | {action} | "
            f"User: {user_id} | Data: {json.dumps(data, default=str)}\n"
        )

        with open(log_file, "a", encoding="utf-8") as f:
            f.write(log_entry)


# Initialize client
email_client = EmailClient()


@mcp.tool(
    name="gmail_check_emails",
    annotations={
        "title": "Check Gmail Emails",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def gmail_check_emails(params: CheckEmailsInput) -> str:
    """Check Gmail emails based on specified criteria.

    This tool retrieves emails from the user's Gmail account based on the
    provided filters. Supports various search queries and can limit results.

    Args:
        params: CheckEmailsInput containing user credentials and search criteria

    Returns:
        str: JSON-formatted response containing email list or error message
    """
    result = await email_client.check_emails(params)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="gmail_send_email",
    annotations={
        "title": "Send Gmail Email",
        "readOnlyHint": False,
        "destructiveHint": False,
        "idempotentHint": False,
        "openWorldHint": True
    }
)
async def gmail_send_email(params: SendEmailInput) -> str:
    """Send an email through Gmail.

    This tool sends an email using the user's Gmail account. The email will be
    logged to the vault for audit purposes. Requires proper authentication.

    Args:
        params: SendEmailInput containing recipient, subject, and body

    Returns:
        str: JSON-formatted response with send status or error message
    """
    result = await email_client.send_email(params)
    return json.dumps(result, indent=2)


@mcp.tool(
    name="gmail_get_thread",
    annotations={
        "title": "Get Gmail Thread",
        "readOnlyHint": True,
        "destructiveHint": False,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def gmail_get_thread(
    user_id: str,
    thread_id: str,
    access_token: Optional[str] = None
) -> str:
    """Retrieve a full Gmail thread by ID.

    This tool fetches all messages in a Gmail thread, providing complete
    conversation history.

    Args:
        user_id: User ID performing the action
        thread_id: Gmail thread ID to retrieve
        access_token: JWT access token (optional in dev mode)

    Returns:
        str: JSON-formatted response containing thread messages or error
    """
    import httpx

    headers = email_client._get_headers(user_id, access_token)

    try:
        async with httpx.AsyncClient(timeout=30.0) as client:
            response = await client.get(
                f"{email_client.api_url}/api/emails/threads/{thread_id}",
                headers=headers
            )
            response.raise_for_status()
            return json.dumps(response.json(), indent=2)
    except httpx.HTTPStatusError as e:
        error = {"error": f"Failed to get thread: {e.response.status_code}"}
        return json.dumps(error, indent=2)
    except Exception as e:
        error = {"error": f"Unexpected error: {str(e)}"}
        return json.dumps(error, indent=2)


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
    # import gmail_mcp.tools.additional  # noqa: F401

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
        port=8000,
        reload=False,
    )