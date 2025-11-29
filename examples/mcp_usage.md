# MCP Usage Examples

Using the Agent Messaging System via MCP in Claude Code.

## Prerequisites

1. Agents must be running:
   ```bash
   python start_agents.py
   ```

2. MCP server is configured in `.mcp.json`

## Examples

### 1. Send a DM to an Agent

```python
dm_agent(
    agent_name="sylvia",
    content="Explain the concept of retrieval-augmented generation",
    from_user="student@example.com"
)
```

Response:
```json
{
  "success": true,
  "message": {
    "id": "msg_...",
    "from_user": "student@example.com",
    "to_user": "agent_sylvia",
    "content": "Explain the concept of retrieval-augmented generation",
    "timestamp": "2025-11-29T..."
  }
}
```

### 2. List All Agents

```python
get_agents()
```

Response:
```json
{
  "success": true,
  "agents": {
    "sylvia": {
      "name": "Sylvia",
      "role": "Teaching Assistant"
    },
    ...
  },
  "count": 12
}
```

### 3. View Messages

```python
# All messages
view_messages()

# Messages for specific agent
view_messages(agent_name="sylvia")
```

### 4. View Conversation

```python
view_conversation(
    user1="student@example.com",
    user2="agent_sylvia"
)
```

## Use Cases

### Ask for Help
```python
dm_agent(
    agent_name="moss",
    content="How do I deploy a Python application to production?",
    from_user="developer@example.com"
)
```

### Course Information
```python
dm_agent(
    agent_name="roy",
    content="What courses are starting next month?",
    from_user="prospective@example.com"
)
```

### Technical Questions
```python
dm_agent(
    agent_name="architect",
    content="What's the best way to design a microservices architecture?",
    from_user="engineer@example.com"
)
```

### Community Engagement
```python
dm_agent(
    agent_name="tessa",
    content="Are there any upcoming community events?",
    from_user="community@example.com"
)
```
