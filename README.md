# AI Agent Messaging System - Template Repository

A complete NATS-based messaging system for AI agents with MCP (Model Context Protocol) integration for Claude Code.

## Features

- **12 AI Agents** with distinct personalities and roles
- **NATS Message Broker** for reliable message routing
- **MCP Server** for Claude Code integration
- **Web UI** for real-time message viewing
- **Namespace Support** for multi-repo deployments
- **Async Python** with modern asyncio patterns

## Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Configure NATS

Set your NATS server URL:

```bash
export NATS_URL="nats://localhost:4222"
export NATS_NAMESPACE="my-project"  # Optional, defaults to 'themultiverse'
```

### 3. Start the Agents

```bash
python start_agents.py
```

### 4. Start the Web UI (Optional)

```bash
python agent_messaging_web.py
```

Open http://localhost:5002

### 5. Use with Claude Code

The MCP server is pre-configured. Just use the tools:

```python
# Send a DM to an agent
dm_agent(
    agent_name="sylvia",
    content="Explain prompt engineering",
    from_user="you@example.com"
)

# List all agents
get_agents()

# View messages
view_messages(agent_name="sylvia")
```

## Available Agents

| Agent | Role |
|-------|------|
| Sylvia | Teaching Assistant |
| Roy | Course Coordinator |
| Cynthia | Student Support |
| Moss | Technical Support |
| Tessa | Community Manager |
| Historian | Knowledge Keeper |
| Architect | System Designer |
| Ray | Learning Facilitator |
| Orchestrator | Workflow Coordinator |
| Monitor | System Observer |
| Aetherix | Matrix Manager |
| Morgan | Research Assistant |

## Architecture

```
┌─────────────┐
│   Claude    │
│    Code     │
└──────┬──────┘
       │ MCP
       ▼
┌─────────────────┐
│  MCP Server     │
└────────┬────────┘
         │
         ▼
    ┌────────────┐
    │   NATS     │
    └──────┬─────┘
           │
    ┌──────┴──────┐
    ▼             ▼
┌─────────┐  ┌─────────┐
│ Agent 1 │  │ Agent 2 │
└─────────┘  └─────────┘
```

## Files

### Core Files
- `agent_messaging.py` - Core messaging infrastructure
- `start_agents.py` - Agent launcher
- `agent_messaging_web.py` - Web UI server

### MCP Server
- `mcp_server/servers/agent_messaging_server.py` - FastMCP server
- `mcp_server/operations/agent_messaging_ops.py` - Operations
- `.mcp.json` - MCP configuration

### Configuration
- `.claude/settings.local.json` - Claude Code settings
- `.cursor/rules/` - Cursor AI agent rules
- `.env.example` - Environment variables template

### Examples
- `examples/` - Usage examples
- `docs/` - Additional documentation

## Customization

### Add Your Own Agents

Edit `agent_messaging.py` and add to `AGENT_PERSONAS`:

```python
AGENT_PERSONAS = {
    'custom_agent': {
        'name': 'Custom Agent',
        'role': 'Your Custom Role'
    }
}
```

### Custom Message Handlers

```python
async def custom_handler(message: Message):
    # Your custom logic
    await agent.send_message(message.from_user, "Custom response")

agent = AgentMessageQueue('agent_name', message_handler=custom_handler)
```

### Namespace Configuration

Set `NATS_NAMESPACE` environment variable to use different namespaces for different projects:

```bash
export NATS_NAMESPACE="project-name"
```

## MCP Tools

| Tool | Description |
|------|-------------|
| `dm_agent` | Send a DM to an agent |
| `get_agents` | List all available agents |
| `view_messages` | View message history |
| `view_conversation` | View conversation between users |

## Requirements

- Python 3.8+
- NATS Server (local or remote)
- FastMCP
- nats-py
- Flask (for web UI)

## License

MIT

## Support

For issues and questions, please open an issue on GitHub.
