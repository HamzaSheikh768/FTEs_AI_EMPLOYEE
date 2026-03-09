"""
MCP Server for Email Watcher functionality
Exposes Gmail checking capabilities as MCP tools
"""
import os
import sys
import json
import asyncio
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List
from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel, Field
import tempfile


class EmailCheckRequest(BaseModel):
    """Request parameters for checking emails"""
    max_emails: int = Field(default=10, description="Maximum number of emails to check")
    include_body: bool = Field(default=True, description="Whether to include email body in response")
    unread_only: bool = Field(default=True, description="Whether to check only unread emails")


class EmailResponse(BaseModel):
    """Response model for email information"""
    id: str
    threadId: str
    subject: str
    sender: str
    date: str
    body: str = ""
    has_attachments: bool = False


def check_emails_handler(request: Dict[str, Any]) -> List[Dict[str, Any]]:
    """Handler function for checking emails"""
    max_emails = request.get("max_emails", 10)
    include_body = request.get("include_body", True)
    unread_only = request.get("unread_only", True)

    # This would normally call the actual Gmail watcher implementation
    # For now, we'll simulate the functionality

    print(f"Checking emails (max: {max_emails}, unread: {unread_only})")

    # This is a simulated response - in real implementation,
    # we'd call the actual email checking functionality
    # Here we'll return an empty list to indicate no new emails
    # but in a real implementation we'd parse existing email files
    # that were created by the GmailWatcher

    emails = []

    # Look for any email files in the Inbox that were created by GmailWatcher
    vault_path = Path("AI_Employee_Vault")  # Default path
    inbox_path = vault_path / "Inbox"
    if inbox_path.exists():
        email_files = list(inbox_path.glob("EMAIL_*.md"))

        for email_file in email_files[:max_emails]:
            with open(email_file, 'r', encoding='utf-8') as f:
                content = f.read()

            # Extract information from the email file
            lines = content.split('\n')
            subject = "Unknown Subject"
            sender = "Unknown Sender"
            date = "Unknown Date"
            body = ""

            # Parse YAML frontmatter and content
            in_frontmatter = False
            for i, line in enumerate(lines):
                if line.strip() == '---':
                    if not in_frontmatter:
                        in_frontmatter = True  # Start of frontmatter
                    else:
                        in_frontmatter = False  # End of frontmatter
                        body = '\n'.join(lines[i+1:]).strip()  # Content after frontmatter
                        break
                elif in_frontmatter:
                    if line.startswith('subject:'):
                        subject = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('from:'):
                        sender = line.split(':', 1)[1].strip().strip('"\'')
                    elif line.startswith('date:'):
                        date = line.split(':', 1)[1].strip().strip('"\'')

            if not in_frontmatter:  # If frontmatter was not closed, get entire content as body
                body = content

            email_resp = {
                "id": email_file.stem,
                "threadId": email_file.stem,
                "subject": subject,
                "sender": sender,
                "date": date,
                "body": body if include_body else "",
                "has_attachments": False
            }
            emails.append(email_resp)

    return emails


