#!/usr/bin/env python3
"""
WhatsApp Watcher Implementation for Personal AI Employee
Handles WhatsApp Web automation for monitoring and messaging
"""

import os
import time
import json
from pathlib import Path
from datetime import datetime
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from typing import List, Dict, Any, Optional


class WhatsAppWatcher:
    def __init__(self, vault_path="AI_Employee_Vault", session_path=None):
        """
        Initialize the WhatsApp Watcher

        Args:
            vault_path (str): Path to the AI Employee vault
            session_path (str): Path to WhatsApp session storage
        """
        self.vault_path = Path(vault_path)
        self.session_path = Path(session_path) if session_path else Path(".whatsapp_session")
        self.inbox_path = self.vault_path / "Inbox"
        self.browser = None
        self.page = None

        # Create necessary directories
        self.inbox_path.mkdir(parents=True, exist_ok=True)
        self.session_path.mkdir(parents=True, exist_ok=True)

        # Keywords for message filtering
        self.urgent_keywords = [
            'urgent', 'asap', 'emergency', 'immediate', 'critical',
            'payment', 'invoice', 'deadline', 'meeting', 'important'
        ]

    def setup_browser(self, headless=True):
        """Setup Playwright browser instance with WhatsApp session"""
        try:
            playwright = sync_playwright().start()

            # Launch browser with persistent context for session
            self.browser = playwright.chromium.launch_persistent_context(
                user_data_dir=str(self.session_path),
                headless=headless,
                viewport={'width': 1280, 'height': 800},
                args=[
                    '--no-sandbox',
                    '--disable-setuid-sandbox',
                    '--disable-dev-shm-usage',
                    '--disable-accelerated-2d-canvas',
                    '--no-first-run',
                    '--no-zygote',
                    '--disable-gpu'
                ]
            )

            # Get or create page
            if self.browser.pages:
                self.page = self.browser.pages[0]
            else:
                self.page = self.browser.new_page()

            # Set up basic browser context
            self.page.set_default_timeout(30000)  # 30 second timeout

            print("Browser setup successful")
            return True
        except Exception as e:
            print(f"Error setting up browser: {e}")
            return False

    def login_to_whatsapp(self):
        """Navigate to WhatsApp Web and wait for login"""
        try:
            # Navigate to WhatsApp Web
            self.page.goto("https://web.whatsapp.com")

            # Wait for either QR code or main interface
            try:
                # Check if already logged in (main interface visible)
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=5000)
                print("Already logged in to WhatsApp")
                return True
            except PlaywrightTimeoutError:
                # QR code is shown, need to scan
                print("Please scan the QR code to log in to WhatsApp")
                self.page.wait_for_selector('[data-testid="chat-list"]', timeout=120000)
                print("Successfully logged in to WhatsApp")
                return True

        except PlaywrightTimeoutError:
            print("Login timeout - please check your connection and try again")
            return False
        except Exception as e:
            print(f"Error during WhatsApp login: {e}")
            return False

    def check_unread_messages(self) -> List[Dict[str, Any]]:
        """Check for unread messages and return them"""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call setup_browser() first.")

        try:
            # Navigate to WhatsApp if not already there
            if "web.whatsapp.com" not in self.page.url:
                self.page.goto("https://web.whatsapp.com")

            # Wait for chat list to load
            self.page.wait_for_selector('[data-testid="chat-list"]', timeout=10000)

            # Find unread messages
            unread_chats = self.page.query_selector_all('[data-testid="chat"]')
            messages = []

            for chat in unread_chats:
                try:
                    # Check if chat has unread indicator
                    unread_indicator = chat.query_selector('[data-testid="unread-count"]')
                    if unread_indicator:
                        # Get chat info
                        contact_name = self._extract_contact_name(chat)
                        last_message = self._extract_last_message(chat)
                        timestamp = self._extract_timestamp(chat)

                        messages.append({
                            'contact': contact_name,
                            'text': last_message,
                            'timestamp': timestamp,
                            'unread_count': unread_indicator.inner_text().strip()
                        })

                except Exception as e:
                    print(f"Error processing chat: {e}")
                    continue

            return messages

        except PlaywrightTimeoutError:
            print("Timeout while checking messages")
            return []
        except Exception as e:
            print(f"Error checking unread messages: {e}")
            return []

    def send_message(self, recipient: str, message: str, attachment_path: Optional[str] = None) -> bool:
        """Send a WhatsApp message to a contact"""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call setup_browser() first.")

        try:
            # Check for dry run mode
            if os.getenv("WHATSAPP_DRY_RUN", "false").lower() == "true":
                print(f"[DRY RUN] Would send WhatsApp message to {recipient}: {message}")
                return True

            # Navigate to WhatsApp if not already there
            if "web.whatsapp.com" not in self.page.url:
                self.page.goto("https://web.whatsapp.com")

            # Search for contact
            search_box = self.page.wait_for_selector('[data-testid="chat-list-search"]')
            search_box.fill(recipient)
            time.sleep(2)  # Wait for search results

            # Click on the contact
            contact_selectors = [
                f'[title="{recipient}"]',
                '[data-testid="contact"]'
            ]

            contact_found = False
            for selector in contact_selectors:
                try:
                    contact = self.page.wait_for_selector(selector, timeout=5000)
                    contact.click()
                    contact_found = True
                    break
                except:
                    continue

            if not contact_found:
                print(f"Contact not found: {recipient}")
                return False

            # Wait for chat to open
            self.page.wait_for_selector('[data-testid="conversation-panel-messages"]', timeout=5000)

            # Type and send message
            message_box = self.page.wait_for_selector('[data-testid="conversation-panel-compose-input"]')
            message_box.fill(message)

            # Add attachment if provided
            if attachment_path and Path(attachment_path).exists():
                attachment_button = self.page.query_selector('[data-testid="compose-attach-button"]')
                if attachment_button:
                    attachment_button.click()
                    # Handle file upload dialog
                    # Note: This might need additional implementation based on WhatsApp's UI

            # Send the message
            send_button = self.page.wait_for_selector('[data-testid="compose-send-button"]')
            send_button.click()

            # Wait for message to be sent
            time.sleep(2)

            print(f"Message sent to {recipient}")
            return True

        except PlaywrightTimeoutError:
            print("Timeout while sending message")
            return False
        except Exception as e:
            print(f"Error sending message: {e}")
            return False

    def search_contacts(self, query: str) -> List[Dict[str, Any]]:
        """Search for WhatsApp contacts"""
        if not self.page:
            raise RuntimeError("Browser not initialized. Call setup_browser() first.")

        try:
            # Navigate to WhatsApp if not already there
            if "web.whatsapp.com" not in self.page.url:
                self.page.goto("https://web.whatsapp.com")

            # Use search box
            search_box = self.page.wait_for_selector('[data-testid="chat-list-search"]')
            search_box.fill(query)
            time.sleep(2)

            # Get search results
            contacts = []
            contact_elements = self.page.query_selector_all('[data-testid="contact"]')

            for element in contact_elements[:10]:  # Limit to 10 results
                try:
                    name = self._extract_contact_name(element)
                    phone = self._extract_phone_number(element)
                    last_seen = self._extract_last_seen(element)
                    is_online = self._check_online_status(element)

                    contacts.append({
                        'name': name,
                        'phone': phone,
                        'last_seen': last_seen,
                        'is_online': is_online
                    })
                except:
                    continue

            # Clear search
            search_box.fill("")

            return contacts

        except Exception as e:
            print(f"Error searching contacts: {e}")
            return []

    def _extract_contact_name(self, element) -> str:
        """Extract contact name from chat element"""
        try:
            name_element = element.query_selector('[data-testid="chat-title"]')
            return name_element.inner_text().strip() if name_element else "Unknown"
        except:
            return "Unknown"

    def _extract_last_message(self, element) -> str:
        """Extract last message from chat element"""
        try:
            message_element = element.query_selector('[data-testid="last-message"]')
            return message_element.inner_text().strip() if message_element else ""
        except:
            return ""

    def _extract_timestamp(self, element) -> str:
        """Extract timestamp from chat element"""
        try:
            timestamp_element = element.query_selector('[data-testid="chat-timestamp"]')
            return timestamp_element.inner_text().strip() if timestamp_element else ""
        except:
            return ""

    def _extract_phone_number(self, element) -> str:
        """Extract phone number from contact element"""
        # This would need to be implemented based on WhatsApp's UI
        # For now, return empty string
        return ""

    def _extract_last_seen(self, element) -> Optional[str]:
        """Extract last seen status from contact element"""
        try:
            last_seen_element = element.query_selector('[data-testid="last-seen"]')
            return last_seen_element.inner_text().strip() if last_seen_element else None
        except:
            return None

    def _check_online_status(self, element) -> bool:
        """Check if contact is online"""
        try:
            online_indicator = element.query_selector('[data-testid="online-indicator"]')
            return online_indicator is not None
        except:
            return False

    def monitor_messages(self, interval=30):
        """Continuously monitor for new messages"""
        print(f"Starting WhatsApp message monitoring (check interval: {interval}s)")

        processed_messages = set()

        try:
            while True:
                unread_messages = self.check_unread_messages()

                for message in unread_messages:
                    message_key = f"{message['contact']}_{message['timestamp']}"

                    if message_key not in processed_messages:
                        # Check if message is urgent
                        is_urgent = any(keyword in message['text'].lower()
                                      for keyword in self.urgent_keywords)

                        if is_urgent:
                            # Create urgent action file
                            self._create_urgent_action_file(message)

                        # Log the message
                        self._log_message(message)
                        processed_messages.add(message_key)

                time.sleep(interval)

        except KeyboardInterrupt:
            print("Message monitoring stopped by user")
        except Exception as e:
            print(f"Error in monitoring loop: {e}")
            raise

    def _create_urgent_action_file(self, message: Dict[str, Any]):
        """Create an action file for urgent messages"""
        action_id = f"WHATSAPP_URGENT_{int(time.time())}"

        action_content = f"""---
type: whatsapp_message
from: {message.get('contact', 'Unknown')}
received: {datetime.now().isoformat()}
priority: high
status: pending
---

## Urgent WhatsApp Message

**From:** {message.get('contact', 'Unknown')}
**Time:** {message.get('timestamp', 'Unknown')}
**Message:** {message.get('text', '')}

## Suggested Actions
- [ ] Reply to sender
- [ ] Forward to relevant party
- [ ] Create follow-up task
"""

        action_file = self.inbox_path / f"{action_id}.md"
        with open(action_file, 'w', encoding='utf-8') as f:
            f.write(action_content)

        print(f"Created urgent action file: {action_file.name}")

    def _log_message(self, message: Dict[str, Any]):
        """Log message to vault logs"""
        log_entry = f"[{datetime.now().isoformat()}] WhatsApp | {message.get('contact', 'Unknown')} | {message.get('text', '')[:50]}...\n"

        logs_path = self.vault_path / "Logs"
        logs_path.mkdir(parents=True, exist_ok=True)

        log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"
        with open(log_file, 'a', encoding='utf-8') as f:
            f.write(log_entry)

    def close(self):
        """Close the browser instance"""
        if self.browser:
            self.browser.close()
            print("Browser closed")


