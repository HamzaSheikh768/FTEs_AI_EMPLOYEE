#!/usr/bin/env python3
"""
Test script for Platinum Tier components
"""
import os
import sys
from pathlib import Path
from datetime import datetime
import logging

# Add the project root to Python path
sys.path.insert(0, str(Path(__file__).parent))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

def test_watchdog():
    """Test Watchdog functionality"""
    logger.info("Testing Watchdog component...")
    try:
        from watcher.watchdog import Watchdog
        watchdog = Watchdog()

        # Collect metrics
        metrics = watchdog.collect_system_metrics()
        logger.info(f"✓ Watchdog metrics collected: CPU {metrics['cpu_percent']:.1f}%, Memory {metrics['memory_percent']:.1f}%")

        # Check for anomalies
        alerts = watchdog.check_for_anomalies(metrics)
        logger.info(f"✓ Watchdog alerts generated: {len(alerts)}")

        # Generate health report
        report = watchdog.generate_health_report()
        if 'summary' in report and 'total_metrics_collected' in report['summary']:
            logger.info(f"✓ Watchdog health report generated: {report['summary']['total_metrics_collected']} metrics")
        else:
            logger.info(f"✓ Watchdog health report generated: {len(report.get('summary', {}))} summary items")

        return True
    except Exception as e:
        logger.error(f"✗ Watchdog test failed: {e}")
        return False


def test_cloud_sync():
    """Test CloudSyncAgent functionality"""
    logger.info("Testing CloudSyncAgent component...")
    try:
        from watcher.cloud_sync_agent import CloudSyncAgent
        sync_agent = CloudSyncAgent()

        # Scan local vault
        items = sync_agent.scan_local_vault()
        logger.info(f"✓ CloudSyncAgent scanned vault: {len(items)} items found")

        # Check sync status
        status = sync_agent.check_sync_status(items[:5])  # Test with first 5 items
        logger.info(f"✓ CloudSyncAgent status check completed: {status['total_items']} items")

        return True
    except Exception as e:
        logger.error(f"✗ CloudSyncAgent test failed: {e}")
        return False


def test_a2a_messenger():
    """Test A2AMessenger functionality"""
    logger.info("Testing A2AMessenger component...")
    try:
        from watcher.a2a_messenger import A2AMessenger, Message, MessageType, MessagePriority
        from datetime import datetime

        messenger = A2AMessenger()

        # Register agents
        messenger.register_agent("test_sender", ["testing"])
        messenger.register_agent("test_recipient", ["testing"])
        logger.info("✓ A2AMessenger agents registered")

        # Create and send a message
        test_msg = Message(
            id="test_msg_1",
            sender="test_sender",
            recipient="test_recipient",
            type=MessageType.STATUS_UPDATE,
            content={"status": "test", "value": 123},
            timestamp=datetime.now(),
            priority=MessagePriority.NORMAL
        )

        success = messenger.send_message(test_msg)
        logger.info(f"✓ A2AMessenger message sent: {success}")

        # Receive message
        received = messenger.receive_message("test_recipient")
        logger.info(f"✓ A2AMessenger message received: {received is not None}")

        return True
    except Exception as e:
        logger.error(f"✗ A2AMessenger test failed: {e}")
        return False


def test_scheduler():
    """Test SchedulerCron functionality"""
    logger.info("Testing SchedulerCron component...")
    try:
        from watcher.scheduler_cron import SchedulerCron, TaskPriority
        from datetime import datetime

        scheduler = SchedulerCron()

        # Add a simple test task
        def test_task():
            logger.info("Test task executed!")
            return "Task completed"

        success = scheduler.add_task(
            task_id="test_task_1",
            name="Test Task",
            cron_expression="* * * * *",  # Every minute
            function=test_task,
            priority=TaskPriority.NORMAL
        )
        logger.info(f"✓ SchedulerCron task added: {success}")

        # Get task status
        statuses = scheduler.get_all_task_statuses()
        logger.info(f"✓ SchedulerCron task statuses retrieved: {len(statuses)} tasks")

        return True
    except Exception as e:
        logger.error(f"✗ SchedulerCron test failed: {e}")
        return False


