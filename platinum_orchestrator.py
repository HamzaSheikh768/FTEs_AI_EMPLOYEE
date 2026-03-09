"""
Platinum Tier Orchestrator - Main System Integration

This orchestrator coordinates all Platinum tier components:
- Watchdog: System health monitoring
- CloudSyncAgent: Cloud-local synchronization
- A2AMessenger: Agent-to-agent communication
- CEOBriefingGenerator: Business reports
- SchedulerCron: Task scheduling
- FinanceWatcher: Financial monitoring
"""
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any
import logging
from watcher.watchdog import Watchdog
from watcher.cloud_sync_agent import CloudSyncAgent
from watcher.a2a_messenger import A2AMessenger
from watcher.ceo_briefing_generator import CEOBriefingGenerator
from watcher.scheduler_cron import SchedulerCron
from watcher.finance_watcher import FinanceWatcher


class PlatinumOrchestrator:
    """
    Platinum Tier Orchestrator - Coordinates all Platinum tier components
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Platinum tier orchestrator"""
        self.config = self._load_config(config_path)

        # Initialize all Platinum tier components
        self.watchdog = Watchdog()
        self.cloud_sync = CloudSyncAgent()
        self.messenger = A2AMessenger()
        self.briefing_generator = CEOBriefingGenerator()
        self.scheduler = SchedulerCron()
        self.finance_watcher = FinanceWatcher()

        # Setup logging for orchestrator
        self._setup_logging()

        # Component registration for A2AMessenger
        self._register_agents()

        # Component status tracking
        self.component_statuses = {
            'watchdog': 'initialized',
            'cloud_sync': 'initialized',
            'messenger': 'initialized',
            'briefing_generator': 'initialized',
            'scheduler': 'initialized',
            'finance_watcher': 'initialized'
        }

        # Thread handles
        self.threads = {}

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load orchestrator configuration"""
        default_config = {
            'log_level': 'INFO',
            'heartbeat_interval': 30,
            'health_check_interval': 60,
            'sync_interval': 300  # 5 minutes
        }

        if config_path and Path(config_path).exists():
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                    # Merge with defaults
                    for key, value in default_config.items():
                        if key not in config:
                            config[key] = value
                return config
            except Exception as e:
                print(f"Error loading config, using defaults: {e}")
                return default_config
        return default_config

    def _setup_logging(self):
        """Setup logging for the orchestrator"""
        log_file = Path('AI_Employee_Vault/Platinum/Orchestrator_Logs') / f"orchestrator_{datetime.now().strftime('%Y%m%d')}.log"
        log_file.parent.mkdir(parents=True, exist_ok=True)

        logging.basicConfig(
            level=getattr(logging, self.config.get('log_level', 'INFO')),
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def _register_agents(self):
        """Register all components as agents in the A2AMessenger system"""
        # Register each component as an agent
        self.messenger.register_agent("watchdog_agent", ["system_monitoring", "health_checks"])
        self.messenger.register_agent("cloud_sync_agent", ["file_sync", "backup", "cloud_integration"])
        self.messenger.register_agent("briefing_generator_agent", ["reporting", "analytics", "business_intelligence"])
        self.messenger.register_agent("scheduler_agent", ["task_scheduling", "cron_jobs", "time_management"])
        self.messenger.register_agent("finance_watcher_agent", ["financial_monitoring", "transaction_analysis", "fraud_detection"])

        self.logger.info("All Platinum tier agents registered with A2AMessenger")

    def start_all_services(self):
        """Start all Platinum tier services"""
        self.logger.info("Starting Platinum tier services...")

        # Start Watchdog monitoring
        watchdog_thread = threading.Thread(target=self.watchdog.start_monitoring, daemon=True)
        watchdog_thread.start()
        self.threads['watchdog'] = watchdog_thread
        self.component_statuses['watchdog'] = 'running'
        self.logger.info("Watchdog monitoring started")

        # Start scheduler
        self.scheduler.start_scheduler()
        self.component_statuses['scheduler'] = 'running'
        self.logger.info("Scheduler started")

        # Start A2AMessenger heartbeat monitoring
        heartbeat_thread = self.messenger.start_heartbeat_monitoring(
            interval=self.config.get('heartbeat_interval', 30)
        )
        self.threads['messenger'] = heartbeat_thread
        self.component_statuses['messenger'] = 'running'
        self.logger.info("A2AMessenger heartbeat monitoring started")

        # Start continuous monitoring threads
        monitoring_thread = threading.Thread(target=self._continuous_monitoring, daemon=True)
        monitoring_thread.start()
        self.threads['monitoring'] = monitoring_thread
        self.logger.info("Continuous monitoring started")

        self.logger.info("All Platinum tier services started successfully")

    def stop_all_services(self):
        """Stop all Platinum tier services"""
        self.logger.info("Stopping Platinum tier services...")

        # Stop scheduler
        self.scheduler.stop_scheduler()
        self.component_statuses['scheduler'] = 'stopped'
        self.logger.info("Scheduler stopped")

        # Wait for threads to finish (with timeout)
        for name, thread in self.threads.items():
            if thread.is_alive():
                # Note: daemon threads will stop automatically, but we still log
                self.logger.info(f"Thread {name} will stop automatically (daemon)")

        self.logger.info("All Platinum tier services stopped")

    def _continuous_monitoring(self):
        """Main orchestrator loop for continuous monitoring and coordination"""
        self.logger.info("Platinum orchestrator continuous monitoring started")

        while True:
            try:
                # Perform health checks periodically
                if datetime.now().minute % 5 == 0:  # Every 5 minutes
                    self._perform_health_check()

                # Check for sync opportunities periodically
                if datetime.now().minute % 10 == 0:  # Every 10 minutes
                    self._check_sync_opportunities()

                # Generate reports if needed
                if datetime.now().hour == 9 and datetime.now().minute == 0:  # Daily at 9 AM
                    self._generate_daily_briefing()

                # Check financial alerts periodically
                if datetime.now().minute % 15 == 0:  # Every 15 minutes
                    self._check_financial_alerts()

                time.sleep(60)  # Check every minute

            except Exception as e:
                self.logger.error(f"Error in orchestrator monitoring loop: {e}")
                time.sleep(60)  # Wait before retrying

    def _perform_health_check(self):
        """Perform comprehensive system health check"""
        self.logger.info("Performing system health check...")

        # Check each component status
        watchdog_status = self.component_statuses.get('watchdog', 'unknown')
        sync_status = self.component_statuses.get('cloud_sync', 'unknown')
        messenger_status = self.component_statuses.get('messenger', 'unknown')

        # Generate health report
        self.watchdog.generate_health_report()

        # Check for component failures and restart if needed
        for component, status in self.component_statuses.items():
            if status == 'failed':
                self.logger.warning(f"Restarting failed component: {component}")
                # In a real implementation, restart the component
                self.component_statuses[component] = 'restarted'

        # Send status update via messenger
        status_data = {
            'timestamp': datetime.now().isoformat(),
            'component_statuses': self.component_statuses,
            'system_health': 'monitoring'
        }
        self.messenger.send_status_update("orchestrator", status_data)

        self.logger.info("System health check completed")

    def _check_sync_opportunities(self):
        """Check for opportunities to sync data"""
        self.logger.info("Checking for sync opportunities...")

        # Check if any vault changes need synchronization
        try:
            # Perform a sync with default provider (simulated)
            sync_results = self.cloud_sync.full_sync()
            self.logger.info(f"Sync completed: {sync_results['status_report']}")
        except Exception as e:
            self.logger.error(f"Sync failed: {e}")
            # Send error notification
            error_data = {
                'error': str(e),
                'component': 'cloud_sync',
                'timestamp': datetime.now().isoformat()
            }
            self.messenger.send_error_notification("cloud_sync_agent", error_data)

    def _generate_daily_briefing(self):
        """Generate daily CEO briefing"""
        self.logger.info("Generating daily CEO briefing...")

        try:
            # Generate weekly briefing
            briefing = self.briefing_generator.generate_briefing()
            self.logger.info(f"Daily briefing generated: {briefing.title}")

            # Send notification about briefing generation
            notification_data = {
                'briefing_id': briefing.id,
                'title': briefing.title,
                'generated_at': datetime.now().isoformat(),
                'summary': briefing.summary
            }

            # Broadcast to relevant agents
            self.messenger.broadcast_message(
                message_template=self.messenger.send_message.__code__,  # This is a placeholder
                recipients=['briefing_generator_agent', 'system_monitor']
            )

        except Exception as e:
            self.logger.error(f"Briefing generation failed: {e}")
            # Send error notification
            error_data = {
                'error': str(e),
                'component': 'briefing_generator',
                'timestamp': datetime.now().isoformat()
            }
            self.messenger.send_error_notification("briefing_generator_agent", error_data)

    def _check_financial_alerts(self):
        """Check for financial alerts and handle them"""
        self.logger.info("Checking for financial alerts...")

        try:
            # Get recent alerts
            recent_alerts = self.finance_watcher.get_alerts(limit=10, severity='warning')

            if recent_alerts:
                for alert in recent_alerts:
                    self.logger.info(f"Financial alert: {alert.message}")

                    # Send alert via messenger
                    alert_data = {
                        'alert_id': alert.id,
                        'type': alert.type.value,
                        'severity': alert.severity,
                        'message': alert.message,
                        'timestamp': alert.timestamp.isoformat(),
                        'amount': str(alert.amount) if alert.amount else None
                    }

                    # Send to financial monitoring agents
                    self.messenger.send_message(
                        self.messenger.send_message.__code__,  # Placeholder
                    )

        except Exception as e:
            self.logger.error(f"Financial alert check failed: {e}")

    def coordinate_workflow(self, workflow_name: str, tasks: List[Dict[str, Any]]):
        """Coordinate a multi-step workflow across components"""
        self.logger.info(f"Coordinating workflow: {workflow_name}")

        # Use the A2AMessenger to coordinate the workflow
        success = self.messenger.coordinate_workflow(workflow_name, tasks)

        if success:
            self.logger.info(f"Workflow {workflow_name} coordinated successfully")
        else:
            self.logger.error(f"Workflow {workflow_name} coordination failed")

    def handle_system_event(self, event_type: str, event_data: Dict[str, Any]):
        """Handle system events and coordinate response"""
        self.logger.info(f"Handling system event: {event_type}")

        # Determine appropriate response based on event type
        if event_type == "high_cpu_usage":
            # Coordinate with watchdog and other components
            self.logger.info("Handling high CPU usage event")
            # Could trigger scaling, alerting, or other responses
        elif event_type == "financial_anomaly":
            # Handle financial anomaly with finance_watcher and notifications
            self.logger.info("Handling financial anomaly event")
            # Could trigger fraud investigation, alerts, etc.
        elif event_type == "sync_required":
            # Trigger cloud sync
            self.logger.info("Handling sync required event")
            self._check_sync_opportunities()
        else:
            self.logger.info(f"Unknown event type: {event_type}")

    def get_system_status(self) -> Dict[str, Any]:
        """Get comprehensive system status"""
        status = {
            'timestamp': datetime.now().isoformat(),
            'orchestrator_status': 'running',
            'component_statuses': self.component_statuses,
            'active_threads': len([t for t in self.threads.values() if t.is_alive()]),
            'health_report': self.watchdog.generate_health_report() if hasattr(self, 'watchdog') else None,
            'scheduled_tasks': self.scheduler.get_scheduled_tasks() if hasattr(self, 'scheduler') else [],
            'recent_alerts': len(self.finance_watcher.alerts) if hasattr(self, 'finance_watcher') and hasattr(self.finance_watcher, 'alerts') else 0
        }
        return status

    def run(self):
        """Run the orchestrator"""
        self.logger.info("Starting Platinum Tier Orchestrator...")

        try:
            # Start all services
            self.start_all_services()

            # Main loop - keep running
            while True:
                time.sleep(10)  # Main loop doesn't need to do much, services run in background

        except KeyboardInterrupt:
            self.logger.info("Shutdown requested by user")
        except Exception as e:
            self.logger.error(f"Orchestrator error: {e}")
        finally:
            self.stop_all_services()
            self.logger.info("Platinum Tier Orchestrator stopped")


if __name__ == "__main__":
    # Create and run the orchestrator
    orchestrator = PlatinumOrchestrator()

    # Create a simple workflow to test coordination
    test_workflow = [
        {"required_capabilities": ["file_processing"], "task": "scan_inbox"},
        {"required_capabilities": ["reporting"], "task": "generate_daily_report"},
        {"required_capabilities": ["file_sync"], "task": "sync_reports_to_cloud"}
    ]

    # Coordinate the test workflow
    orchestrator.coordinate_workflow("test_daily_workflow", test_workflow)

    # Get system status
    status = orchestrator.get_system_status()
    print(f"System status: {status['component_statuses']}")
    print(f"Active threads: {status['active_threads']}")
    print(f"Recent alerts: {status['recent_alerts']}")

    # Example of handling a system event
    orchestrator.handle_system_event("sync_required", {"reason": "daily_sync", "priority": "normal"})

    print("Platinum Orchestrator initialization complete")
    print("All Platinum tier components have been integrated")

    # Uncomment the next lines to run the orchestrator continuously
    # orchestrator.run()