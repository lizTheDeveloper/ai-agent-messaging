# Agent Messaging System

A NATS-based messaging system for AI agents and humans to communicate via DMs and message queues.

## Components

### 1. **agent_messaging.py** - Core messaging infrastructure

- `AgentMessageQueue` - Subscribe to an agent's inbox and send messages
- `MessageRouter` - Route DMs between humans and agents
- `MessageViewer` - Read all messages in the system
- `Message` - Message data structure

### 2. **agent_messaging_web.py** - Web frontend

- View all messages in real-time
- Send DMs to any agent
- Filter messages by agent
- Auto-refreshing UI

### 3. **start_agents.py** - Agent runner

Starts all 12 agents listening to their message queues:
- Sylvia (Teaching Assistant)
- Roy (Course Coordinator)
- Cynthia (Student Support)
- Moss (Technical Support)
- Tessa (Community Manager)
- Historian (Knowledge Keeper)
- Architect (System Designer)
- Ray (Learning Facilitator)
- Orchestrator (Workflow Coordinator)
- Monitor (System Observer)
- Aetherix (Matrix Manager)
- Morgan (Research Assistant)

## Architecture

```
┌─────────────┐
│   Human     │
│  (Browser)  │
└──────┬──────┘
       │ HTTP
       ▼
┌─────────────────┐
│  Web Frontend   │
│  (port 5002)    │
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │   Router   │
    └──────┬─────┘
           │ NATS
           ▼
    ┌──────────────────────────────┐
    │    NATS Message Broker       │
    │  (nats://localhost:4222)     │
    └──┬───────────────────────┬───┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│ agents.     │         │ agents.     │
│ sylvia.     │         │ roy.        │
│ inbox       │         │ inbox       │
└──────┬──────┘         └──────┬──────┘
       │                       │
       ▼                       ▼
┌─────────────┐         ┌─────────────┐
│   Sylvia    │         │    Roy      │
│   Agent     │         │   Agent     │
└─────────────┘         └─────────────┘
```

## Message Flow

### Sending a DM (Human → Agent)

1. Human sends DM via web UI
2. Router publishes to `agents.{agent_name}.inbox`
3. Agent's queue receives message
4. Agent processes and responds
5. Response published to `messages.dm.{human_email}`
6. Response also published to `messages.all` stream
7. Web UI displays response

### Agent-to-Agent Communication

```python
await sylvia.send_message('agent_roy', 'Hey Roy, can you help with this?')
```

1. Message published to `agents.roy.inbox`
2. Roy's queue receives it
3. Roy processes and responds
4. Response sent to `agents.sylvia.inbox`

## NATS Topics

```
agents.{agent_name}.inbox     - Agent's incoming messages
agents.{agent_name}.outbox    - Agent's sent messages
messages.all                  - All messages (for viewing)
messages.dm.{user_email}      - DMs to a specific human
```

## Setup

1. **Install dependencies:**
   ```bash
   pip install nats-py flask
   ```

2. **Start NATS server:**
   ```bash
   # macOS
   brew install nats-server
   nats-server

   # Docker
   docker run -p 4222:4222 nats:latest
   ```

3. **Set NATS_URL environment variable:**
   ```bash
   export NATS_URL="nats://orchestrator:orchestrator2024@34.185.163.86:4222"
   ```
   (Already in your .env file!)

## Usage

### Start the agents:

```bash
python start_agents.py
```

This starts all 12 agents listening to their message queues.

### Start the web interface:

```bash
python agent_messaging_web.py
```

Open http://localhost:5002 in your browser.

### Send a DM:

1. Enter your email
2. Select an agent
3. Type your message
4. Click Send

The agent will automatically respond!

### View all messages:

Click "All Messages" in the sidebar to see the full message stream.

### Filter by agent:

Click any agent card to see only their conversations.

## Programmatic Usage

### Create a custom agent:

```python
from agent_messaging import AgentMessageQueue

async def my_handler(message):
    print(f"Received: {message.content}")
    # Custom logic here
    await agent.send_message(
        message.from_user,
        f"Processed: {message.content}"
    )

agent = AgentMessageQueue('custom_agent', message_handler=my_handler)
await agent.connect()
await agent.start_listening()
```

### Send a message:

```python
from agent_messaging import MessageRouter

router = MessageRouter()
await router.connect()
await router.send_dm('alice@example.com', 'sylvia', 'Hello!')
```

### View messages:

```python
from agent_messaging import MessageViewer

viewer = MessageViewer()
await viewer.connect()
await viewer.start_viewing()

# Get all messages
messages = viewer.get_all_messages()

# Get agent-specific messages
sylvia_messages = viewer.get_agent_messages('sylvia')
```

## Integration with Matrix

The agent system is designed to work alongside the existing Matrix integration.

Agents can:
- Receive DMs via NATS (this system)
- Receive messages via Matrix (matrix_integration.py)
- Coordinate between both systems

### Bridge NATS ↔ Matrix:

```python
# In your Matrix bot
async def on_matrix_message(room, message):
    # Forward to NATS
    await router.send_dm(sender_email, 'sylvia', message.body)

# In your NATS agent
async def message_handler(nats_message):
    # Forward response to Matrix
    await matrix_client.room_send(room_id, {
        'msgtype': 'm.text',
        'body': response
    })
```

## Next Steps

### MCP Server Integration

Create an MCP server to expose agent messaging to Claude Code:

```python
# mcp_agent_messaging_server.py
from mcp.server import Server
from agent_messaging import MessageRouter

server = Server("agent-messaging")

@server.tool()
async def dm_agent(agent_name: str, message: str) -> str:
    """Send a DM to an agent"""
    router = MessageRouter()
    await router.send_dm('user@example.com', agent_name, message)
    return f"Message sent to {agent_name}"

@server.tool()
async def list_agents() -> list:
    """List available agents"""
    return list(AGENT_PERSONAS.keys())
```

### Custom Agent Personalities

Update agent handlers to give each agent unique behavior:

```python
# Sylvia - Teaching assistant
async def sylvia_handler(message):
    # Analyze question
    # Generate helpful teaching response
    # Include references to course materials

# Roy - Course coordinator
async def roy_handler(message):
    # Check class schedules
    # Provide enrollment information
    # Coordinate with other agents
```

### Message Persistence

Add database storage:

```python
# Store messages in PostgreSQL
async def store_message(message):
    conn = await asyncpg.connect(DATABASE_URL)
    await conn.execute(
        "INSERT INTO agent_messages (...) VALUES (...)",
        message.id, message.from_user, ...
    )
```

## Troubleshooting

**NATS connection refused:**
- Make sure NATS server is running
- Check NATS_URL is correct
- Try: `nats-server -m 8222` and visit http://localhost:8222

**Agents not receiving messages:**
- Check agents are running (`python start_agents.py`)
- Verify NATS connection in logs
- Test with simple publisher/subscriber

**Web UI not updating:**
- Check browser console for errors
- Verify Flask server is running
- Try manual refresh

## Security

**Production considerations:**
- Add authentication to web UI
- Validate message content
- Rate limit message sending
- Encrypt sensitive message content
- Add message retention policies

## License

Part of The Multiverse School infrastructure
