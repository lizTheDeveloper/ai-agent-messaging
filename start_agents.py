"""
Start all agent message queue listeners
Each agent runs in its own task and processes messages from their inbox
"""
import asyncio
import logging
from agent_messaging import AgentMessageQueue, AGENT_PERSONAS

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Start all agent listeners"""
    print("\n" + "="*60)
    print("🤖 STARTING AGENT MESSAGE LISTENERS")
    print("="*60)
    print()

    # Create agent queues
    agents = {}
    for agent_id in AGENT_PERSONAS.keys():
        agent = AgentMessageQueue(agent_id)
        agents[agent_id] = agent
        print(f"✓ Created queue for {AGENT_PERSONAS[agent_id]['name']} ({agent_id})")

    # Connect all agents
    print("\n📡 Connecting agents to NATS...")
    for agent_id, agent in agents.items():
        success = await agent.connect()
        if success:
            print(f"  ✓ {agent_id} connected")
        else:
            print(f"  ✗ {agent_id} failed to connect")

    # Start listening
    print("\n👂 Starting message listeners...")
    for agent_id, agent in agents.items():
        await agent.start_listening()
        print(f"  ✓ {agent_id} listening on agents.{agent_id}.inbox")

    print("\n" + "="*60)
    print("✅ ALL AGENTS ONLINE AND LISTENING")
    print("="*60)
    print("\nAgents will now respond to messages automatically.")
    print("Press Ctrl+C to stop all agents\n")

    # Keep running
    try:
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        print("\n\n🛑 Shutting down agents...")
        for agent in agents.values():
            await agent.close()
        print("✓ All agents stopped\n")


if __name__ == '__main__':
    asyncio.run(main())
