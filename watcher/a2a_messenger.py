"""
Platinum Tier A2A Messenger - Agent-to-Agent Communication

Facilitates communication between different agents in the system, coordinates complex multi-step processes,
shares status and progress information, handles handoffs between different agents, supports message queuing
and retries, and maintains communication logs.
"""
import json
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Any, Callable
from dataclasses import dataclass
from enum import Enum
import logging
import threading
import queue
from dataclasses import asdict


class MessageType(Enum):
    TASK_ASSIGNMENT = "task_assignment"
    STATUS_UPDATE = "status_update"
    PROGRESS_REPORT = "progress_report"
    HANDOFF_REQUEST = "handoff_request"
    HANDOFF_CONFIRMATION = "handoff_confirmation"
    ERROR_NOTIFICATION = "error_notification"
    COMPLETION = "completion"
    HEARTBEAT = "heartbeat"


class MessagePriority(Enum):
    LOW = 1
    NORMAL = 5
    HIGH = 10
    CRITICAL = 20


@dataclass
class Message:
    id: str
    sender: str
    recipient: str
    type: MessageType
    content: Dict[str, Any]
    timestamp: datetime
    priority: MessagePriority
    correlation_id: Optional[str] = None
    reply_to: Optional[str] = None
    ttl: int = 3600  # Time to live in seconds
    retries: int = 0
    max_retries: int = 3


class AgentStatus(Enum):
    IDLE = "idle"
    BUSY = "busy"
    OFFLINE = "offline"
    ERROR = "error"


@dataclass
class AgentInfo:
    name: str
    status: AgentStatus
    capabilities: List[str]
    last_heartbeat: datetime
    message_queue: queue.Queue


