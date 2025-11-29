"""
Agent Messaging System
Handles DMs between humans and agents via NATS queues
"""
import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, asdict
import os

try:
    import nats
    from nats.aio.client import Client as NATS
    NATS_AVAILABLE = True
except ImportError:
    NATS_AVAILABLE = False
    NATS = None

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

NATS_URL = os.environ.get('NATS_URL', 'nats://localhost:4222')
# Namespace all NATS subjects to prevent cross-talk between repos
NATS_NAMESPACE = os.environ.get('NATS_NAMESPACE', 'themultiverse')

# Agent personas - customize for your project
AGENT_PERSONAS = {
    'cynthia': {'name': 'Cynthia', 'role': 'Utopian Researcher'},
    'sylvia': {'name': 'Sylvia', 'role': 'Research Skeptic'},
    'orchestrator': {'name': 'Orchestrator', 'role': 'Coordinator'},
    'tessa': {'name': 'Tessa', 'role': 'Far Future UX Designer'},
    'historian': {'name': 'Historian', 'role': 'Wiki Documentation Updater'},
    'planner': {'name': 'Planner', 'role': 'Project Plan Manager'},
    'ray': {'name': 'Ray', 'role': 'Sci-Fi Tech Visionary'},
    'moss': {'name': 'Moss', 'role': 'Feature Implementer'},
    'roy': {'name': 'Roy', 'role': 'Simulation Maintainer'},
    'priya': {'name': 'Priya', 'role': 'Quantitative Validator'}
}


@dataclass
class Message:
    """Represents a message in the system"""
    id: str
    from_user: str  # username or agent name
    to_user: str    # username or agent name
    content: str
    timestamp: str
    message_type: str = 'dm'  # dm, broadcast, system
    thread_id: Optional[str] = None

    def to_dict(self):
        return asdict(self)

    @classmethod
    def from_dict(cls, data: dict):
        return cls(**data)


class AgentMessageQueue:
    """
    Message queue for an individual agent.
    Subscribes to agent's inbox and processes messages.
    """

    def __init__(self, agent_name: str, message_handler: Optional[Callable] = None):
        self.agent_name = agent_name
        self.inbox_subject = f"{NATS_NAMESPACE}.agents.{agent_name}.inbox"
        self.outbox_subject = f"{NATS_NAMESPACE}.agents.{agent_name}.outbox"
        self.message_handler = message_handler or self.default_message_handler
        self.nc: Optional[NATS] = None
        self.subscription = None

    async def connect(self):
        """Connect to NATS"""
        if not NATS_AVAILABLE:
            logger.error("NATS not available")
            return False

        try:
            self.nc = await asyncio.wait_for(
                nats.connect(NATS_URL),
                timeout=5.0
            )
            logger.info(f"Agent {self.agent_name} connected to NATS")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            return False

    async def start_listening(self):
        """Start listening to inbox"""
        if not self.nc:
            if not await self.connect():
                return

        async def message_callback(msg):
            try:
                data = json.loads(msg.data.decode())
                message = Message.from_dict(data)
                logger.info(f"[{self.agent_name}] Received message from {message.from_user}: {message.content[:50]}...")

                # Process message
                await self.message_handler(message)

            except Exception as e:
                logger.error(f"Error processing message: {e}")

        self.subscription = await self.nc.subscribe(self.inbox_subject, cb=message_callback)
        logger.info(f"Agent {self.agent_name} listening on {self.inbox_subject}")

    async def send_message(self, to_user: str, content: str, thread_id: Optional[str] = None):
        """Send a message from this agent"""
        if not self.nc:
            await self.connect()

        message = Message(
            id=f"msg_{datetime.utcnow().timestamp()}",
            from_user=f"agent_{self.agent_name}",
            to_user=to_user,
            content=content,
            timestamp=datetime.utcnow().isoformat(),
            thread_id=thread_id
        )

        # Publish to recipient's inbox if they're an agent
        if to_user.startswith('agent_'):
            recipient_agent = to_user.replace('agent_', '')
            subject = f"{NATS_NAMESPACE}.agents.{recipient_agent}.inbox"
        else:
            # For humans, publish to general message stream
            subject = f"{NATS_NAMESPACE}.messages.dm.{to_user}"

        await self.nc.publish(subject, json.dumps(message.to_dict()).encode())

        # Also publish to outbox for tracking
        await self.nc.publish(self.outbox_subject, json.dumps(message.to_dict()).encode())

        logger.info(f"[{self.agent_name}] Sent message to {to_user}")

    async def default_message_handler(self, message: Message):
        """Default message handler - just logs the message"""
        logger.info(f"[{self.agent_name}] Received: {message.content}")

        # Echo response (simple example)
        response = f"Agent {self.agent_name} received your message: '{message.content[:50]}...'"
        await self.send_message(message.from_user, response, message.thread_id)

    async def close(self):
        """Close connection"""
        if self.nc:
            await self.nc.close()


