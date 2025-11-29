"""
Web Frontend for Agent Messaging System
View all messages and send DMs to agents
"""
from flask import Flask, render_template, request, jsonify
import asyncio
import json
from agent_messaging import MessageRouter, MessageViewer, AGENT_PERSONAS
from datetime import datetime
import threading

app = Flask(__name__)

# Global instances
router = MessageRouter()
viewer = MessageViewer()
messages_cache = []
event_loop = None

# Background task to keep asyncio running
def run_async_tasks():
    """Run async tasks in background thread"""
    global event_loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    event_loop = loop

    async def setup():
        await router.connect()
        await viewer.connect()
        await viewer.start_viewing(print_messages=False)

    loop.run_until_complete(setup())
    loop.run_forever()

# Start background thread
bg_thread = threading.Thread(target=run_async_tasks, daemon=True)
bg_thread.start()

# Wait for event loop to be ready
import time
while event_loop is None:
    time.sleep(0.1)


@app.route('/')
def index():
    """Main page"""
    return render_template('agent_messages.html', agents=AGENT_PERSONAS)


@app.route('/api/messages')
def get_messages():
    """Get all messages"""
    messages = viewer.get_all_messages()
    return jsonify({
        'success': True,
        'messages': [msg.to_dict() for msg in messages],
        'count': len(messages)
    })


@app.route('/api/messages/<agent_name>')
def get_agent_messages(agent_name):
    """Get messages for specific agent"""
    messages = viewer.get_agent_messages(agent_name)
    return jsonify({
        'success': True,
        'agent': agent_name,
        'messages': [msg.to_dict() for msg in messages],
        'count': len(messages)
    })


@app.route('/api/send', methods=['POST'])
def send_message():
    """Send a DM to an agent"""
    try:
        data = request.json
        if not data:
            return jsonify({'success': False, 'error': 'No JSON data received'}), 400

        from_user = data.get('from_user')
        to_agent = data.get('to_agent')
        content = data.get('content')

        if not all([from_user, to_agent, content]):
            return jsonify({'success': False, 'error': 'Missing required fields'}), 400

        # Send message asynchronously
        async def send():
            return await router.send_dm(from_user, to_agent, content)

        # Run in event loop
        future = asyncio.run_coroutine_threadsafe(send(), event_loop)
        message = future.result(timeout=5)

        return jsonify({
            'success': True,
            'message': message.to_dict()
        })
    except Exception as e:
        import traceback
        traceback.print_exc()
        return jsonify({'success': False, 'error': str(e)}), 500


@app.route('/api/agents')
def get_agents():
    """Get list of available agents"""
    return jsonify({
        'success': True,
        'agents': AGENT_PERSONAS
    })


if __name__ == '__main__':
    print("\n" + "="*60)
    print("🤖 Agent Messaging Web Interface")
    print("="*60)
    print("\nRunning on http://localhost:5002")
    print("\nAvailable agents:")
    for agent_id, info in AGENT_PERSONAS.items():
        print(f"  - {info['name']} ({info['role']})")
    print("\nPress Ctrl+C to stop\n")

    app.run(debug=False, host='0.0.0.0', port=5002)
