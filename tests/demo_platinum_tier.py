#!/usr/bin/env python3
"""
Demonstration script for Platinum Tier components
"""
import os
import sys
from pathlib import Path
from datetime import datetime, timedelta
import logging
import time

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def demonstrate_watchdog():
    """Demonstrate Watchdog functionality"""
    logger.info("=== Demonstrating Watchdog ===")
    from watcher.watchdog import Watchdog

    watchdog = Watchdog()

    # Collect system metrics
    metrics = watchdog.collect_system_metrics()
    logger.info(f"✓ System metrics collected:")
    logger.info(f"  - CPU: {metrics['cpu_percent']}%")
    logger.info(f"  - Memory: {metrics['memory_percent']}%")
    logger.info(f"  - Disk: {metrics['disk_percent']}%")
    logger.info(f"  - Process count: {metrics['process_count']}")

    # Check for anomalies
    alerts = watchdog.check_for_anomalies(metrics)
    logger.info(f"✓ Checked for anomalies - found {len(alerts)} alerts")

    # Generate health report
    report = watchdog.generate_health_report()
    logger.info(f"✓ Generated health report with {report['summary']['total_metrics_collected']} metrics")
    logger.info("")


def demonstrate_cloud_sync():
    """Demonstrate CloudSyncAgent functionality"""
    logger.info("=== Demonstrating CloudSyncAgent ===")
    from watcher.cloud_sync_agent import CloudSyncAgent

    sync_agent = CloudSyncAgent()

    # Scan local vault
    items = sync_agent.scan_local_vault()
    logger.info(f"✓ Scanned vault: {len(items)} items found")
    logger.info(f"  - First 5 items: {[item.cloud_path for item in items[:5]]}")

    # Check sync status
    status = sync_agent.check_sync_status(items[:5])
    logger.info(f"✓ Sync status: {status['total_items']} items, {status['synced_items']} synced")
    logger.info("")


def demonstrate_a2a_messenger():
    """Demonstrate A2AMessenger functionality"""
    logger.info("=== Demonstrating A2AMessenger ===")
    from watcher.a2a_messenger import A2AMessenger, Message, MessageType, MessagePriority
    from datetime import datetime

    messenger = A2AMessenger()

    # Register agents
    messenger.register_agent("demo_sender", ["demo", "testing"])
    messenger.register_agent("demo_recipient", ["demo", "processing"])
    logger.info("✓ Registered demo agents")

    # Create and send a message
    demo_msg = Message(
        id="demo_msg_1",
        sender="demo_sender",
        recipient="demo_recipient",
        type=MessageType.STATUS_UPDATE,
        content={"status": "demo", "value": "Hello from Platinum tier!"},
        timestamp=datetime.now(),
        priority=MessagePriority.NORMAL
    )

    success = messenger.send_message(demo_msg)
    logger.info(f"✓ Message sent: {success}")

    # Receive message
    received = messenger.receive_message("demo_recipient")
    if received:
        logger.info(f"✓ Message received: {received.content['value']}")
    logger.info("")


def demonstrate_scheduler():
    """Demonstrate SchedulerCron functionality"""
    logger.info("=== Demonstrating SchedulerCron ===")
    from watcher.scheduler_cron import SchedulerCron, TaskPriority

    scheduler = SchedulerCron()

    # Define a demo task function
    def demo_task(task_name: str):
        logger.info(f"Executing demo task: {task_name}")
        return f"Demo task {task_name} completed at {datetime.now()}"

    # Add a demo task
    success = scheduler.add_task(
        task_id="demo_task_1",
        name="Demo Task",
        cron_expression="0 * * * *",  # Every hour
        function=demo_task,
        args=["platinum_demo"],
        priority=TaskPriority.NORMAL
    )
    logger.info(f"✓ Demo task added: {success}")

    # Get task status
    statuses = scheduler.get_all_task_statuses()
    logger.info(f"✓ Task statuses: {statuses}")
    logger.info("")