class MessageRouter:
    """
    Routes messages between humans and agents.
    Handles DMs and broadcasts.
    """

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.message_history: List[Message] = []

    async def connect(self):
        """Connect to NATS"""
        if not NATS_AVAILABLE:
            logger.error("NATS not available")
            return False

        try:
            self.nc = await asyncio.wait_for(
                nats.connect(NATS_URL),
                timeout=5.0
            )
            logger.info("MessageRouter connected to NATS")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            return False

    async def send_dm(self, from_user: str, to_agent: str, content: str):
        """Send a DM from a human to an agent"""
        if not self.nc:
            await self.connect()

        message = Message(
            id=f"msg_{datetime.utcnow().timestamp()}",
            from_user=from_user,
            to_user=f"agent_{to_agent}",
            content=content,
            timestamp=datetime.utcnow().isoformat()
        )

        # Route to agent's inbox
        subject = f"{NATS_NAMESPACE}.agents.{to_agent}.inbox"
        await self.nc.publish(subject, json.dumps(message.to_dict()).encode())

        # Store in message history
        self.message_history.append(message)

        # Also publish to all-messages stream for viewing
        await self.nc.publish(f"{NATS_NAMESPACE}.messages.all", json.dumps(message.to_dict()).encode())

        logger.info(f"Routed DM from {from_user} to agent {to_agent}")
        return message

    async def subscribe_all_messages(self, callback):
        """Subscribe to all messages for viewing"""
        if not self.nc:
            await self.connect()

        async def message_callback(msg):
            try:
                data = json.loads(msg.data.decode())
                message = Message.from_dict(data)
                await callback(message)
            except Exception as e:
                logger.error(f"Error in message callback: {e}")

        await self.nc.subscribe(f"{NATS_NAMESPACE}.messages.all", cb=message_callback)
        logger.info("Subscribed to all messages stream")

    async def get_conversation(self, user1: str, user2: str) -> List[Message]:
        """Get conversation history between two users"""
        return [
            msg for msg in self.message_history
            if (msg.from_user == user1 and msg.to_user == user2) or
               (msg.from_user == user2 and msg.to_user == user1)
        ]


class MessageViewer:
    """
    Views all messages in the system.
    Provides a read-only interface to the message stream.
    """

    def __init__(self):
        self.nc: Optional[NATS] = None
        self.messages: List[Message] = []

    async def connect(self):
        """Connect to NATS"""
        if not NATS_AVAILABLE:
            logger.error("NATS not available")
            return False

        try:
            self.nc = await asyncio.wait_for(
                nats.connect(NATS_URL),
                timeout=5.0
            )
            logger.info("MessageViewer connected to NATS")
            return True
        except Exception as e:
            logger.error(f"Failed to connect to NATS: {e}")
            return False

    async def start_viewing(self, print_messages: bool = True):
        """Start viewing all messages"""
        if not self.nc:
            await self.connect()

        async def message_callback(msg):
            try:
                data = json.loads(msg.data.decode())
                message = Message.from_dict(data)
                self.messages.append(message)

                if print_messages:
                    print(f"\n📨 [{message.timestamp}]")
                    print(f"   From: {message.from_user}")
                    print(f"   To: {message.to_user}")
                    print(f"   Message: {message.content}")

            except Exception as e:
                logger.error(f"Error viewing message: {e}")

        # Subscribe to all message subjects
        await self.nc.subscribe(f"{NATS_NAMESPACE}.messages.>", cb=message_callback)
        await self.nc.subscribe(f"{NATS_NAMESPACE}.agents.*.inbox", cb=message_callback)
        await self.nc.subscribe(f"{NATS_NAMESPACE}.agents.*.outbox", cb=message_callback)

        logger.info("MessageViewer subscribed to all message streams")

    def get_all_messages(self) -> List[Message]:
        """Get all messages"""
        return self.messages

    def get_agent_messages(self, agent_name: str) -> List[Message]:
        """Get all messages for a specific agent"""
        return [
            msg for msg in self.messages
            if msg.from_user == f"agent_{agent_name}" or msg.to_user == f"agent_{agent_name}"
        ]


# Example usage
async def demo():
    """Demonstration of the messaging system"""

    # Create a message router
    router = MessageRouter()
    await router.connect()

    # Create a message viewer
    viewer = MessageViewer()
    await viewer.start_viewing()

    # Create agent queue for Sylvia
    sylvia = AgentMessageQueue('sylvia')
    await sylvia.start_listening()

    # Create agent queue for Roy
    roy = AgentMessageQueue('roy')
    await roy.start_listening()

    # Send some test messages
    await router.send_dm('alice@example.com', 'sylvia', 'Hello Sylvia! Can you help me with my homework?')
    await asyncio.sleep(1)

    await router.send_dm('bob@example.com', 'roy', 'Hi Roy, when does the next class start?')
    await asyncio.sleep(1)

    # Let agents respond
    await asyncio.sleep(2)

    print("\n" + "="*60)
    print("MESSAGE HISTORY")
    print("="*60)
    for msg in viewer.get_all_messages():
        print(f"{msg.from_user} → {msg.to_user}: {msg.content[:50]}...")

    # Keep running
    await asyncio.sleep(10)

    # Cleanup
    await sylvia.close()
    await roy.close()


if __name__ == '__main__':
    if NATS_AVAILABLE:
        asyncio.run(demo())
    else:
        print("NATS not available. Please install: pip install nats-py")