def main():
    """Main function for testing WhatsApp watcher functionality"""
    import argparse

    parser = argparse.ArgumentParser(description="WhatsApp Watcher for Personal AI Employee")
    parser.add_argument("--vault-path", default="AI_Employee_Vault", help="Path to AI Employee vault")
    parser.add_argument("--session-path", default=".whatsapp_session", help="Path to WhatsApp session")
    parser.add_argument("--check-messages", action="store_true", help="Check for unread messages")
    parser.add_argument("--send-message", help="Send a test message")
    parser.add_argument("--recipient", help="Recipient for test message")
    parser.add_argument("--monitor", action="store_true", help="Run in monitoring mode")
    parser.add_argument("--interval", type=int, default=30, help="Monitoring interval in seconds")
    parser.add_argument("--dry-run", action="store_true", help="Log actions without executing")
    parser.add_argument("--headless", action="store_true", help="Run browser in headless mode")

    args = parser.parse_args()

    watcher = WhatsAppWatcher(vault_path=args.vault_path, session_path=args.session_path)

    try:
        # Setup browser
        if not watcher.setup_browser(headless=args.headless):
            print("Failed to setup browser")
            return

        # Login to WhatsApp
        if not watcher.login_to_whatsapp():
            print("Failed to login to WhatsApp")
            return

        if args.check_messages:
            # Check for unread messages
            messages = watcher.check_unread_messages()
            print(f"Found {len(messages)} unread messages:")
            for msg in messages:
                print(f"  - {msg['contact']}: {msg['text'][:50]}...")

        elif args.send_message and args.recipient:
            # Send a test message
            success = watcher.send_message(args.recipient, args.send_message)
            if success:
                print("Message sent successfully")
            else:
                print("Failed to send message")

        elif args.monitor:
            # Run in monitoring mode
            watcher.monitor_messages(interval=args.interval)

        else:
            print("No action specified. Use --check-messages, --send-message, or --monitor")

    finally:
        watcher.close()


if __name__ == "__main__":
    main()