def mark_email_read_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for marking an email as read"""
    email_id = request.get("email_id")
    if not email_id:
        return {"success": False, "error": "email_id is required"}

    vault_path = Path("AI_Employee_Vault")  # Default path
    inbox_path = vault_path / "Inbox"
    done_path = vault_path / "Done"
    done_path.mkdir(parents=True, exist_ok=True)

    email_file = inbox_path / f"{email_id}.md"
    if email_file.exists():
        # Move the email file to Done folder
        destination = done_path / email_file.name
        email_file.rename(destination)

        return {"success": True, "message": f"Email {email_id} marked as read and moved to Done"}
    else:
        return {"success": False, "error": f"Email {email_id} not found"}


class EmailWatcherMCP:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.fastmcp = FastMCP("Email Watcher MCP Server")

        # Register tools
        from fastmcp.tools import Tool

        # Create tool instances with proper parameters
        check_emails_tool = Tool(
            name="check_emails",
            description="Check for new emails in the configured Gmail account",
            parameters=EmailCheckRequest.model_json_schema()
        )

        mark_email_read_tool = Tool(
            name="mark_email_read",
            description="Mark an email as read",
            parameters={
                "type": "object",
                "properties": {
                    "email_id": {"type": "string", "description": "The ID of the email to mark as read"}
                },
                "required": ["email_id"]
            }
        )

        # Add tools to the FastMCP instance with handlers
        self.fastmcp.add_tool(check_emails_tool)
        self.fastmcp.add_tool(mark_email_read_tool)

    async def check_emails(self, request: EmailCheckRequest) -> List[EmailResponse]:
        """Check for emails and return formatted results"""
        try:
            print(f"Checking emails (max: {request.max_emails}, unread: {request.unread_only})")

            emails = []

            # Look for any email files in the Inbox that were created by GmailWatcher
            inbox_path = self.vault_path / "Inbox"
            if inbox_path.exists():
                email_files = list(inbox_path.glob("EMAIL_*.md"))

                for email_file in email_files[:request.max_emails]:
                    with open(email_file, 'r', encoding='utf-8') as f:
                        content = f.read()

                    # Extract information from the email file
                    lines = content.split('\n')
                    subject = "Unknown Subject"
                    sender = "Unknown Sender"
                    date = "Unknown Date"
                    body = ""

                    # Parse YAML frontmatter and content
                    in_frontmatter = False
                    for i, line in enumerate(lines):
                        if line.strip() == '---':
                            if not in_frontmatter:
                                in_frontmatter = True  # Start of frontmatter
                            else:
                                in_frontmatter = False  # End of frontmatter
                                body = '\n'.join(lines[i+1:]).strip()  # Content after frontmatter
                                break
                        elif in_frontmatter:
                            if line.startswith('subject:'):
                                subject = line.split(':', 1)[1].strip().strip('"\'')
                            elif line.startswith('from:'):
                                sender = line.split(':', 1)[1].strip().strip('"\'')
                            elif line.startswith('date:'):
                                date = line.split(':', 1)[1].strip().strip('"\'')

                    if not in_frontmatter:  # If frontmatter was not closed, get entire content as body
                        body = content

                    email_resp = EmailResponse(
                        id=email_file.stem,
                        threadId=email_file.stem,
                        subject=subject,
                        sender=sender,
                        date=date,
                        body=body if request.include_body else "",
                        has_attachments=False
                    )
                    emails.append(email_resp)

            return emails

        except Exception as e:
            print(f"Error checking emails: {e}")
            import traceback
            traceback.print_exc()
            return []

    async def mark_email_read(self, request: Dict[str, str]) -> Dict[str, Any]:
        """Mark an email as read by moving it from Inbox to Done folder"""
        try:
            email_id = request.get("email_id")
            if not email_id:
                return {"success": False, "error": "email_id is required"}

            inbox_path = self.vault_path / "Inbox"
            done_path = self.vault_path / "Done"
            done_path.mkdir(parents=True, exist_ok=True)

            email_file = inbox_path / f"{email_id}.md"
            if email_file.exists():
                # Move the email file to Done folder
                destination = done_path / email_file.name
                email_file.rename(destination)

                return {"success": True, "message": f"Email {email_id} marked as read and moved to Done"}
            else:
                return {"success": False, "error": f"Email {email_id} not found"}

        except Exception as e:
            return {"success": False, "error": str(e)}

    def serve(self, host: str = "localhost", port: int = 8000):
        """Start the MCP server"""
        return self.fastmcp.run(transport="stdio", show_banner=False)


def main():
    import argparse

    parser = argparse.ArgumentParser(description="Email Watcher MCP Server")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8000, help="Port to bind to")

    args = parser.parse_args()

    server = EmailWatcherMCP(vault_path=args.vault_path)

    print(f"Starting Email Watcher MCP Server on {args.host}:{args.port}")
    print(f"Vault path: {args.vault_path}")

    server.serve(host=args.host, port=args.port)


if __name__ == "__main__":
    main()