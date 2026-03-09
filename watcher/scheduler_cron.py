"""
Platinum Tier SchedulerCron - Advanced Task Scheduling

Handles complex time-based task scheduling with support for cron expressions, manages task dependencies,
schedules tasks across multiple time zones, supports conditional scheduling based on system state,
provides scheduling conflict detection and resolution, and enables dynamic scheduling adjustments.
"""
import json
import time
import threading
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable, Union
from dataclasses import dataclass
from enum import Enum
import logging
import re
import pytz
from croniter import croniter


class TaskStatus(Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class TaskPriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class TaskDependency:
    task_id: str
    condition: str  # 'completed', 'success', 'failure', 'timestamp'


@dataclass
class ScheduledTask:
    id: str
    name: str
    cron_expression: str
    function: Callable
    args: List[Any]
    kwargs: Dict[str, Any]
    timezone: str
    priority: TaskPriority
    dependencies: List[TaskDependency]
    max_retries: int
    timeout: int  # seconds
    created_at: datetime
    last_run: Optional[datetime] = None
    next_run: Optional[datetime] = None
    status: TaskStatus = TaskStatus.PENDING
    retries: int = 0
    result: Optional[Any] = None
    error: Optional[str] = None


class SchedulerCron:
    """
    Platinum Tier SchedulerCron - Advanced Task Scheduling
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the Scheduler Cron system"""
        self.config = self._load_config(config_path)
        self.scheduling_logs_dir = Path(self.config.get('scheduling_logs_dir', 'AI_Employee_Vault/Platinum/Scheduling_Logs'))
        self.performance_logs_dir = Path(self.config.get('performance_logs_dir', 'AI_Employee_Vault/Platinum/Health_Metrics'))

        # Initialize task registry
        self.tasks: Dict[str, ScheduledTask] = {}
        self.task_queue: List[ScheduledTask] = []
        self.executed_tasks: List[ScheduledTask] = []
        self.scheduling_lock = threading.Lock()
        self.running = False
        self.scheduler_thread: Optional[threading.Thread] = None

        # Setup logging
        self.scheduling_logs_dir.mkdir(parents=True, exist_ok=True)
        self.performance_logs_dir.mkdir(parents=True, exist_ok=True)
        self._setup_logging()

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'scheduling_logs_dir': 'AI_Employee_Vault/Platinum/Scheduling_Logs',
            'performance_logs_dir': 'AI_Employee_Vault/Platinum/Health_Metrics',
            'default_timezone': 'UTC',
            'scheduler_interval': 1,  # seconds
            'max_concurrent_tasks': 5,
            'task_retention_days': 30
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
        """Setup logging for the Scheduler Cron"""
        log_file = self.scheduling_logs_dir / f"scheduler_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def validate_cron_expression(self, cron_expr: str) -> bool:
        """Validate a cron expression"""
        try:
            # Test with a known datetime
            croniter(cron_expr, datetime.now())
            return True
        except:
            return False

    def parse_cron_to_datetime(self, cron_expr: str, timezone_str: str = 'UTC', base_time: Optional[datetime] = None) -> datetime:
        """Parse a cron expression to the next execution datetime"""
        if base_time is None:
            base_time = datetime.now(pytz.timezone(timezone_str))
        else:
            base_time = base_time.astimezone(pytz.timezone(timezone_str))

        cron_iter = croniter(cron_expr, base_time)
        next_run = cron_iter.get_next(datetime)
        return next_run

    def add_task(
        self,
        task_id: str,
        name: str,
        cron_expression: str,
        function: Callable,
        args: List[Any] = None,
        kwargs: Dict[str, Any] = None,
        timezone: str = None,
        priority: TaskPriority = TaskPriority.NORMAL,
        dependencies: List[TaskDependency] = None,
        max_retries: int = 3,
        timeout: int = 300  # 5 minutes
    ) -> bool:
        """Add a new task to the scheduler"""
        if not self.validate_cron_expression(cron_expression):
            self.logger.error(f"Invalid cron expression: {cron_expression}")
            return False

        if timezone is None:
            timezone = self.config.get('default_timezone', 'UTC')

        if args is None:
            args = []
        if kwargs is None:
            kwargs = {}
        if dependencies is None:
            dependencies = []

        # Check if task already exists
        if task_id in self.tasks:
            self.logger.warning(f"Task {task_id} already exists, updating...")
            # Cancel the existing task if it's running
            existing_task = self.tasks[task_id]
            if existing_task.status in [TaskStatus.RUNNING, TaskStatus.SCHEDULED]:
                existing_task.status = TaskStatus.CANCELLED

        # Calculate next run time
        next_run = self.parse_cron_to_datetime(cron_expression, timezone)

        task = ScheduledTask(
            id=task_id,
            name=name,
            cron_expression=cron_expression,
            function=function,
            args=args,
            kwargs=kwargs,
            timezone=timezone,
            priority=priority,
            dependencies=dependencies,
            max_retries=max_retries,
            timeout=timeout,
            created_at=datetime.now(),
            next_run=next_run
        )

        self.tasks[task_id] = task
        self._add_to_queue(task)

        self.logger.info(f"Task {task_id} added: {name} scheduled for {next_run}")
        return True

    def _add_to_queue(self, task: ScheduledTask):
        """Add task to the execution queue based on priority and timing"""
        with self.scheduling_lock:
            # Remove from queue if already present
            self.task_queue = [t for t in self.task_queue if t.id != task.id]

            # Add with proper ordering
            inserted = False
            for i, queue_task in enumerate(self.task_queue):
                if task.priority.value > queue_task.priority.value:
                    self.task_queue.insert(i, task)
                    inserted = True
                    break
                elif task.priority.value == queue_task.priority.value and task.next_run < queue_task.next_run:
                    self.task_queue.insert(i, task)
                    inserted = True
                    break

            if not inserted:
                self.task_queue.append(task)

    def remove_task(self, task_id: str) -> bool:
        """Remove a task from the scheduler"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]
        task.status = TaskStatus.CANCELLED

        # Remove from queue
        self.task_queue = [t for t in self.task_queue if t.id != task_id]

        del self.tasks[task_id]
        self.logger.info(f"Task {task_id} removed from scheduler")
        return True

    def _check_task_dependencies(self, task: ScheduledTask) -> bool:
        """Check if all task dependencies are satisfied"""
        if not task.dependencies:
            return True

        for dep in task.dependencies:
            if dep.task_id not in self.tasks:
                self.logger.error(f"Dependency {dep.task_id} not found for task {task.id}")
                return False

            dep_task = self.tasks[dep.task_id]
            if dep.condition == 'completed':
                if dep_task.status not in [TaskStatus.COMPLETED, TaskStatus.FAILED]:
                    return False
            elif dep.condition == 'success':
                if dep_task.status != TaskStatus.COMPLETED:
                    return False
            elif dep.condition == 'failure':
                if dep_task.status != TaskStatus.FAILED:
                    return False
            elif dep.condition == 'timestamp':
                # Check if dependency executed after a certain time
                if dep_task.last_run is None or dep_task.last_run < datetime.fromisoformat(dep.condition):
                    return False

        return True

    def _execute_task(self, task: ScheduledTask) -> bool:
        """Execute a single task"""
        original_status = task.status
        task.status = TaskStatus.RUNNING
        task.last_run = datetime.now()

        try:
            # Execute the task function
            result = task.function(*task.args, **task.kwargs)
            task.result = result
            task.status = TaskStatus.COMPLETED
            self.logger.info(f"Task {task.id} completed successfully")
            return True

        except Exception as e:
            task.error = str(e)
            task.status = TaskStatus.FAILED
            self.logger.error(f"Task {task.id} failed: {str(e)}")

            # Check if we should retry
            if task.retries < task.max_retries:
                task.retries += 1
                # Reschedule for retry
                task.next_run = datetime.now() + timedelta(seconds=60 * task.retries)  # Exponential backoff
                task.status = TaskStatus.SCHEDULED
                self._add_to_queue(task)
                self.logger.info(f"Task {task.id} scheduled for retry ({task.retries}/{task.max_retries})")
            else:
                self.logger.error(f"Task {task.id} failed after {task.max_retries} retries")

            return False

    def _run_scheduler_loop(self):
        """Main scheduler loop that runs in a separate thread"""
        self.logger.info("Scheduler started")

        while self.running:
            current_time = datetime.now()

            # Check for tasks that should run now
            with self.scheduling_lock:
                ready_tasks = []
                for task in self.task_queue[:]:  # Create a copy to iterate over
                    if task.next_run and current_time >= task.next_run:
                        if self._check_task_dependencies(task):
                            ready_tasks.append(task)
                            # Remove from queue temporarily
                            self.task_queue.remove(task)

            # Execute ready tasks
            for task in ready_tasks:
                success = self._execute_task(task)
                if success:
                    # Schedule next execution
                    task.next_run = self.parse_cron_to_datetime(
                        task.cron_expression,
                        task.timezone,
                        task.last_run
                    )
                    # Add back to queue for next execution
                    self._add_to_queue(task)
                else:
                    # Task failed, already handled in _execute_task
                    pass

            # Clean up old tasks periodically
            if current_time.second == 0:  # Every minute
                self._cleanup_old_tasks()

            time.sleep(self.config.get('scheduler_interval', 1))

        self.logger.info("Scheduler stopped")

    def _cleanup_old_tasks(self):
        """Clean up old executed tasks based on retention policy"""
        retention_days = self.config.get('task_retention_days', 30)
        cutoff_date = datetime.now() - timedelta(days=retention_days)

        self.executed_tasks = [task for task in self.executed_tasks
                               if task.last_run and task.last_run > cutoff_date]

    def start_scheduler(self):
        """Start the scheduler in a background thread"""
        if self.running:
            self.logger.warning("Scheduler already running")
            return

        self.running = True
        self.scheduler_thread = threading.Thread(target=self._run_scheduler_loop, daemon=True)
        self.scheduler_thread.start()
        self.logger.info("Scheduler started in background thread")

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=5)  # Wait up to 5 seconds
        self.logger.info("Scheduler stopped")

    def get_task_status(self, task_id: str) -> Optional[TaskStatus]:
        """Get the status of a specific task"""
        if task_id not in self.tasks:
            return None
        return self.tasks[task_id].status

    def get_all_task_statuses(self) -> Dict[str, TaskStatus]:
        """Get statuses of all tasks"""
        return {task_id: task.status for task_id, task in self.tasks.items()}

    def get_scheduled_tasks(self) -> List[Dict[str, Any]]:
        """Get information about all scheduled tasks"""
        tasks_info = []
        for task in self.tasks.values():
            tasks_info.append({
                'id': task.id,
                'name': task.name,
                'cron_expression': task.cron_expression,
                'timezone': task.timezone,
                'status': task.status.value,
                'priority': task.priority.value,
                'next_run': task.next_run.isoformat() if task.next_run else None,
                'last_run': task.last_run.isoformat() if task.last_run else None,
                'retries': task.retries,
                'max_retries': task.max_retries
            })
        return tasks_info

    def get_conflicts(self) -> List[Dict[str, Any]]:
        """Detect and return scheduling conflicts"""
        conflicts = []
        scheduled_tasks = [task for task in self.tasks.values() if task.status == TaskStatus.SCHEDULED]

        # Compare each task with others for potential conflicts
        for i, task1 in enumerate(scheduled_tasks):
            for j, task2 in enumerate(scheduled_tasks[i+1:], i+1):
                # For now, just check if both tasks have the same next_run time
                if (task1.next_run and task2.next_run and
                    abs((task1.next_run - task2.next_run).total_seconds()) < 60):  # Within 1 minute
                    conflicts.append({
                        'task1': task1.id,
                        'task2': task2.id,
                        'conflict_time': task1.next_run.isoformat(),
                        'type': 'time_overlap',
                        'severity': 'medium'
                    })

        return conflicts

    def resolve_conflicts(self) -> bool:
        """Attempt to resolve detected scheduling conflicts"""
        conflicts = self.get_conflicts()
        if not conflicts:
            return True

        resolved = 0
        for conflict in conflicts:
            task1_id = conflict['task1']
            task2_id = conflict['task2']

            # Simple resolution: delay the lower priority task by 1 minute
            task1 = self.tasks[task1_id]
            task2 = self.tasks[task2_id]

            if task1.priority.value < task2.priority.value:
                # Delay task1
                task1.next_run = task1.next_run + timedelta(minutes=1)
                self._add_to_queue(task1)
                resolved += 1
            elif task2.priority.value < task1.priority.value:
                # Delay task2
                task2.next_run = task2.next_run + timedelta(minutes=1)
                self._add_to_queue(task2)
                resolved += 1
            else:
                # Same priority, delay task2 by 30 seconds
                task2.next_run = task2.next_run + timedelta(seconds=30)
                self._add_to_queue(task2)
                resolved += 1

        self.logger.info(f"Resolved {resolved} conflicts")
        return True

    def adjust_schedule(self, task_id: str, new_cron: str = None, new_timezone: str = None) -> bool:
        """Dynamically adjust a task's schedule"""
        if task_id not in self.tasks:
            return False

        task = self.tasks[task_id]

        if new_cron:
            if not self.validate_cron_expression(new_cron):
                self.logger.error(f"Invalid new cron expression: {new_cron}")
                return False
            task.cron_expression = new_cron

        if new_timezone:
            task.timezone = new_timezone

        # Recalculate next run based on new schedule
        task.next_run = self.parse_cron_to_datetime(task.cron_expression, task.timezone)
        self._add_to_queue(task)

        self.logger.info(f"Task {task_id} schedule adjusted")
        return True

    def add_conditional_task(self, condition_func: Callable[[], bool], task_function: Callable, *args, **kwargs) -> str:
        """Add a task that runs based on a condition"""
        task_id = f"conditional_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(self.tasks)}"

        def conditional_wrapper():
            if condition_func():
                return task_function(*args, **kwargs)
            else:
                self.logger.info(f"Condition not met for conditional task {task_id}")
                return None

        self.add_task(
            task_id=task_id,
            name=f"Conditional Task {task_id}",
            cron_expression="*/5 * * * *",  # Check every 5 minutes
            function=conditional_wrapper
        )

        return task_id

    def import_task_schedule(self, schedule_file: str) -> bool:
        """Import task schedule from a JSON file"""
        try:
            with open(schedule_file, 'r') as f:
                schedule_data = json.load(f)

            for task_data in schedule_data.get('tasks', []):
                self.add_task(
                    task_id=task_data['id'],
                    name=task_data['name'],
                    cron_expression=task_data['cron_expression'],
                    function=globals()[task_data['function_name']],  # This would need to be more sophisticated
                    args=task_data.get('args', []),
                    kwargs=task_data.get('kwargs', {}),
                    timezone=task_data.get('timezone'),
                    priority=TaskPriority(task_data.get('priority', TaskPriority.NORMAL.value)),
                    max_retries=task_data.get('max_retries', 3),
                    timeout=task_data.get('timeout', 300)
                )

            self.logger.info(f"Imported schedule from {schedule_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to import schedule: {str(e)}")
            return False

    def export_task_schedule(self, schedule_file: str) -> bool:
        """Export current task schedule to a JSON file"""
        try:
            schedule_data = {
                'exported_at': datetime.now().isoformat(),
                'tasks': []
            }

            for task in self.tasks.values():
                task_data = {
                    'id': task.id,
                    'name': task.name,
                    'cron_expression': task.cron_expression,
                    'timezone': task.timezone,
                    'priority': task.priority.value,
                    'max_retries': task.max_retries,
                    'timeout': task.timeout
                }
                schedule_data['tasks'].append(task_data)

            with open(schedule_file, 'w') as f:
                json.dump(schedule_data, f, indent=2)

            self.logger.info(f"Exported schedule to {schedule_file}")
            return True
        except Exception as e:
            self.logger.error(f"Failed to export schedule: {str(e)}")
            return False


# Example task functions for testing
def example_task_function(task_name: str, data: Dict[str, Any]):
    """Example task function for testing"""
    print(f"Executing task: {task_name}")
    print(f"Data: {data}")
    # Simulate some work
    time.sleep(2)
    return f"Task {task_name} completed at {datetime.now()}"


def check_system_health():
    """Example condition function for conditional tasks"""
    import psutil
    cpu_percent = psutil.cpu_percent(interval=1)
    return cpu_percent < 80  # Only run if CPU is below 80%


if __name__ == "__main__":
    # Example usage
    scheduler = SchedulerCron()

    # Add some example tasks
    scheduler.add_task(
        task_id="daily_ceo_briefing",
        name="Daily CEO Briefing",
        cron_expression="0 9 * * *",  # Every day at 9 AM
        function=example_task_function,
        args=["daily_briefing", {"type": "ceo_report", "frequency": "daily"}],
        timezone="US/Eastern",
        priority=TaskPriority.HIGH
    )

    scheduler.add_task(
        task_id="weekly_sync",
        name="Weekly Cloud Sync",
        cron_expression="0 2 * * 0",  # Every Sunday at 2 AM
        function=example_task_function,
        args=["weekly_sync", {"type": "cloud_sync", "frequency": "weekly"}],
        timezone="UTC",
        priority=TaskPriority.NORMAL
    )

    scheduler.add_task(
        task_id="health_check",
        name="System Health Check",
        cron_expression="*/15 * * * *",  # Every 15 minutes
        function=example_task_function,
        args=["health_check", {"type": "system_monitor", "frequency": "15min"}],
        timezone="UTC",
        priority=TaskPriority.LOW
    )

    # Print initial task statuses
    print("Initial task statuses:")
    for task_id, status in scheduler.get_all_task_statuses().items():
        print(f"  {task_id}: {status.value}")

    # Get scheduled tasks info
    scheduled_tasks = scheduler.get_scheduled_tasks()
    print(f"\nScheduled tasks: {len(scheduled_tasks)}")
    for task in scheduled_tasks:
        print(f"  {task['name']}: {task['cron_expression']} (next: {task['next_run']})")

    # Check for conflicts
    conflicts = scheduler.get_conflicts()
    print(f"\nConflicts found: {len(conflicts)}")
    for conflict in conflicts:
        print(f"  {conflict}")

    # Start scheduler
    scheduler.start_scheduler()
    print("\nScheduler started in background")

    # Let it run for a few seconds to see it in action
    time.sleep(10)

    # Stop scheduler
    scheduler.stop_scheduler()
    print("Scheduler stopped")