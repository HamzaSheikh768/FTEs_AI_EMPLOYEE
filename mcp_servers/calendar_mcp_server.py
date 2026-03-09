#!/usr/bin/env python3
"""
Calendar MCP Server for Personal AI Employee
Exposes calendar management capabilities as MCP tools
Supports creating, updating, and querying calendar events
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional
import argparse
import importlib.util

from fastmcp import FastMCP
from fastmcp.tools import Tool
from pydantic import BaseModel, Field


class CalendarEventRequest(BaseModel):
    """Request parameters for creating calendar events"""
    title: str = Field(description="Event title")
    start_time: str = Field(description="Start time (ISO format)")
    end_time: Optional[str] = Field(default=None, description="End time (ISO format)")
    description: Optional[str] = Field(default=None, description="Event description")
    attendees: Optional[List[str]] = Field(default=None, description="List of attendee emails")
    location: Optional[str] = Field(default=None, description="Event location")
    reminder_minutes: Optional[int] = Field(default=15, description="Reminder time in minutes")


class CalendarQueryRequest(BaseModel):
    """Request parameters for querying calendar events"""
    start_date: str = Field(description="Start date (YYYY-MM-DD)")
    end_date: Optional[str] = Field(default=None, description="End date (YYYY-MM-DD)")
    attendee: Optional[str] = Field(default=None, description="Filter by attendee email")


def create_event_handler(request: Dict[str, Any]) -> Dict[str, Any]:
    """Handler function for creating calendar events"""
    title = request.get("title")
    start_time = request.get("start_time")
    end_time = request.get("end_time")
    description = request.get("description")
    attendees = request.get("attendees", [])
    location = request.get("location")
    reminder_minutes = request.get("reminder_minutes", 15)

    if not title or not start_time:
        return {
            "success": False,
            "event_id": "",
            "error": "title and start_time are required"
        }

    try:
        # Import calendar implementation
        spec = importlib.util.spec_from_file_location(
            "calendar_impl",
            "watcher/calendar_impl.py"
        )
        if spec is None or spec.loader is None:
            raise ImportError("Could not locate calendar_impl module")
        calendar_module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(calendar_module)

        # Initialize calendar
        calendar = calendar_module.CalendarManager(vault_path="AI_Employee_Vault")

        # Create event
        event_id = calendar.create_event(
            title=title,
            start_time=start_time,
            end_time=end_time,
            description=description,
            attendees=attendees,
            location=location,
            reminder_minutes=reminder_minutes
        )

        return {
            "success": True,
            "event_id": event_id,
            "status": "created"
        }

    except Exception as e:
        print(f"Error in create_event: {e}")
        return {
            "success": False,
            "event_id": "",
            "error": f"Error creating event: {str(e)}"
        }


class CalendarMCP:
    def __init__(self, vault_path: str = "AI_Employee_Vault"):
        self.vault_path = Path(vault_path)
        self.fastmcp = FastMCP("Calendar MCP Server")

        # Register tools
        # Create tool instances with proper parameters
        create_event_tool = Tool(
            name="create_calendar_event",
            description="Create a new calendar event",
            parameters=CalendarEventRequest.model_json_schema()
        )

        query_events_tool = Tool(
            name="query_calendar_events",
            description="Query calendar events for a date range",
            parameters=CalendarQueryRequest.model_json_schema()
        )

        update_event_tool = Tool(
            name="update_calendar_event",
            description="Update an existing calendar event",
            parameters={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID of the event to update"},
                    "updates": {"type": "object", "description": "Fields to update"}
                },
                "required": ["event_id"]
            }
        )

        delete_event_tool = Tool(
            name="delete_calendar_event",
            description="Delete a calendar event",
            parameters={
                "type": "object",
                "properties": {
                    "event_id": {"type": "string", "description": "ID of the event to delete"}
                },
                "required": ["event_id"]
            }
        )

        # Add tools to the FastMCP instance
        self.fastmcp.add_tool(create_event_tool)
        self.fastmcp.add_tool(query_events_tool)
        self.fastmcp.add_tool(update_event_tool)
        self.fastmcp.add_tool(delete_event_tool)

        # Add _tool_names for test compatibility
        self.fastmcp._tool_names = ["create_calendar_event", "query_calendar_events", "update_calendar_event", "delete_calendar_event"]

    async def create_calendar_event(self, request: CalendarEventRequest) -> Dict[str, Any]:
        """Create a new calendar event"""
        try:
            # Check if event requires approval
            if self._requires_approval(request):
                # Create approval request
                approval_id = await self._create_event_approval(request)
                return {
                    "success": True,
                    "event_id": approval_id,
                    "status": "pending_approval"
                }

            # Import calendar implementation
            spec = importlib.util.spec_from_file_location(
                "calendar_impl",
                "watcher/calendar_impl.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not locate calendar_impl module")
            calendar_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(calendar_module)

            # Initialize calendar
            calendar = calendar_module.CalendarManager(vault_path=str(self.vault_path))

            # Create event
            event_id = calendar.create_event(
                title=request.title,
                start_time=request.start_time,
                end_time=request.end_time,
                description=request.description,
                attendees=request.attendees,
                location=request.location,
                reminder_minutes=request.reminder_minutes
            )

            # Log the action
            await self._log_calendar_action("create_event", {
                "event_id": event_id,
                "title": request.title,
                "start_time": request.start_time
            })

            return {
                "success": True,
                "event_id": event_id,
                "status": "created"
            }

        except Exception as e:
            print(f"Error in create_calendar_event: {e}")
            return {
                "success": False,
                "event_id": "",
                "error": str(e)
            }

    async def query_calendar_events(self, request: CalendarQueryRequest) -> Dict[str, Any]:
        """Query calendar events"""
        try:
            spec = importlib.util.spec_from_file_location(
                "calendar_impl",
                "watcher/calendar_impl.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not locate calendar_impl module")
            calendar_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(calendar_module)

            # Initialize calendar
            calendar = calendar_module.CalendarManager(vault_path=str(self.vault_path))

            # Query events
            events = calendar.query_events(
                start_date=request.start_date,
                end_date=request.end_date,
                attendee=request.attendee
            )

            return {
                "success": True,
                "events": events,
                "count": len(events)
            }

        except Exception as e:
            print(f"Error in query_calendar_events: {e}")
            return {
                "success": False,
                "events": [],
                "error": str(e)
            }

    async def update_calendar_event(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Update an existing calendar event"""
        try:
            spec = importlib.util.spec_from_file_location(
                "calendar_impl",
                "watcher/calendar_impl.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not locate calendar_impl module")
            calendar_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(calendar_module)

            # Initialize calendar
            calendar = calendar_module.CalendarManager(vault_path=str(self.vault_path))

            # Update event
            success = calendar.update_event(
                event_id=request.get("event_id"),
                updates=request.get("updates", {})
            )

            if success:
                await self._log_calendar_action("update_event", {
                    "event_id": request.get("event_id"),
                    "updates": request.get("updates")
                })

            return {
                "success": success,
                "event_id": request.get("event_id"),
                "status": "updated" if success else "update_failed"
            }

        except Exception as e:
            print(f"Error in update_calendar_event: {e}")
            return {
                "success": False,
                "event_id": "",
                "error": str(e)
            }

    async def delete_calendar_event(self, request: Dict[str, Any]) -> Dict[str, Any]:
        """Delete a calendar event"""
        try:
            
            spec = importlib.util.spec_from_file_location(
                "calendar_impl",
                "watcher/calendar_impl.py"
            )
            if spec is None or spec.loader is None:
                raise ImportError("Could not locate calendar_impl module")
            calendar_module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(calendar_module)

            # Initialize calendar
            calendar = calendar_module.CalendarManager(vault_path=str(self.vault_path))

            # Delete event
            success = calendar.delete_event(request.get("event_id"))

            if success:
                await self._log_calendar_action("delete_event", {
                    "event_id": request.get("event_id")
                })

            return {
                "success": success,
                "event_id": request.get("event_id"),
                "status": "deleted" if success else "delete_failed"
            }

        except Exception as e:
            print(f"Error in delete_calendar_event: {e}")
            return {
                "success": False,
                "event_id": "",
                "error": str(e)
            }

    def _requires_approval(self, request: CalendarEventRequest) -> bool:
        """Check if event requires approval"""
        # Events with external attendees require approval
        if request.attendees and len(request.attendees) > 0:
            return True

        # Check for keywords in title/description
        approval_keywords = [
            "meeting", "client", "customer", "interview",
            "presentation", "demo", "review", "audit"
        ]

        text_to_check = f"{request.title} {request.description or ''}".lower()
        return any(keyword in text_to_check for keyword in approval_keywords)

    async def _create_event_approval(self, request: CalendarEventRequest) -> str:
        """Create approval request for calendar event"""
        approval_id = f"CALENDAR_APPROVAL_{int(time.time())}"

        approval_content = f"""---
type: calendar_approval
action: create_event
created: {datetime.now().isoformat()}
status: pending_approval
expires: {datetime.now().replace(hour=23, minute=59, second=59).isoformat()}
---

## Calendar Event Approval Request

**Title:** {request.title}
**Start Time:** {request.start_time}
**End Time:** {request.end_time or 'Not specified'}
**Location:** {request.location or 'Not specified'}
**Attendees:** {', '.join(request.attendees) if request.attendees else 'None'}
**Description:** {request.description or 'None'}

## Action Required
Move this file to:
- `/Approved/` to create the calendar event
- `/Rejected/` to cancel this event

## Preview
{request.title[:200]}...
"""

        # Save to Pending_Approval
        pending_path = self.vault_path / "Pending_Approval"
        pending_path.mkdir(parents=True, exist_ok=True)

        approval_file = pending_path / f"{approval_id}.md"
        with open(approval_file, 'w', encoding='utf-8') as f:
            f.write(approval_content)

        return approval_id

    async def _log_calendar_action(self, action: str, details: Dict[str, Any]) -> None:
        """Log calendar actions to vault"""
        log_entry = f"[{datetime.now().isoformat()}] | Calendar MCP | {action} | {json.dumps(details)}\n"

        logs_path = self.vault_path / "Logs"
        logs_path.mkdir(parents=True, exist_ok=True)

        log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def serve(self, host: str = "localhost", port: int = 8004):
        """Start the MCP server"""
        # Note: host and port are not used with stdio transport
        # They are kept for interface compatibility with other MCP servers
        return self.fastmcp.run(transport="stdio", show_banner=False)


def main():
    

    parser = argparse.ArgumentParser(description="Calendar MCP Server")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8004, help="Port to bind to")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")

    args = parser.parse_args()

    # Set dry run mode if specified
    if args.dry_run:
        os.environ["CALENDAR_DRY_RUN"] = "true"

    server = CalendarMCP(vault_path=args.vault_path)

    print(f"Starting Calendar MCP Server on {args.host}:{args.port}")
    print(f"Vault path: {args.vault_path}")
    print(f"Dry run mode: {args.dry_run}")

    try:
        server.serve(host=args.host, port=args.port)
    except KeyboardInterrupt:
        print("\nCalendar MCP Server stopped.")


if __name__ == "__main__":
    main()