"""
Basic usage examples for the Agent Messaging System
"""
import asyncio
import sys
import os

# Add parent to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent_messaging import MessageRouter, AGENT_PERSONAS


async def main():
    """Basic usage example"""

    # 1. Create a router
    router = MessageRouter()
    await router.connect()

    # 2. List available agents
    print("Available Agents:")
    for agent_id, info in AGENT_PERSONAS.items():
        print(f"  - {info['name']} ({agent_id}): {info['role']}")

    # 3. Send a message to an agent
    print("\nSending message to Sylvia...")
    message = await router.send_dm(
        from_user="you@example.com",
        to_agent="sylvia",
        content="What are the key concepts in AI?"
    )
    print(f"  ✓ Message sent: {message.id}")

    # 4. Wait for response
    print("\nWaiting for response...")
    await asyncio.sleep(2)

    print("\n✓ Example complete!")


if __name__ == "__main__":
    asyncio.run(main())
