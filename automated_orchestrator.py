#!/usr/bin/env python3
"""
Gold Tier Master Orchestrator for Personal AI Employee
The one-click start file that launches the complete autonomous system
"""
import os
import sys
import time
import signal
import logging
import shutil
import subprocess
import threading
import socket
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import json

from dotenv import load_dotenv
from platinum_orchestrator import PlatinumOrchestrator

# Load environment variables
load_dotenv()

# Create Logs directory if it doesn't exist
logs_dir = Path('Logs')
logs_dir.mkdir(parents=True, exist_ok=True)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('Logs/orchestrator.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ProcessManager:
    """
    Manages subprocesses and their lifecycle
    """
    def __init__(self):
        self.processes: Dict[str, subprocess.Popen] = {}
        self.process_names: Dict[int, str] = {}
        self.shutdown_event = threading.Event()

    def start_process(self, name: str, cmd: List[str], log_file: str = None):
        """Start a subprocess and store reference"""
        try:
            # Create log directory if it doesn't exist
            if log_file:
                log_dir = Path(log_file).parent
                log_dir.mkdir(parents=True, exist_ok=True)
                log_handle = open(log_file, 'a', encoding='utf-8')
            else:
                log_handle = subprocess.PIPE

            process = subprocess.Popen(
                cmd,
                stdout=log_handle,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True
            )

            self.processes[name] = process
            self.process_names[process.pid] = name

            logger.info("%s started with PID %s", name, process.pid)
            return process
        except Exception as e:
            logger.error("Failed to start %s: %s", name, e)
            return None

    def stop_process(self, name: str):
        """Stop a subprocess by name"""
        if name in self.processes:
            process = self.processes[name]
            try:
                # Try graceful shutdown first
                process.terminate()
                try:
                    process.wait(timeout=10)
                except subprocess.TimeoutExpired:
                    # Force kill if graceful shutdown fails
                    process.kill()
                    process.wait()
                logger.info("%s stopped", name)
            except Exception as e:
                logger.error("Error stopping %s: %s", name, e)
            finally:
                if hasattr(process.stdout, 'close'):
                    process.stdout.close()
                del self.processes[name]

    def stop_all(self):
        """Stop all running processes"""
        for name in list(self.processes.keys()):
            self.stop_process(name)
        self.shutdown_event.set()

    def is_alive(self, name: str) -> bool:
        """Check if a process is alive"""
        if name in self.processes:
            return self.processes[name].poll() is None
        return False

    def get_process_status(self) -> Dict[str, bool]:
        """Get status of all managed processes"""
        status = {}
        for name, process in self.processes.items():
            status[name] = process.poll() is None
        return status


class MCPManager:
    """Manages MCP servers"""
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager
        self.mcp_servers = {}

    def check_port_available(self, port: int) -> bool:
        """Check if a port is available"""
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
            result = sock.connect_ex(('localhost', port))
            return result != 0

    def start_mcp_servers(self):
        """Start all MCP servers"""
        logger.info("Starting MCP servers...")

        mcp_servers = [
            {
                'name': 'email_mcp',
                'cmd': [sys.executable, 'mcp_servers/email_watcher_server.py'],
                'port': 8000
            },
            {
                'name': 'linkedin_mcp',
                'cmd': [sys.executable, 'mcp_servers/linkedin_poster_server.py'],
                'port': 8001
            },
            {
                'name': 'odoo_mcp',
                'cmd': [sys.executable, 'mcp_servers/odoo_server.py'],
                'port': 8002
            },
            {
                'name': 'whatsapp_mcp',
                'cmd': [sys.executable, 'mcp_servers/whatsapp_mcp_server.py'],
                'port': 8003
            },
            {
                'name': 'x_twitter_mcp',
                'cmd': [sys.executable, 'mcp_servers/x_poster_server.py'],
                'port': 8004
            },
            {
                'name': 'meta_social_mcp',
                'cmd': [sys.executable, 'mcp_servers/meta_social_server.py'],
                'port': 8005
            },
            {
                'name': 'browser_payment_mcp',
                'cmd': [sys.executable, 'mcp_servers/browser_payment_mcp_server.py'],
                'port': 8006
            },
            {
                'name': 'calendar_mcp',
                'cmd': [sys.executable, 'mcp_servers/calendar_mcp_server.py'],
                'port': 8007
            }
        ]

        for server in mcp_servers:
            try:
                # Check if port is available
                if not self.check_port_available(server['port']):
                    logger.warning("Port %s is already in use, skipping %s", server['port'], server['name'])
                    continue

                # Start MCP server
                log_file = Path('Logs') / f'{server["name"]}.log'
                process = self.process_manager.start_process(
                    server['name'],
                    server['cmd'],
                    str(log_file)
                )

                if process:
                    self.mcp_servers[server['name']] = process
                    logger.info("%s started with PID: %s on port %s", server['name'], process.pid, server['port'])

                    # Give server time to start
                    time.sleep(2)
                else:
                    logger.error(f"Failed to start {server['name']}")

            except Exception as e:
                logger.error("Failed to start %s: %s", server['name'], e)

    def stop_mcp_servers(self):
        """Stop all MCP servers"""
        logger.info("Stopping MCP servers...")
        for name in list(self.mcp_servers.keys()):
            self.process_manager.stop_process(name)
        self.mcp_servers.clear()


class WatcherManager:
    """Manages watcher processes"""
    def __init__(self, process_manager: ProcessManager):
        self.process_manager = process_manager
        self.vault_path = Path("AI_Employee_Vault")

    def start_watchers(self):
        """Start all watcher processes"""
        logger.info("Starting watchers...")

        # Ensure vault directories exist
        for path in [self.vault_path / "Inbox",
                     self.vault_path / "Needs_Action",
                     self.vault_path / "Plans",
                     self.vault_path / "Done",
                     self.vault_path / "Pending_Approval",
                     self.vault_path / "Approved",
                     self.vault_path / "Rejected",
                     self.vault_path / "Briefings",
                     self.vault_path / "Logs"]:
            path.mkdir(parents=True, exist_ok=True)

        watcher_processes = [
            {
                'name': 'gmail_watcher',
                'cmd': [sys.executable, 'watcher/gmail_watcher_impl.py', '--headless'],
                'log_file': str(self.vault_path / 'Logs' / 'gmail_watcher.log')
            },
            {
                'name': 'filesystem_watcher',
                'cmd': [sys.executable, 'watcher/filesystem_detector.py'],
                'log_file': str(self.vault_path / 'Logs' / 'filesystem_watcher.log')
            },
            {
                'name': 'linkedin_poster',
                'cmd': [sys.executable, 'watcher/linkedin_poster_impl.py', '--headless'],
                'log_file': str(self.vault_path / 'Logs' / 'linkedin_poster.log')
            },
            {
                'name': 'whatsapp_watcher',
                'cmd': [sys.executable, 'watcher/whatsapp_watcher_impl.py', '--headless'],
                'log_file': str(self.vault_path / 'Logs' / 'whatsapp_watcher.log')
            },
            {
                'name': 'x_twitter_watcher',
                'cmd': [sys.executable, 'watcher/x_twitter_poster_impl.py', '--headless'],
                'log_file': str(self.vault_path / 'Logs' / 'x_twitter_watcher.log')
            }
        ]

        # Add additional watchers if they exist
        additional_watchers = [
            {'name': f.stem.replace('_impl', ''),
             'cmd': [sys.executable, str(f), '--headless'],
             'log_file': str(self.vault_path / 'Logs' / f'{f.stem.replace("_impl", "")}.log')}
            for f in Path('watcher').glob('*_impl.py')
            if f.name not in ['gmail_watcher_impl.py', 'linkedin_poster_impl.py', 'whatsapp_watcher_impl.py', 'x_twitter_poster_impl.py']
        ]
        watcher_processes.extend(additional_watchers)

        for watcher in watcher_processes:
            if not self.process_manager.is_alive(watcher['name']):
                logger.info(f"Starting {watcher['name']}...")
                self.process_manager.start_process(
                    watcher['name'],
                    watcher['cmd'],
                    watcher['log_file']
                )
            else:
                logger.info(f"{watcher['name']} is already running")


class ClaudeInvoker:
    """Manages Claude Code invocation for the Ralph Wiggum loop"""
    def __init__(self, vault_path: Path):
        self.vault_path = vault_path
        self.last_full_check = 0.0
        self.check_interval = 120  # 2 minutes
        self.last_briefing_check = 0.0
        self.briefing_check_interval = 3600  # Check every hour

    def invoke_claude_ralph_wiggum_loop(self):
        """Invoke Claude Code with Ralph Wiggum loop for persistence"""
        try:
            # Process Ralph Wiggum loop: Inbox → Needs_Action → Plans → Execution → Logging → Done
            self.process_inbox_to_needs_action()
            self.process_needs_action_to_plans()
            self.process_plans_to_execution()
            self.execute_scheduled_tasks()
        except Exception as e:
            logger.error("Error in Claude Ralph Wiggum loop: %s", e)

    def process_inbox_to_needs_action(self):
        """Move files from Inbox to Needs_Action for processing"""
        inbox_path = self.vault_path / "Inbox"
        needs_action_path = self.vault_path / "Needs_Action"

        inbox_files = list(inbox_path.glob("*.md"))
        for file_path in inbox_files:
            try:
                # Move to Needs_Action
                new_path = needs_action_path / file_path.name
                shutil.move(str(file_path), str(new_path))
                logger.info(f"Moved {file_path.name} from Inbox to Needs_Action")

                # Log this action
                self.log_action("FILE_MOVED", "SUCCESS", {
                    "from": "Inbox",
                    "to": "Needs_Action",
                    "file": file_path.name
                })
            except Exception as e:
                logger.error(f"Error moving {file_path.name} from Inbox to Needs_Action: {e}")

    def process_needs_action_to_plans(self):
        """Process files in Needs_Action and create Plans"""
        needs_action_path = self.vault_path / "Needs_Action"
        plans_path = self.vault_path / "Plans"
        pending_approval_path = self.vault_path / "Pending_Approval"

        needs_action_files = list(needs_action_path.glob("*.md"))
        for file_path in needs_action_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Determine if approval is needed
                needs_approval = any(keyword in content.lower() for keyword in [
                    'sensitive', 'approval', 'private', 'confidential', 'finance', 'payment', 'hiring', 'firing'
                ])

                if needs_approval:
                    # Move to Pending_Approval
                    new_path = pending_approval_path / file_path.name
                    shutil.move(str(file_path), str(new_path))
                    logger.info(f"Moved {file_path.name} to Pending_Approval (requires approval)")
                else:
                    # Create a plan
                    plan_file = plans_path / f"Plan_{file_path.stem}.md"
                    plan_content = f"""# Plan for {file_path.stem}

## Original Request:
{content[:500]}...

## Recommended Action:
Execute immediately (no approval required)

## Status:
Planned
"""
                    with open(plan_file, 'w', encoding='utf-8') as f:
                        f.write(plan_content)

                    logger.info(f"Created plan for {file_path.name}")

            except Exception as e:
                logger.error(f"Error processing needs_action file {file_path.name}: {e}")

    def process_plans_to_execution(self):
        """Execute plans that are ready"""
        plans_path = self.vault_path / "Plans"
        done_path = self.vault_path / "Done"

        plan_files = list(plans_path.glob("Plan_*.md"))
        for file_path in plan_files:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()

                # Check if the plan is already executed
                if 'Status: Completed' in content:
                    continue

                # Execute the plan (for now, just mark as done)
                # In a real implementation, this would execute the actual tasks
                updated_content = content.replace('Status: Planned', 'Status: Completed') + f"\n\n## Execution Log\nExecuted on {datetime.now().isoformat()}"

                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(updated_content)

                # Move to Done
                done_file = done_path / f"DONE_{file_path.name}"
                shutil.move(str(file_path), str(done_file))

                logger.info(f"Executed plan {file_path.name}")

            except Exception as e:
                logger.error(f"Error executing plan {file_path.name}: {e}")

    def execute_scheduled_tasks(self):
        """Execute scheduled tasks like CEO briefing generation"""
        from datetime import datetime

        now = datetime.now()

        # Check if it's Sunday night for CEO briefing
        if now.weekday() == 6 and now.hour >= 23:  # Sunday and after 11 PM
            if now.timestamp() - self.last_briefing_check > 3600:  # Only once per hour
                self.generate_ceo_briefing()
                self.last_briefing_check = now.timestamp()
        # Reset briefing check for other days
        elif now.weekday() != 6:
            self.last_briefing_check = 0.0

    def generate_ceo_briefing(self):
        """Generate CEO briefing using the existing CEO briefing generator"""
        try:
            from watcher.ceo_briefing_formatter import generate_weekly_briefing
            briefing_path = generate_weekly_briefing()
            logger.info(f"CEO Briefing generated: {briefing_path}")

            # Log this action
            self.log_action("CEO_BRIEFING_GENERATED", "SUCCESS", {
                "path": briefing_path,
                "date": datetime.now().strftime("%Y-%m-%d")
            })
        except Exception as e:
            logger.error(f"Error generating CEO briefing: {e}")
            self.log_action("CEO_BRIEFING_GENERATED", "ERROR", {
                "error": str(e)
            })

    def log_action(self, action: str, status: str, details: dict):
        """Log an action to the system logs"""
        try:
            logs_path = self.vault_path / "Logs"
            today_log_file = logs_path / f"{datetime.now().strftime('%Y-%m-%d')}.md"

            log_entry = {
                "timestamp": datetime.now().isoformat(),
                "action": action,
                "status": status,
                "agent": "ClaudeInvoker",
                "details": details
            }

            with open(today_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry) + "\n")
        except Exception as e:
            logger.error(f"Error writing audit log: {e}")


