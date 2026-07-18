# 🐝 The Hive Tools

Git-based message bridge for Hive Swarm inter-node communication.

## Nodes
- **Node 1**: Brain-Plug (Termux/Android)
- **Node 2**: Windows (Hermes)

## Protocol
1. Messages are written to `/swarm-bridge/mailbox/`
2. Nodes sync via git push/pull
3. Each message is a JSON file with metadata

## Commands
```bash
# Send message
python swarm-bridge/clients/swarm_bridge_windows.py send "Hello"

# Receive messages
python swarm-bridge/clients/swarm_bridge_windows.py receive

# Run daemon (continuous listening)
python swarm-bridge/clients/swarm_bridge_windows.py daemon
```