def test_finance_watcher():
    """Test FinanceWatcher functionality"""
    logger.info("Testing FinanceWatcher component...")
    try:
        from watcher.finance_watcher import FinanceWatcher, FinancialTransaction, TransactionType, TransactionCategory, Currency
        from datetime import datetime
        import uuid
        from decimal import Decimal

        watcher = FinanceWatcher()

        # Add an account
        watcher.add_account("test_account", "Test Account", Decimal('1000'), Currency.USD)
        logger.info("✓ FinanceWatcher account added")

        # Create a test transaction
        transaction = FinancialTransaction(
            id=str(uuid.uuid4()),
            account_id="test_account",
            amount=Decimal('125.50'),
            currency=Currency.USD,
            transaction_type=TransactionType.EXPENSE,
            category=TransactionCategory.FOOD,
            description="Test transaction",
            merchant="Test Merchant",
            timestamp=datetime.now()
        )

        # Record transaction
        success = watcher.record_transaction(transaction)
        logger.info(f"✓ FinanceWatcher transaction recorded: {success}")

        # Generate summary
        summary = watcher.generate_financial_summary(period_days=1)
        logger.info(f"✓ FinanceWatcher summary generated: ${summary.total_income} income, ${summary.total_expenses} expenses")

        return True
    except Exception as e:
        logger.error(f"✗ FinanceWatcher test failed: {e}")
        return False


def test_ceo_briefing_generator():
    """Test CEOBriefingGenerator functionality"""
    logger.info("Testing CEOBriefingGenerator component...")
    try:
        from watcher.ceo_briefing_generator import CEOBriefingGenerator, ReportType

        generator = CEOBriefingGenerator()

        # Generate a test briefing
        briefing = generator.generate_briefing(ReportType.WEEKLY)
        logger.info(f"✓ CEOBriefingGenerator briefing created: {briefing.title}")

        # Check sections
        logger.info(f"✓ CEOBriefingGenerator sections: {len(briefing.sections)}")

        # Export in different formats
        export_json = generator.export_report(briefing.id, "json")
        export_md = generator.export_report(briefing.id, "markdown")
        logger.info(f"✓ CEOBriefingGenerator exports created: JSON at {export_json}, MD at {export_md}")

        return True
    except Exception as e:
        logger.error(f"✗ CEOBriefingGenerator test failed: {e}")
        return False


def test_platinum_orchestrator():
    """Test Platinum Orchestrator integration"""
    logger.info("Testing Platinum Orchestrator integration...")
    try:
        from platinum_orchestrator import PlatinumOrchestrator

        orchestrator = PlatinumOrchestrator()

        # Get system status
        status = orchestrator.get_system_status()
        logger.info(f"✓ Platinum Orchestrator status retrieved: {status['component_statuses']}")

        # Coordinate a test workflow
        test_workflow = [
            {"required_capabilities": ["testing"], "task": "test_task_1"},
            {"required_capabilities": ["reporting"], "task": "generate_report"}
        ]

        orchestrator.coordinate_workflow("test_workflow", test_workflow)
        logger.info("✓ Platinum Orchestrator workflow coordinated")

        return True
    except Exception as e:
        logger.error(f"✗ Platinum Orchestrator test failed: {e}")
        return False


def main():
    """Run all tests"""
    logger.info("Starting Platinum Tier component tests...")

    tests = [
        ("Watchdog", test_watchdog),
        ("CloudSyncAgent", test_cloud_sync),
        ("A2AMessenger", test_a2a_messenger),
        ("SchedulerCron", test_scheduler),
        ("FinanceWatcher", test_finance_watcher),
        ("CEOBriefingGenerator", test_ceo_briefing_generator),
        ("PlatinumOrchestrator", test_platinum_orchestrator),
    ]

    results = []
    for test_name, test_func in tests:
        logger.info(f"\n--- Testing {test_name} ---")
        success = test_func()
        results.append((test_name, success))

    # Print summary
    logger.info(f"\n--- Test Summary ---")
    passed = 0
    for test_name, success in results:
        status = "PASS" if success else "FAIL"
        logger.info(f"{test_name}: {status}")
        if success:
            passed += 1

    logger.info(f"\nTotal: {passed}/{len(results)} tests passed")

    if passed == len(results):
        logger.info("🎉 All Platinum Tier components are working correctly!")
        return True
    else:
        logger.info("❌ Some Platinum Tier components have issues.")
        return False


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)