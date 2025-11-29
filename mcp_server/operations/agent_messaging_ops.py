"""
Agent Messaging Operations
Handles agent DMs and message queries
"""

import asyncio
import os
import sys
from typing import List, Dict, Optional

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from agent_messaging import MessageRouter, MessageViewer, AGENT_PERSONAS

# Global instances
_router = None
_viewer = None
_event_loop = None


def _get_event_loop():
    """Get or create event loop for async operations"""
    global _event_loop
    if _event_loop is None:
        _event_loop = asyncio.new_event_loop()
        asyncio.set_event_loop(_event_loop)
    return _event_loop


def _get_router():
    """Get or create MessageRouter"""
    global _router
    if _router is None:
        _router = MessageRouter()
        loop = _get_event_loop()
        loop.run_until_complete(_router.connect())
    return _router


def _get_viewer():
    """Get or create MessageViewer"""
    global _viewer
    if _viewer is None:
        _viewer = MessageViewer()
        loop = _get_event_loop()
        loop.run_until_complete(_viewer.connect())
        loop.run_until_complete(_viewer.start_viewing(print_messages=False))
    return _viewer


async def send_dm_async(from_user: str, to_agent: str, content: str) -> Dict:
    """Send a DM to an agent (async)"""
    router = _get_router()
    message = await router.send_dm(from_user, to_agent, content)
    return {
        "success": True,
        "message": message.to_dict()
    }


def send_dm(from_user: str, to_agent: str, content: str) -> Dict:
    """Send a DM to an agent"""
    loop = _get_event_loop()
    return loop.run_until_complete(send_dm_async(from_user, to_agent, content))


def list_agents() -> Dict:
    """List all available agents"""
    return {
        "success": True,
        "agents": AGENT_PERSONAS,
        "count": len(AGENT_PERSONAS)
    }


def get_messages(agent_name: Optional[str] = None) -> Dict:
    """Get messages (all or for specific agent)"""
    viewer = _get_viewer()

    if agent_name:
        messages = viewer.get_agent_messages(agent_name)
    else:
        messages = viewer.get_all_messages()

    return {
        "success": True,
        "messages": [msg.to_dict() for msg in messages],
        "count": len(messages),
        "agent": agent_name if agent_name else "all"
    }


def get_conversation(user1: str, user2: str) -> Dict:
    """Get conversation between two users"""
    router = _get_router()
    messages = [
        msg for msg in router.message_history
        if (msg.from_user == user1 and msg.to_user == user2) or
           (msg.from_user == user2 and msg.to_user == user1)
    ]

    return {
        "success": True,
        "messages": [msg.to_dict() for msg in messages],
        "count": len(messages),
        "participants": [user1, user2]
    }