class A2AMessenger:
    """
    Platinum Tier A2A Messenger - Agent-to-Agent Communication
    """

    def __init__(self, config_path: Optional[str] = None):
        """Initialize the A2A Messenger system"""
        self.config = self._load_config(config_path)
        self.communication_logs_dir = Path(self.config.get('communication_logs_dir', 'AI_Employee_Vault/Platinum/Agent_Communication'))
        self.agents_registry_dir = Path(self.config.get('agents_registry_dir', 'AI_Employee_Vault/Platinum/Agent_Registry'))

        # Initialize agent registry and message queues
        self.agents: Dict[str, AgentInfo] = {}
        self.message_queues: Dict[str, queue.Queue] = {}
        self.sent_messages: List[Message] = []
        self.received_messages: Dict[str, List[Message]] = {}
        self.message_acknowledgments: Dict[str, bool] = {}
        self.processing_lock = threading.Lock()

        # Setup logging
        self._setup_logging()
        self.communication_logs_dir.mkdir(parents=True, exist_ok=True)
        self.agents_registry_dir.mkdir(parents=True, exist_ok=True)

    def _load_config(self, config_path: Optional[str]) -> Dict[str, Any]:
        """Load configuration from file or use defaults"""
        default_config = {
            'communication_logs_dir': 'AI_Employee_Vault/Platinum/Agent_Communication',
            'agents_registry_dir': 'AI_Employee_Vault/Platinum/Agent_Registry',
            'max_message_size': 1024 * 1024,  # 1MB
            'message_retention_hours': 24,
            'retry_interval': 30,  # seconds
            'max_retries': 3,
            'queue_size': 1000
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
        """Setup logging for the A2A Messenger"""
        log_file = self.communication_logs_dir / f"communication_{datetime.now().strftime('%Y%m%d')}.log"
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler(log_file),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger(__name__)

    def register_agent(self, name: str, capabilities: List[str]) -> bool:
        """Register a new agent in the system"""
        if name in self.agents:
            self.logger.warning(f"Agent {name} already registered")
            return False

        agent_queue = queue.Queue(maxsize=self.config.get('queue_size', 1000))
        agent_info = AgentInfo(
            name=name,
            status=AgentStatus.IDLE,  # IDLE means available and ready
            capabilities=capabilities,
            last_heartbeat=datetime.now(),
            message_queue=agent_queue
        )

        self.agents[name] = agent_info
        self.message_queues[name] = agent_queue
        self.received_messages[name] = []

        # Save agent info to registry
        agent_file = self.agents_registry_dir / f"{name}_agent.json"
        with open(agent_file, 'w') as f:
            json.dump({
                'name': name,
                'status': agent_info.status.value,
                'capabilities': capabilities,
                'last_heartbeat': agent_info.last_heartbeat.isoformat(),
                'timestamp': datetime.now().isoformat()
            }, f, indent=2)

        self.logger.info(f"Agent {name} registered with capabilities: {capabilities}")
        return True

    def unregister_agent(self, name: str) -> bool:
        """Unregister an agent from the system"""
        if name not in self.agents:
            return False

        # Mark as offline
        self.agents[name].status = AgentStatus.OFFLINE
        del self.agents[name]
        del self.message_queues[name]
        del self.received_messages[name]

        # Remove from registry
        agent_file = self.agents_registry_dir / f"{name}_agent.json"
        if agent_file.exists():
            agent_file.unlink()

        self.logger.info(f"Agent {name} unregistered")
        return True

    def send_message(self, message: Message) -> bool:
        """Send a message to a recipient agent"""
        if message.recipient not in self.message_queues:
            self.logger.error(f"Recipient agent {message.recipient} not found")
            return False

        # Check message size - convert enums to strings for JSON serialization
        message_dict = asdict(message)
        message_dict['type'] = message_dict['type'].value
        message_dict['priority'] = message_dict['priority'].value
        if message_dict['correlation_id'] is None:
            message_dict['correlation_id'] = None
        if message_dict['reply_to'] is None:
            message_dict['reply_to'] = None

        message_size = len(json.dumps(message_dict, default=str))
        if message_size > self.config.get('max_message_size', 1024 * 1024):
            self.logger.error(f"Message too large: {message_size} bytes")
            return False

        # Check TTL
        if (datetime.now() - message.timestamp).total_seconds() > message.ttl:
            self.logger.error(f"Message expired (TTL exceeded)")
            return False

        try:
            # Add to recipient's queue
            self.message_queues[message.recipient].put(message, block=False)

            # Track sent message
            self.sent_messages.append(message)

            # Add to recipient's received messages
            if message.recipient not in self.received_messages:
                self.received_messages[message.recipient] = []
            self.received_messages[message.recipient].append(message)

            # Log the message
            self._log_message(message, "sent")

            self.logger.info(f"Message sent from {message.sender} to {message.recipient} (type: {message.type.value})")
            return True

        except queue.Full:
            self.logger.error(f"Recipient queue for {message.recipient} is full")
            return False
        except Exception as e:
            self.logger.error(f"Failed to send message: {str(e)}")
            return False

    def broadcast_message(self, message_template: Message, recipients: List[str]) -> Dict[str, bool]:
        """Broadcast a message to multiple recipients"""
        results = {}

        for recipient in recipients:
            # Create a copy of the message for each recipient
            broadcast_msg = Message(
                id=f"{message_template.id}_{recipient}",
                sender=message_template.sender,
                recipient=recipient,
                type=message_template.type,
                content=message_template.content,
                timestamp=message_template.timestamp,
                priority=message_template.priority,
                correlation_id=message_template.correlation_id,
                reply_to=message_template.reply_to,
                ttl=message_template.ttl,
                retries=message_template.retries,
                max_retries=message_template.max_retries
            )

            results[recipient] = self.send_message(broadcast_msg)

        return results

    def receive_message(self, agent_name: str) -> Optional[Message]:
        """Receive a message for an agent"""
        if agent_name not in self.message_queues:
            self.logger.error(f"Agent {agent_name} not registered")
            return None

        try:
            # Non-blocking get
            message = self.message_queues[agent_name].get_nowait()

            # Update agent status to busy if this is a task assignment
            if message.type == MessageType.TASK_ASSIGNMENT:
                self.agents[agent_name].status = AgentStatus.BUSY

            self.logger.info(f"Message received by {agent_name} (type: {message.type.value})")
            return message

        except queue.Empty:
            return None

    def get_messages_for_agent(self, agent_name: str, count: int = 10) -> List[Message]:
        """Get multiple messages for an agent"""
        if agent_name not in self.received_messages:
            return []

        # Return the most recent messages
        all_messages = self.received_messages[agent_name]
        return all_messages[-count:]

    def acknowledge_message(self, message_id: str, recipient: str) -> bool:
        """Acknowledge receipt of a message"""
        ack_key = f"{recipient}:{message_id}"
        self.message_acknowledgments[ack_key] = True

        # Log acknowledgment
        ack_log = {
            'timestamp': datetime.now().isoformat(),
            'message_id': message_id,
            'recipient': recipient,
            'action': 'acknowledged'
        }

        ack_file = self.communication_logs_dir / f"acknowledgments_{datetime.now().strftime('%Y%m%d')}.log"
        with open(ack_file, 'a') as f:
            f.write(json.dumps(ack_log) + '\n')

        return True

    def handle_message_retry(self, message: Message) -> bool:
        """Handle message retry logic"""
        if message.retries >= message.max_retries:
            self.logger.error(f"Message {message.id} failed after {message.max_retries} retries")
            # Log failure
            failure_log = {
                'timestamp': datetime.now().isoformat(),
                'message_id': message.id,
                'sender': message.sender,
                'recipient': message.recipient,
                'error': 'Max retries exceeded',
                'action': 'failed'
            }
            self._log_event(failure_log)
            return False

        # Increment retry count
        message.retries += 1

        # Wait before retry
        time.sleep(self.config.get('retry_interval', 30))

        # Try sending again
        return self.send_message(message)

    def coordinate_workflow(self, workflow_id: str, tasks: List[Dict[str, Any]]) -> bool:
        """Coordinate a multi-step workflow between agents"""
        self.logger.info(f"Starting workflow coordination: {workflow_id}")

        for i, task in enumerate(tasks):
            # Find suitable agent for the task
            agent_name = self._find_suitable_agent(task.get('required_capabilities', []))

            if not agent_name:
                self.logger.error(f"No suitable agent found for task {i}")
                return False

            # Create task assignment message
            task_msg = Message(
                id=f"{workflow_id}_task_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                sender="workflow_coordinator",
                recipient=agent_name,
                type=MessageType.TASK_ASSIGNMENT,
                content={
                    'workflow_id': workflow_id,
                    'task_id': i,
                    'task_definition': task,
                    'task_sequence': i,
                    'total_tasks': len(tasks)
                },
                timestamp=datetime.now(),
                priority=MessagePriority.NORMAL,
                correlation_id=workflow_id
            )

            # Send task assignment
            success = self.send_message(task_msg)
            if not success:
                self.logger.error(f"Failed to assign task {i} to agent {agent_name}")
                return False

            self.logger.info(f"Task {i} assigned to agent {agent_name}")

        return True

    def _find_suitable_agent(self, required_capabilities: List[str]) -> Optional[str]:
        """Find an agent that can handle the required capabilities"""
        available_agents = [name for name, info in self.agents.items()
                           if info.status == AgentStatus.IDLE]

        for agent_name in available_agents:
            agent_info = self.agents[agent_name]
            if all(cap in agent_info.capabilities for cap in required_capabilities):
                return agent_name

        return None

    def handle_agent_handoff(self, current_agent: str, next_agent: str, context: Dict[str, Any]) -> bool:
        """Handle handoff of work between agents"""
        if current_agent not in self.agents or next_agent not in self.agents:
            self.logger.error(f"Handoff failed: one or both agents not registered")
            return False

        # Create handoff request message
        handoff_msg = Message(
            id=f"handoff_{current_agent}_to_{next_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            sender=current_agent,
            recipient=next_agent,
            type=MessageType.HANDOFF_REQUEST,
            content={
                'from_agent': current_agent,
                'to_agent': next_agent,
                'context': context,
                'handoff_timestamp': datetime.now().isoformat()
            },
            timestamp=datetime.now(),
            priority=MessagePriority.HIGH
        )

        # Send handoff request
        success = self.send_message(handoff_msg)
        if success:
            # Update agent statuses
            self.agents[current_agent].status = AgentStatus.IDLE
            self.agents[next_agent].status = AgentStatus.BUSY

        return success

    def update_agent_status(self, agent_name: str, status: AgentStatus) -> bool:
        """Update an agent's status"""
        if agent_name not in self.agents:
            return False

        old_status = self.agents[agent_name].status
        self.agents[agent_name].status = status
        self.agents[agent_name].last_heartbeat = datetime.now()

        # Log status change
        status_log = {
            'timestamp': datetime.now().isoformat(),
            'agent': agent_name,
            'old_status': old_status.value,
            'new_status': status.value,
            'action': 'status_update'
        }
        self._log_event(status_log)

        return True

    def get_agent_status(self, agent_name: str) -> Optional[AgentStatus]:
        """Get an agent's current status"""
        if agent_name not in self.agents:
            return None
        return self.agents[agent_name].status

    def get_all_agent_statuses(self) -> Dict[str, AgentStatus]:
        """Get all agents' statuses"""
        return {name: info.status for name, info in self.agents.items()}

    def send_status_update(self, agent_name: str, status_data: Dict[str, Any]) -> bool:
        """Send a status update message"""
        if agent_name not in self.agents:
            return False

        status_msg = Message(
            id=f"status_update_{agent_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            sender=agent_name,
            recipient="system_monitor",  # Or broadcast to all
            type=MessageType.STATUS_UPDATE,
            content=status_data,
            timestamp=datetime.now(),
            priority=MessagePriority.NORMAL
        )

        return self.send_message(status_msg)

    def send_error_notification(self, source_agent: str, error_details: Dict[str, Any]) -> bool:
        """Send an error notification"""
        error_msg = Message(
            id=f"error_{source_agent}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
            sender=source_agent,
            recipient="error_handler",
            type=MessageType.ERROR_NOTIFICATION,
            content=error_details,
            timestamp=datetime.now(),
            priority=MessagePriority.HIGH
        )

        # Also update agent status to ERROR
        self.update_agent_status(source_agent, AgentStatus.ERROR)

        return self.send_message(error_msg)

    def _log_message(self, message: Message, action: str):
        """Log message to file"""
        log_entry = {
            'timestamp': message.timestamp.isoformat(),
            'message_id': message.id,
            'sender': message.sender,
            'recipient': message.recipient,
            'type': message.type.value,
            'priority': message.priority.value,
            'action': action
        }

        log_file = self.communication_logs_dir / f"messages_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(log_entry, default=str) + '\n')

    def _log_event(self, event_data: Dict[str, Any]):
        """Log an event to file"""
        log_file = self.communication_logs_dir / f"events_{datetime.now().strftime('%Y%m%d')}.log"
        with open(log_file, 'a') as f:
            f.write(json.dumps(event_data, default=str) + '\n')

    def cleanup_old_logs(self):
        """Clean up old log files based on retention policy"""
        import os
        from datetime import timedelta

        retention_hours = self.config.get('message_retention_hours', 24)
        cutoff_time = datetime.now() - timedelta(hours=retention_hours)

        for log_file in self.communication_logs_dir.glob("*.log"):
            if datetime.fromtimestamp(log_file.stat().st_mtime) < cutoff_time:
                try:
                    log_file.unlink()
                    self.logger.info(f"Deleted old log file: {log_file}")
                except Exception as e:
                    self.logger.error(f"Failed to delete old log file {log_file}: {e}")

    def start_heartbeat_monitoring(self, interval: int = 60):
        """Start monitoring agent heartbeats"""
        self.logger.info(f"Starting heartbeat monitoring with {interval}s interval")

        def heartbeat_worker():
            while True:
                current_time = datetime.now()

                # Check each agent's last heartbeat
                for agent_name, agent_info in self.agents.items():
                    # Only consider an agent truly offline if it hasn't had any contact for a longer period
                    # (e.g., 10 minutes instead of 2 minutes based on the interval)
                    long_timeout = max(600, interval * 2)  # At least 10 minutes or 2x interval

                    if (current_time - agent_info.last_heartbeat).total_seconds() > long_timeout:
                        # Agent may be offline (hasn't been active for a significant time)
                        if agent_info.status not in [AgentStatus.OFFLINE, AgentStatus.ERROR]:
                            self.logger.debug(f"Agent {agent_name} marked as offline (inactive for {long_timeout}s)")
                            self.update_agent_status(agent_name, AgentStatus.OFFLINE)
                    else:
                        # Agent is responsive or has been recently active
                        if agent_info.status == AgentStatus.OFFLINE:
                            self.update_agent_status(agent_name, AgentStatus.IDLE)

                time.sleep(interval)

        # Start heartbeat monitoring in background
        heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
        heartbeat_thread.start()

        return heartbeat_thread


if __name__ == "__main__":
    # Example usage
    messenger = A2AMessenger()

    # Register some agents
    messenger.register_agent("inbox_router", ["file_processing", "routing"])
    messenger.register_agent("task_completer", ["task_management", "file_move"])
    messenger.register_agent("scheduler", ["time_management", "scheduling"])

    # Create and send a message
    test_message = Message(
        id="test_msg_1",
        sender="inbox_router",
        recipient="task_completer",
        type=MessageType.TASK_ASSIGNMENT,
        content={
            "task": "move_file_to_done",
            "file_path": "AI_Employee_Vault/Needs_Action/test_task.md",
            "priority": "high"
        },
        timestamp=datetime.now(),
        priority=MessagePriority.HIGH
    )

    success = messenger.send_message(test_message)
    print(f"Message sent successfully: {success}")

    # Receive the message
    received_msg = messenger.receive_message("task_completer")
    if received_msg:
        print(f"Received message: {received_msg.type.value} from {received_msg.sender}")

    # Update agent status
    messenger.update_agent_status("task_completer", AgentStatus.BUSY)
    print(f"Task completer status: {messenger.get_agent_status('task_completer')}")

    # Check all statuses
    all_statuses = messenger.get_all_agent_statuses()
    print(f"All agent statuses: {all_statuses}")

    # Send a status update
    messenger.send_status_update("inbox_router", {
        "files_processed": 5,
        "errors": 0,
        "uptime": "2h 30m"
    })

    # Coordinate a simple workflow
    workflow_tasks = [
        {"required_capabilities": ["file_processing"], "task": "read_inbox"},
        {"required_capabilities": ["task_management"], "task": "create_plan"},
        {"required_capabilities": ["file_processing"], "task": "update_dashboard"}
    ]
    workflow_success = messenger.coordinate_workflow("daily_processing", workflow_tasks)
    print(f"Workflow coordination success: {workflow_success}")

    print("A2A Messenger example completed")