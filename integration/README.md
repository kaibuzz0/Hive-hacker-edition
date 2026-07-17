# 🤖 HERMES INTEGRATION

The Hive-Hermes Bridge enables bidirectional communication between your Hive OS Swarm and the Hermes AI Agent.

## Architecture

```
┌─────────────┐         ┌──────────────┐         ┌─────────────┐
│   HERMES    │◄───────►│    BRIDGE    │◄───────►│  HIVE OS    │
│   AGENT     │  JSON   │              │  Tasks  │   SWARM     │
└─────────────┘  Queue   └──────────────┘         └─────────────┘
                    Port 8766
```

## Features

- **Task Delegation**: Hermes can delegate tasks to Hive Swarm agents
- **Tool Execution**: Hermes can trigger Hive security tools
- **Status Sync**: Real-time synchronization of task status
- **Bidirectional**: Both systems can initiate requests

## Quick Start

### Start the Integration

```bash
./start.sh
# Select option 2: Start Full Integration
```

Or manually:

```bash
# Start Hive daemon
python3 ~/.hive/core/self_heal.py --daemon

# Start Hermes Bridge
python3 ~/.hive/integration/hermes_bridge.py --daemon
```

### Check Status

```bash
./start.sh status
```

## Communication Protocol

### Hermes → Hive (Delegation)

```json
{
  "source": "hermes",
  "type": "delegate_task",
  "content": {
    "task": "Scan 192.168.1.0/24",
    "agent": "executor",
    "priority": "high"
  }
}
```

### Hive → Hermes (Results)

```json
{
  "source": "hive",
  "type": "tool_result",
  "content": {
    "tool": "port_scanner",
    "returncode": 0,
    "stdout": "...",
    "stderr": ""
  }
}
```

## Available Tools via Hermes

Hermes can trigger these Hive tools:

| Tool | Description | Usage |
|------|-------------|-------|
| port_scanner | Network port scanning | `hermes: run port_scanner 192.168.1.1` |
| dir_bruter | Directory enumeration | `hermes: run dir_bruter http://example.com` |
| subdomain_brute | Subdomain discovery | `hermes: run subdomain_brute example.com` |
| hash_cracker | Password hash cracking | `hermes: run hash_cracker [hash]` |
| payload_gen | Generate payloads | `hermes: run payload_gen reverse_shell` |

## Configuration

Edit `~/.hive/config/hermes_config.json`:

```json
{
  "connection": {
    "poll_interval": 1.0,
    "queue_path": "~/.hive/hermes_queue.json"
  },
  "ports": {
    "hermes_bridge": 8766
  }
}
```

## Logs

- **Bridge Logs**: `~/.hive/logs/hermes_bridge.log`
- **Message Queue**: `~/.hive/hermes_queue.json`
- **State**: `~/.hive/state/hermes_bridge.json`

## Troubleshooting

### Bridge Not Connecting

```bash
# Check if bridge is running
ps aux | grep hermes_bridge

# Restart bridge
pkill -f hermes_bridge
python3 ~/.hive/integration/hermes_bridge.py --daemon
```

### Message Queue Stuck

```bash
# Clear queue
rm ~/.hive/hermes_queue.json
```

### Port Conflicts

```bash
# Check ports
~/.hive/core/port_manager.sh status

# Repair
~/.hive/core/port_manager.sh repair
```

## Advanced Usage

### Send Manual Message to Hermes

```python
from integration.hermes_bridge import HermesBridge

bridge = HermesBridge()
bridge.send_to_hermes("custom_event", {
    "data": "your_data_here"
})
```

### Custom Tool Integration

Add new tools to `hermes_bridge.py`:

```python
def run_custom_tool(self, args):
    # Your tool logic
    return {"result": "success"}
```

## Security

- Bridge uses local file queue (no network exposure)
- All messages are JSON validated
- Automatic cleanup of old messages (keeps last 100)
- No credentials in queue files

## Files

- `integration/hermes_bridge.py` - Main bridge component
- `integration/hermes_config.json` - Bridge configuration
- `start.sh` - Unified startup script