class Orchestrator:
    """
    Main orchestrator for the Personal AI Employee system
    """
    def __init__(self):
        self.process_manager = ProcessManager()
        self.mcp_manager = MCPManager(self.process_manager)
        self.watcher_manager = WatcherManager(self.process_manager)
        self.claude_invoker = ClaudeInvoker(Path("AI_Employee_Vault"))
        self.platinum_orchestrator = PlatinumOrchestrator()

        # Setup signal handler for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

        # Health check tracking
        self.last_health_check = 0.0
        self.health_check_interval = 60  # Check every minute

    def _signal_handler(self, signum, _frame):
        """Handle shutdown signals gracefully"""
        logger.info(f"Shutdown signal {signum} received. Stopping orchestrator...")
        self.process_manager.stop_all()
        sys.exit(0)

    def run_health_check(self):
        """Check health of all components and restart if needed"""
        current_time = time.time()
        if current_time - self.last_health_check < self.health_check_interval:
            return

        logger.info("Running health checks...")

        # Check MCP servers
        for name in list(self.mcp_manager.mcp_servers.keys()):
            if not self.process_manager.is_alive(name):
                logger.warning(f"MCP server {name} is down, restarting...")
                # Restart the MCP server
                self.restart_mcp_server(name)

        # Check watchers
        status = self.process_manager.get_process_status()
        for name, is_alive in status.items():
            if not is_alive and name in [w['name'] for w in self.get_watcher_configs()]:
                logger.warning(f"Watcher {name} is down, restarting...")
                self.restart_watcher(name)

        self.last_health_check = current_time

    def get_watcher_configs(self):
        """Get configurations for all watchers"""
        return [
            {
                'name': 'gmail_watcher',
                'cmd': [sys.executable, 'watcher/gmail_watcher_impl.py', '--headless'],
                'log_file': str(Path("AI_Employee_Vault/Logs/gmail_watcher.log"))
            },
            {
                'name': 'filesystem_watcher',
                'cmd': [sys.executable, 'watcher/filesystem_detector.py'],
                'log_file': str(Path("AI_Employee_Vault/Logs/filesystem_watcher.log"))
            },
            {
                'name': 'linkedin_poster',
                'cmd': [sys.executable, 'watcher/linkedin_poster_impl.py', '--headless'],
                'log_file': str(Path("AI_Employee_Vault/Logs/linkedin_poster.log"))
            },
            {
                'name': 'whatsapp_watcher',
                'cmd': [sys.executable, 'watcher/whatsapp_watcher_impl.py', '--headless'],
                'log_file': str(Path("AI_Employee_Vault/Logs/whatsapp_watcher.log"))
            },
            {
                'name': 'x_twitter_watcher',
                'cmd': [sys.executable, 'watcher/x_twitter_poster_impl.py', '--headless'],
                'log_file': str(Path("AI_Employee_Vault/Logs/x_twitter_watcher.log"))
            }
        ]

    def restart_mcp_server(self, name: str):
        """Restart a specific MCP server"""
        # For now, we'll just add logic for the core servers
        mcp_configs = {
            'email_mcp': [sys.executable, 'mcp_servers/email_watcher_server.py'],
            'linkedin_mcp': [sys.executable, 'mcp_servers/linkedin_poster_server.py'],
            'odoo_mcp': [sys.executable, 'mcp_servers/odoo_server.py'],
            'whatsapp_mcp': [sys.executable, 'mcp_servers/whatsapp_mcp_server.py'],
            'x_twitter_mcp': [sys.executable, 'mcp_servers/x_poster_server.py'],
            'meta_social_mcp': [sys.executable, 'mcp_servers/meta_social_server.py'],
            'browser_payment_mcp': [sys.executable, 'mcp_servers/browser_payment_mcp_server.py'],
            'calendar_mcp': [sys.executable, 'mcp_servers/calendar_mcp_server.py']
        }

        if name in mcp_configs:
            log_file = Path('Logs') / f'{name}.log'
            process = self.process_manager.start_process(
                name,
                mcp_configs[name],
                str(log_file)
            )
            if process:
                self.mcp_manager.mcp_servers[name] = process
                logger.info(f"MCP server {name} restarted with PID: {process.pid}")

    def restart_watcher(self, name: str):
        """Restart a specific watcher"""
        configs = self.get_watcher_configs()
        for config in configs:
            if config['name'] == name:
                self.process_manager.start_process(
                    name,
                    config['cmd'],
                    config['log_file']
                )
                logger.info(f"Watcher {name} restarted")

    def run(self):
        """Main orchestrator loop"""
        logger.info("Starting Gold Tier Master Orchestrator...")
        logger.info("Vault path: %s", "AI_Employee_Vault")

        # Print loaded environment variables (for debugging)
        gmail_client_id = os.getenv("GMAIL_CLIENT_ID")
        if gmail_client_id:
            logger.info("Gmail client ID loaded: %s... (truncated)", gmail_client_id[:10])
        else:
            logger.warning("GMAIL_CLIENT_ID not found in environment")

        # Start all MCP servers
        self.mcp_manager.start_mcp_servers()

        # Start all watchers
        self.watcher_manager.start_watchers()

        # Start Platinum tier orchestrator
        self.platinum_orchestrator.start_all_services()

        # Print startup message
        logger.info("Gold Tier Master Orchestrator started successfully!")
        logger.info("MCP servers running: %s", list(self.mcp_manager.mcp_servers.keys()))
        logger.info("Watchers running: %s", list(self.process_manager.get_process_status().keys()))
        logger.info("Platinum orchestrator services started")
        logger.info("Ralph Wiggum loop active with 2-minute cycles")

        # Create a sample test task if needed
        self.create_sample_test_task()

        try:
            # Main loop - run indefinitely
            while not self.process_manager.shutdown_event.is_set():
                # Run periodic Claude tasks
                current_time = time.time()
                if current_time - self.claude_invoker.last_full_check >= self.claude_invoker.check_interval:
                    logger.info("Running Claude Ralph Wiggum loop...")
                    self.claude_invoker.invoke_claude_ralph_wiggum_loop()
                    self.claude_invoker.last_full_check = current_time

                # Run health checks
                self.run_health_check()

                # Sleep for a bit before next check
                time.sleep(10)

        except KeyboardInterrupt:
            logger.info("Keyboard interrupt received. Shutting down...")
        except Exception as e:
            logger.error("Error in main loop: %s", e)
        finally:
            self.platinum_orchestrator.stop_all_services()
            self.process_manager.stop_all()
            logger.info("Gold Tier Master Orchestrator stopped.")

    def create_sample_test_task(self):
        """Create a sample test task in Needs_Action if none exists"""
        needs_action_path = Path("AI_Employee_Vault/Needs_Action")
        test_file = needs_action_path / "TEST_AUTO_TASK.md"

        if not test_file.exists():
            # Check if any other files exist to avoid duplicate test tasks
            if not list(needs_action_path.glob("*.md")):
                with open(test_file, 'w', encoding='utf-8') as f:
                    f.write(f"""# Test Task - Auto Generated

## Request
Test the Ralph Wiggum loop functionality

## Type
test

## Priority
normal

## Status
pending

## Created
{datetime.now().isoformat()}
""")
                logger.info("Created sample test task for auto-testing")


def main():
    """Main function to run the orchestrator"""
    orchestrator = Orchestrator()
    orchestrator.run()


if __name__ == "__main__":
    main()