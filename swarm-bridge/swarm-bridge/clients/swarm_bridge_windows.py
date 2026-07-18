#!/usr/bin/env python3
"""
Swarm Bridge Client - Windows Node (Node 2)
Git-based message bridge for Hive Swarm communication
"""

import os
import sys
import json
import hashlib
import time
from datetime import datetime
from pathlib import Path

def get_node_id():
    return "node_2_windows"

def get_peer_id():
    return "node_1_termux"

def generate_message_id():
    return hashlib.md5(str(time.time()).encode()).hexdigest()[:8]

def send_message(content):
    """Send message to peer via GitHub"""
    msg_id = generate_message_id()
    message = {
        "id": msg_id,
        "from": get_node_id(),
        "to": get_peer_id(),
        "content": content,
        "timestamp": datetime.now().isoformat(),
        "status": "pending"
    }
    
    mailbox_dir = Path(__file__).parent.parent / "mailbox"
    msg_file = mailbox_dir / f"{msg_id}.json"
    
    with open(msg_file, 'w') as f:
        json.dump(message, f, indent=2)
    
    print(f"📤 Message queued: {msg_id}")
    print(f"   To: {get_peer_id()}")
    print(f"   Content: {content}")
    print(f"
⚠️  Remember to: git add, commit, and push to sync")
    
    return msg_id

def receive_messages():
    """Check mailbox for incoming messages"""
    mailbox_dir = Path(__file__).parent.parent / "mailbox"
    peer = get_peer_id()
    
    print(f"📡 Checking for messages from {peer}...
")
    
    found = 0
    for msg_file in sorted(mailbox_dir.glob("*.json")):
        try:
            with open(msg_file, 'r') as f:
                msg = json.load(f)
            
            if msg.get("to") == get_node_id():
                found += 1
                print(f"📨 FROM: {msg['from']}")
                print(f"   ID: {msg['id']}")
                print(f"   TIME: {msg['timestamp']}")
                print(f"   CONTENT: {msg['content']}")
                print(f"   STATUS: {msg.get('status', 'unknown')}")
                print("-" * 50)
                
                # Mark as read
                msg['status'] = 'delivered'
                with open(msg_file, 'w') as f:
                    json.dump(msg, f, indent=2)
                    
        except Exception as e:
            pass
    
    if found == 0:
        print("📭 No new messages")
    else:
        print(f"
✅ Retrieved {found} message(s)")

def main():
    if len(sys.argv) < 2:
        print("Usage:")
        print(f"  python {sys.argv[0]} send \"<message>\"")
        print(f"  python {sys.argv[0]} receive")
        print(f"  python {sys.argv[0]} daemon")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "send":
        if len(sys.argv) < 3:
            print("❌ Error: Message required")
            sys.exit(1)
        send_message(sys.argv[2])
    
    elif command == "receive":
        receive_messages()
    
    elif command == "daemon":
        print("🐝 Swarm Bridge Daemon - Node 2 (Windows)")
        print("Press Ctrl+C to stop
")
        while True:
            receive_messages()
            time.sleep(5)
    
    else:
        print(f"❌ Unknown command: {command}")

if __name__ == "__main__":
    main()