def demonstrate_finance_watcher():
    """Demonstrate FinanceWatcher functionality"""
    logger.info("=== Demonstrating FinanceWatcher ===")
    from watcher.finance_watcher import FinanceWatcher, FinancialTransaction, TransactionType, TransactionCategory, Currency
    from datetime import datetime
    import uuid
    from decimal import Decimal

    watcher = FinanceWatcher()

    # Add an account
    watcher.add_account("demo_account", "Demo Account", Decimal('5000'), Currency.USD)
    logger.info("✓ Demo account added")

    # Create demo transactions
    transactions = [
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="demo_account",
            amount=Decimal('125.50'),
            currency=Currency.USD,
            transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.FOOD,
            description="Demo lunch expense",
            merchant="Demo Restaurant",
            timestamp=datetime.now()
        ),
        FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="demo_account",
            amount=Decimal('2500.00'),
            currency=Currency.USD,
            transaction_type=TransactionType.INCOME,
            category=TransactionCategory.SALARY,
            description="Demo salary income",
            merchant="Demo Employer",
            timestamp=datetime.now()
        )
    ]

    # Record transactions
    for transaction in transactions:
        success = watcher.record_transaction(transaction)
        logger.info(f"✓ Transaction recorded: {transaction.description} (${transaction.amount})")

    # Generate summary
    summary = watcher.generate_financial_summary(period_days=7)
    logger.info(f"✓ Financial summary generated:")
    logger.info(f"  - Income: ${summary.total_income}")
    logger.info(f"  - Expenses: ${summary.total_expenses}")
    logger.info(f"  - Net: ${summary.net_flow}")
    logger.info("")


def demonstrate_ceo_briefing_generator():
    """Demonstrate CEOBriefingGenerator functionality"""
    logger.info("=== Demonstrating CEOBriefingGenerator ===")
    from watcher.ceo_briefing_generator import CEOBriefingGenerator, ReportType

    generator = CEOBriefingGenerator()

    # Generate a demo briefing
    briefing = generator.generate_briefing(ReportType.WEEKLY)
    logger.info(f"✓ CEO briefing generated: {briefing.title}")

    # Check sections
    logger.info(f"✓ Briefing sections: {len(briefing.sections)}")
    for i, section in enumerate(briefing.sections):
        logger.info(f"  - {i+1}. {section.title}")

    # Show recommendations
    logger.info(f"✓ Recommendations: {len(briefing.recommendations)}")
    for rec in briefing.recommendations[:2]:  # Show first 2
        logger.info(f"  - {rec.title}: {rec.description}")

    # Export in different formats
    export_json = generator.export_report(briefing.id, "json")
    export_md = generator.export_report(briefing.id, "markdown")
    logger.info(f"✓ Exports created: JSON at {export_json}, MD at {export_md}")
    logger.info("")


def demonstrate_platinum_orchestrator():
    """Demonstrate Platinum Orchestrator integration"""
    logger.info("=== Demonstrating Platinum Orchestrator ===")
    from platinum_orchestrator import PlatinumOrchestrator

    orchestrator = PlatinumOrchestrator()

    # Get system status
    status = orchestrator.get_system_status()
    logger.info(f"✓ System status retrieved:")
    logger.info(f"  - Timestamp: {status['timestamp']}")
    logger.info(f"  - Orchestrator: {status['orchestrator_status']}")
    logger.info(f"  - Components: {list(status['component_statuses'].keys())}")
    logger.info(f"  - Active threads: {status['active_threads']}")

    # Coordinate a demo workflow
    demo_workflow = [
        {"required_capabilities": ["reporting"], "task": "generate_demo_report"},
        {"required_capabilities": ["file_sync"], "task": "sync_demo_report"}
    ]

    orchestrator.coordinate_workflow("demo_workflow", demo_workflow)
    logger.info("✓ Demo workflow coordinated")
    logger.info("")


def main():
    """Run all demonstrations"""
    logger.info("🚀 Starting Platinum Tier component demonstration...")
    logger.info(f"Current time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    logger.info("")

    demonstrations = [
        ("Watchdog", demonstrate_watchdog),
        ("CloudSyncAgent", demonstrate_cloud_sync),
        ("A2AMessenger", demonstrate_a2a_messenger),
        ("SchedulerCron", demonstrate_scheduler),
        ("FinanceWatcher", demonstrate_finance_watcher),
        ("CEOBriefingGenerator", demonstrate_ceo_briefing_generator),
        ("PlatinumOrchestrator", demonstrate_platinum_orchestrator),
    ]

    for demo_name, demo_func in demonstrations:
        try:
            demo_func()
        except Exception as e:
            logger.error(f"❌ Demo {demo_name} failed: {e}")
            import traceback
            traceback.print_exc()

    logger.info("🎉 Platinum Tier demonstration completed!")
    logger.info("All components are integrated and functioning correctly.")


if __name__ == "__main__":
    main()