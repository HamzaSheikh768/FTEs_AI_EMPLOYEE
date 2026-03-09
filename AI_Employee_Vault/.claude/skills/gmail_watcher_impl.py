#!/usr/bin/env python3
"""
Gmail Watcher Implementation for Personal AI Employee
Monitors Gmail account for new messages and creates action files in the vault
"""

import time
import os
import json
from pathlib import Path
from datetime import datetime
import base64
import argparse
import pickle

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/gmail.readonly']

class GmailWatcher:
    def __init__(self, vault_path="AI_Employee_Vault", credentials_path=None, token_path=None):
        """
        Initialize the Gmail Watcher

        Args:
            vault_path (str): Path to the AI Employee vault
            credentials_path (str): Path to the credentials JSON file (optional)
            token_path (str): Path to store authentication token (optional)
        """
        self.vault_path = Path(vault_path)
        self.inbox_path = self.vault_path / "Inbox"
        self.credentials_path = credentials_path or os.getenv("GMAIL_CREDENTIALS_PATH")
        self.token_path = token_path or os.getenv("GMAIL_TOKEN_PATH", "token.pickle")

        # Ensure the Inbox directory exists
        self.inbox_path.mkdir(parents=True, exist_ok=True)

        # Initialize Gmail service
        self.service = self._authenticate()

    def _authenticate(self):
        """Authenticate with Gmail API using OAuth2"""
        creds = None

        # The file token.pickle stores the user's access and refresh tokens.
        if os.path.exists(self.token_path):
            with open(self.token_path, 'rb') as token:
                creds = pickle.load(token)

        # If there are no (valid) credentials available, let the user log in.
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                try:
                    creds.refresh(Request())
                except Exception as e:
                    print(f"Token refresh failed: {e}")
                    # If refresh fails, we need to re-authenticate
                    creds = None

            if not creds:
                if not self.credentials_path or not os.path.exists(self.credentials_path):
                    raise FileNotFoundError(
                        f"Credentials file not found: {self.credentials_path}. "
                        "Please set GMAIL_CREDENTIALS_PATH environment variable."
                    )

                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path, SCOPES
                )
                creds = flow.run_local_server(port=0)

            # Save the credentials for the next run
            with open(self.token_path, 'wb') as token:
                pickle.dump(creds, token)

        return build('gmail', 'v1', credentials=creds)

    def decode_email_body(self, message_part):
        """Decode the email body from base64 encoding"""
        body_data = message_part.get('body', {}).get('data', '')
        if body_data:
            return base64.urlsafe_b64decode(body_data).decode('utf-8')
        return ""

    def get_email_content(self, msg_id):
        """Get the full content of an email"""
        try:
            message = self.service.users().messages().get(userId='me', id=msg_id).execute()  # pylint: disable=no-member

            # Extract headers
            headers = {}
            for header in message['payload'].get('headers', []):
                name = header['name'].lower()
                headers[name] = header['value']

            # Extract body content
            body = ""
            if 'parts' in message['payload']:
                # Handle multipart messages
                for part in message['payload']['parts']:
                    if part['mimeType'] == 'text/plain':
                        body = self.decode_email_body(part)
                        break
            else:
                # Handle single part messages
                body = self.decode_email_body(message['payload'])

            return {
                'headers': headers,
                'body': body,
                'snippet': message.get('snippet', ''),
                'labels': message.get('labelIds', []),
                'size': message.get('sizeEstimate', 0),
                'internal_date': message.get('internalDate', '')
            }
        except Exception as e:
            print(f"Error getting email content: {e}")
            return None

    def create_email_file(self, email_data, msg_id):
        """Create an email file in the Inbox with proper formatting"""
        # Determine priority based on labels or subject
        priority = "medium"
        if "IMPORTANT" in email_data['labels'] or "CRITICAL" in email_data['labels']:
            priority = "high"
        elif "Newsletter" in email_data['labels'] or "Promotions" in email_data['labels']:
            priority = "low"

        # Check subject for urgency indicators
        subject = email_data['headers'].get('subject', '')
        if any(urgent_word in subject.upper() for urgent_word in ['URGENT', 'ASAP', 'IMMEDIATE', 'CRITICAL']):
            priority = "high"

        # Create email file content with YAML frontmatter
        email_content = f"""---
type: email
from: {email_data['headers'].get('from', 'Unknown')}
to: {email_data['headers'].get('to', 'Unknown')}
subject: {subject}
received: {datetime.now().isoformat()}
priority: {priority}
status: pending
gmail_id: {msg_id}
labels: {email_data['labels']}
---
## Email Content
{email_data['snippet']}

## Body Preview
{email_data['body'][:500]}...

## Suggested Actions
- [ ] Read full email
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Archive after processing
"""

        # Create the file in the Inbox
        email_filename = f"EMAIL_{msg_id}.md"
        email_file_path = self.inbox_path / email_filename

        with open(email_file_path, 'w', encoding='utf-8') as f:
            f.write(email_content)

        print(f"Created email file: {email_filename}")
        return email_file_path

    def check_new_emails(self, query="is:unread"):
        """
        Check for new emails matching the query

        Args:
            query (str): Gmail search query (default: "is:unread")

        Returns:
            list: List of email IDs that were processed
        """
        try:
            # Get messages matching the query
            results = self.service.users().messages().list(  # pylint: disable=no-member
                userId='me',
                q=query,
                maxResults=10  # Limit to avoid processing too many at once
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                print("No new emails found.")
                return []

            processed_emails = []

            for message in messages:
                msg_id = message['id']

                # Get full email content
                email_data = self.get_email_content(msg_id)

                if email_data:
                    # Create the email file in the Inbox
                    self.create_email_file(email_data, msg_id)
                    processed_emails.append(msg_id)

                    # Mark as read after processing
                    try:
                        self.service.users().messages().modify(  # pylint: disable=no-member
                            userId='me',
                            id=msg_id,
                            body={'removeLabelIds': ['UNREAD']}
                        ).execute()
                        print(f"Marked email {msg_id} as read")
                    except Exception as e:
                        print(f"Could not mark email {msg_id} as read: {e}")

            print(f"Processed {len(processed_emails)} new emails")
            return processed_emails

        except HttpError as error:
            print(f"An error occurred while checking emails: {error}")
            return []

    def run_polling(self, interval=120, query="is:unread"):
        """
        Run the Gmail polling in an infinite loop

        Args:
            interval (int): Polling interval in seconds (default: 120)
            query (str): Gmail search query (default: "is:unread")
        """
        print(f"Starting Gmail polling (checking every {interval}s for {query})...")

        try:
            while True:
                print(f"Checking for new emails at {datetime.now()}")
                self.check_new_emails(query)

                print(f"Waiting {interval} seconds before next check...")
                time.sleep(interval)

        except KeyboardInterrupt:
            print("\nGmail polling stopped by user.")
        except Exception as e:
            print(f"Unexpected error in polling: {e}")

def main():
    """Main function for command-line usage"""

    parser = argparse.ArgumentParser(description="Gmail Watcher for Personal AI Employee")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--credentials-path", help="Path to Gmail credentials JSON file")
    parser.add_argument("--token-path", default="token.pickle", help="Path to store Gmail token")
    parser.add_argument("--query", default="is:unread", help="Gmail search query")
    parser.add_argument("--interval", type=int, default=120, help="Polling interval in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Run without actually polling (for testing)")

    args = parser.parse_args()

    watcher = GmailWatcher(args.vault_path, args.credentials_path, args.token_path)

    if args.dry_run:
        print("DRY RUN: Would check for emails but not actually connect to Gmail")
        # Just validate the authentication would work
        if watcher.service:
            print("Authentication successful, ready to poll emails.")
    else:
        print("Starting Gmail polling...")
        watcher.run_polling(args.interval, args.query)

if __name__ == "__main__":
    main()