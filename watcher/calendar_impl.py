#!/usr/bin/env python3
"""
Calendar Implementation for Personal AI Employee
Manages calendar events and scheduling
"""

import os
import json
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional


class CalendarManager:
    def __init__(self, vault_path="AI_Employee_Vault"):
        """
        Initialize Calendar Manager

        Args:
            vault_path (str): Path to the AI Employee vault
        """
        self.vault_path = Path(vault_path)
        self.calendar_path = self.vault_path / "Calendar"
        self.events_file = self.calendar_path / "events.json"

        # Create calendar directory
        self.calendar_path.mkdir(parents=True, exist_ok=True)

        # Initialize events file if it doesn't exist
        if not self.events_file.exists():
            self._initialize_events_file()

    def _initialize_events_file(self):
        """Initialize the events JSON file"""
        initial_data = {
            "events": [],
            "last_updated": datetime.now().isoformat()
        }
        with open(self.events_file, 'w', encoding='utf-8') as f:
            json.dump(initial_data, f, indent=2)

    def _load_events(self) -> Dict[str, Any]:
        """Load events from JSON file"""
        try:
            with open(self.events_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Error loading events: {e}")
            return {"events": []}

    def _save_events(self, data: Dict[str, Any]):
        """Save events to JSON file"""
        try:
            data["last_updated"] = datetime.now().isoformat()
            with open(self.events_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving events: {e}")

    def create_event(self, title: str, start_time: str, end_time: Optional[str] = None,
                    description: Optional[str] = None, attendees: Optional[List[str]] = None,
                    location: Optional[str] = None, reminder_minutes: int = 15) -> str:
        """
        Create a new calendar event

        Args:
            title (str): Event title
            start_time (str): Start time in ISO format
            end_time (str): End time in ISO format
            description (str): Event description
            attendees (List[str]): List of attendee emails
            location (str): Event location
            reminder_minutes (int): Reminder time in minutes

        Returns:
            str: Event ID
        """
        # Check for dry run mode
        if os.getenv("CALENDAR_DRY_RUN", "false").lower() == "true":
            event_id = f"DRY_RUN_{int(datetime.now().timestamp())}"
            print(f"[DRY RUN] Would create event: {title} at {start_time}")
            return event_id

        # Generate event ID
        event_id = f"EVENT_{int(datetime.now().timestamp())}"

        # Parse start time
        try:
            start_dt = datetime.fromisoformat(start_time.replace('Z', '+00:00'))
        except:
            start_dt = datetime.now()

        # Set end time if not provided (default 1 hour)
        if not end_time:
            end_dt = start_dt + timedelta(hours=1)
        else:
            try:
                end_dt = datetime.fromisoformat(end_time.replace('Z', '+00:00'))
            except:
                end_dt = start_dt + timedelta(hours=1)

        # Create event object
        event = {
            "id": event_id,
            "title": title,
            "start_time": start_dt.isoformat(),
            "end_time": end_dt.isoformat(),
            "description": description or "",
            "attendees": attendees or [],
            "location": location or "",
            "reminder_minutes": reminder_minutes,
            "created_at": datetime.now().isoformat(),
            "updated_at": datetime.now().isoformat(),
            "status": "scheduled"
        }

        # Load existing events
        data = self._load_events()

        # Add new event
        data["events"].append(event)

        # Save events
        self._save_events(data)

        # Create event file in vault
        self._create_event_file(event)

        print(f"Created calendar event: {event_id}")
        return event_id

    def _create_event_file(self, event: Dict[str, Any]):
        """Create a markdown file for the event"""
        event_file = self.calendar_path / f"{event['id']}.md"

        content = f"""---
type: calendar_event
id: {event['id']}
title: {event['title']}
start_time: {event['start_time']}
end_time: {event['end_time']}
location: {event['location']}
status: {event['status']}
created: {event['created_at']}
---

# {event['title']}

**Start:** {self._format_datetime(event['start_time'])}
**End:** {self._format_datetime(event['end_time'])}
**Location:** {event['location'] or 'TBD'}

## Description
{event['description'] or 'No description provided'}

## Attendees
{chr(10).join(f"- {attendee}" for attendee in event['attendees']) if event['attendees'] else 'No attendees'}

## Reminder
{event['reminder_minutes']} minutes before event

---

*Created by AI Employee*
"""

        with open(event_file, 'w', encoding='utf-8') as f:
            f.write(content)

    def _format_datetime(self, iso_string: str) -> str:
        """Format ISO datetime string for display"""
        try:
            dt = datetime.fromisoformat(iso_string.replace('Z', '+00:00'))
            return dt.strftime("%Y-%m-%d %H:%M")
        except:
            return iso_string

    def query_events(self, start_date: str, end_date: Optional[str] = None,
                    attendee: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Query calendar events

        Args:
            start_date (str): Start date in YYYY-MM-DD format
            end_date (str): End date in YYYY-MM-DD format
            attendee (str): Filter by attendee email

        Returns:
            List[Dict[str, Any]]: List of events
        """
        data = self._load_events()
        events = data.get("events", [])

        # Parse start date
        try:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d")
        except:
            start_dt = datetime.now()

        # Parse end date
        if end_date:
            try:
                end_dt = datetime.strptime(end_date, "%Y-%m-%d")
                end_dt = end_dt + timedelta(days=1)  # Include end date
            except:
                end_dt = start_dt + timedelta(days=30)  # Default 30 days
        else:
            end_dt = start_dt + timedelta(days=30)

        # Filter events
        filtered_events = []
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))

                # Check date range
                if start_dt <= event_start < end_dt:
                    # Check attendee filter
                    if not attendee or attendee in event.get('attendees', []):
                        filtered_events.append(event)
            except:
                continue

        # Sort by start time
        filtered_events.sort(key=lambda x: x.get('start_time', ''))

        return filtered_events

    def update_event(self, event_id: str, updates: Dict[str, Any]) -> bool:
        """
        Update an existing event

        Args:
            event_id (str): Event ID
            updates (Dict[str, Any]): Fields to update

        Returns:
            bool: Success status
        """
        data = self._load_events()
        events = data.get("events", [])

        # Find the event
        for i, event in enumerate(events):
            if event.get('id') == event_id:
                # Update the event
                updated_event = {**event, **updates}
                updated_event['updated_at'] = datetime.now().isoformat()
                events[i] = updated_event

                # Save events
                data['events'] = events
                self._save_events(data)

                # Update event file
                self._create_event_file(updated_event)

                print(f"Updated event: {event_id}")
                return True

        print(f"Event not found: {event_id}")
        return False

    def delete_event(self, event_id: str) -> bool:
        """
        Delete an event

        Args:
            event_id (str): Event ID

        Returns:
            bool: Success status
        """
        data = self._load_events()
        events = data.get("events", [])

        # Find and remove the event
        original_length = len(events)
        events = [event for event in events if event.get('id') != event_id]

        if len(events) < original_length:
            # Save events
            data['events'] = events
            self._save_events(data)

            # Delete event file
            event_file = self.calendar_path / f"{event_id}.md"
            if event_file.exists():
                event_file.unlink()

            print(f"Deleted event: {event_id}")
            return True

        print(f"Event not found: {event_id}")
        return False

    def get_upcoming_events(self, days: int = 7) -> List[Dict[str, Any]]:
        """Get upcoming events for the next N days"""
        start_date = datetime.now().strftime("%Y-%m-%d")
        end_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
        return self.query_events(start_date, end_date)

    def get_events_for_today(self) -> List[Dict[str, Any]]:
        """Get events for today"""
        today = datetime.now().strftime("%Y-%m-%d")
        return self.query_events(today, today)

    def check_reminders(self) -> List[Dict[str, Any]]:
        """Check for events that need reminders"""
        now = datetime.now()
        events = self._load_events().get("events", [])

        reminder_events = []
        for event in events:
            try:
                event_start = datetime.fromisoformat(event['start_time'].replace('Z', '+00:00'))
                reminder_time = event_start - timedelta(minutes=event.get('reminder_minutes', 15))

                # Check if reminder time is within the last 5 minutes
                if now >= reminder_time and now < reminder_time + timedelta(minutes=5):
                    reminder_events.append(event)
            except:
                continue

        return reminder_events

    def create_daily_schedule(self) -> str:
        """Create a daily schedule file"""
        today_events = self.get_events_for_today()
        date_str = datetime.now().strftime("%Y-%m-%d")

        schedule_content = f"""# Daily Schedule - {date_str}

## Events ({len(today_events)})

"""

        if today_events:
            for event in today_events:
                start_str = self._format_datetime(event['start_time'])
                end_str = self._format_datetime(event['end_time'])
                schedule_content += f"""### {event['title']}
- **Time:** {start_str} - {end_str}
- **Location:** {event.get('location', 'TBD')}
- **Attendees:** {', '.join(event.get('attendees', [])) or 'None'}

{event.get('description', 'No description')}

---
"""
        else:
            schedule_content += "No events scheduled for today.\n"

        # Save schedule file
        schedule_file = self.calendar_path / f"schedule_{date_str}.md"
        with open(schedule_file, 'w', encoding='utf-8') as f:
            f.write(schedule_content)

        return str(schedule_file)


def main():
    """Main function for testing calendar functionality"""
    import argparse

    parser = argparse.ArgumentParser(description="Calendar Manager for Personal AI Employee")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--create-event", action="store_true", help="Create a test event")
    parser.add_argument("--query", help="Query events from date (YYYY-MM-DD)")
    parser.add_argument("--upcoming", type=int, help="Get upcoming events for N days")
    parser.add_argument("--today", action="store_true", help="Get today's events")
    parser.add_argument("--schedule", action="store_true", help="Create daily schedule")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")

    args = parser.parse_args()

    calendar = CalendarManager(vault_path=args.vault_path)

    # Set dry run mode
    if args.dry_run:
        os.environ["CALENDAR_DRY_RUN"] = "true"

    if args.create_event:
        # Create a test event
        start_time = (datetime.now() + timedelta(hours=2)).isoformat()
        end_time = (datetime.now() + timedelta(hours=3)).isoformat()

        event_id = calendar.create_event(
            title="Test Meeting",
            start_time=start_time,
            end_time=end_time,
            description="This is a test meeting created by the AI Employee",
            attendees=["test@example.com"],
            location="Conference Room A",
            reminder_minutes=30
        )
        print(f"Created test event: {event_id}")

    elif args.query:
        # Query events
        events = calendar.query_events(args.query)
        print(f"Found {len(events)} events from {args.query}:")
        for event in events:
            print(f"  - {event['title']} at {event['start_time']}")

    elif args.upcoming:
        # Get upcoming events
        events = calendar.get_upcoming_events(args.upcoming)
        print(f"Found {len(events)} events in the next {args.upcoming} days:")
        for event in events:
            print(f"  - {event['title']} on {event['start_time']}")

    elif args.today:
        # Get today's events
        events = calendar.get_events_for_today()
        print(f"Found {len(events)} events for today:")
        for event in events:
            print(f"  - {event['title']} at {event['start_time']}")

    elif args.schedule:
        # Create daily schedule
        schedule_file = calendar.create_daily_schedule()
        print(f"Created daily schedule: {schedule_file}")

    else:
        print("No action specified. Use --create-event, --query, --upcoming, --today, or --schedule")


if __name__ == "__main__":
    main()