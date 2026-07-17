#!/usr/bin/env python3
"""
HIVE-HERMES INTEGRATION BRIDGE
Connects Hive OS Swarm to Hermes Agent in Termux
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any

# Paths
HIVE_ROOT = Path.home() / ".hive"
HERMES_QUEUE = HIVE_ROOT / "hermes_queue.json"
HIVE_STATE = HIVE_ROOT / "state" / "hermes_bridge.json"
LOG_FILE = HIVE_ROOT / "logs" / "hermes_bridge.log"

class HermesBridge:
    """
    Bidirectional bridge between Hive Swarm and Hermes Agent.
    
    Enables:
    - Hermes to delegate tasks to Hive Swarm
    - Hive Swarm to report results back to Hermes
    - Status synchronization
    - Error forwarding
    """
    
    def __init__(self):
        self.running = False
        self.message_count = 0
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        """Ensure required directories exist"""
        HIVE_ROOT.mkdir(parents=True, exist_ok=True)
        (HIVE_ROOT / "logs").mkdir(exist_ok=True)
        (HIVE_ROOT / "state").mkdir(exist_ok=True)
    
    def log(self, message: str, level: str = "INFO"):
        """Log message to file and console"""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        print(entry)
        
        with open(LOG_FILE, 'a') as f:
            f.write(entry + "\n")
    
    def send_to_hermes(self, message_type: str, content: Dict[str, Any]) -> bool:
        """Send message from Hive to Hermes"""
        message = {
            "source": "hive",
            "type": message_type,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "id": f"hive-{self.message_count}"
        }
        
        try:
            queue = []
            if HERMES_QUEUE.exists():
                with open(HERMES_QUEUE) as f:
                    queue = json.load(f)
            
            queue.append(message)
            
            # Keep only last 100 messages
            queue = queue[-100:]
            
            with open(HERMES_QUEUE, 'w') as f:
                json.dump(queue, f, indent=2)
            
            self.message_count += 1
            self.log(f"Sent to Hermes: {message_type}")
            return True
            
        except Exception as e:
            self.log(f"Failed to send: {e}", "ERROR")
            return False
    
    def receive_from_hermes(self) -> List[Dict[str, Any]]:
        """Receive messages from Hermes to Hive"""
        if not HERMES_QUEUE.exists():
            return []
        
        try:
            with open(HERMES_QUEUE) as f:
                queue = json.load(f)
            
            # Filter messages from Hermes
            hermes_messages = [m for m in queue if m.get("source") == "hermes"]
            
            # Keep only Hive messages in queue
            hive_messages = [m for m in queue if m.get("source") == "hive"]
            
            with open(HERMES_QUEUE, 'w') as f:
                json.dump(hive_messages, f, indent=2)
            
            return hermes_messages
            
        except Exception as e:
            self.log(f"Failed to receive: {e}", "ERROR")
            return []
    
    def process_hermes_message(self, message: Dict[str, Any]):
        """Process incoming message from Hermes"""
        msg_type = message.get("type")
        content = message.get("content", {})
        
        self.log(f"Processing Hermes message: {msg_type}")
        
        if msg_type == "delegate_task":
            # Hermes wants to delegate to Hive Swarm
            task_desc = content.get("task")
            agent_type = content.get("agent", "executor")
            
            self.log(f"Delegating to {agent_type}: {task_desc}")
            
            # Here we would actually call the orchestrator
            # For now, simulate
            result = {
                "task": task_desc,
                "agent": agent_type,
                "status": "accepted",
                "task_id": f"task-{int(time.time())}"
            }
            
            # Send acknowledgment back to Hermes
            self.send_to_hermes("task_accepted", result)
            
        elif msg_type == "query_status":
            # Hermes wants Hive status
            status = self.get_hive_status()
            self.send_to_hermes("status_report", status)
            
        elif msg_type == "run_tool":
            # Hermes wants to run a Hive tool
            tool_name = content.get("tool")
            tool_args = content.get("args", [])
            
            self.log(f"Running tool: {tool_name}")
            
            # Execute tool
            result = self.run_hive_tool(tool_name, tool_args)
            self.send_to_hermes("tool_result", result)
    
    def get_hive_status(self) -> Dict[str, Any]:
        """Get current Hive system status"""
        try:
            from core.orchestrator import SwarmOrchestrator
            orch = SwarmOrchestrator()
            status = orch.get_status_report()
            return status
        except Exception as e:
            return {
                "error": str(e),
                "agents": 0,
                "tasks_pending": 0,
                "status": "bridge_only"
            }
    
    def run_hive_tool(self, tool_name: str, args: List[str]) -> Dict[str, Any]:
        """Run a Hive security tool"""
        tool_paths = {
            "port_scanner": "20-SCANNING/port_scanner.py",
            "dir_bruter": "20-SCANNING/dir_bruter.py",
            "subdomain_brute": "10-RECON/subdomain_brute.py",
            "hash_cracker": "70-CRYPTO/hash_cracker.py",
            "payload_gen": "30-EXPLOITATION/payload_generator.py",
        }
        
        if tool_name not in tool_paths:
            return {"error": f"Unknown tool: {tool_name}"}
        
        tool_path = HIVE_ROOT / tool_paths[tool_name]
        
        if not tool_path.exists():
            return {"error": f"Tool not found: {tool_path}"}
        
        try:
            # Run tool
            cmd = ["python3", str(tool_path)] + args
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            return {
                "tool": tool_name,
                "args": args,
                "returncode": result.returncode,
                "stdout": result.stdout,
                "stderr": result.stderr
            }
            
        except subprocess.TimeoutExpired:
            return {"error": "Tool timed out"}
        except Exception as e:
            return {"error": str(e)}
    
    def save_state(self):
        """Save bridge state"""
        state = {
            "running": self.running,
            "message_count": self.message_count,
            "last_update": datetime.now().isoformat()
        }
        
        with open(HIVE_STATE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def load_state(self):
        """Load bridge state"""
        if HIVE_STATE.exists():
            with open(HIVE_STATE) as f:
                state = json.load(f)
                self.message_count = state.get("message_count", 0)
    
    def run(self):
        """Main bridge loop"""
        self.running = True
        self.load_state()
        
        self.log("=" * 60)
        self.log("HIVE-HERMES BRIDGE STARTED")
        self.log("=" * 60)
        self.log(f"Queue: {HERMES_QUEUE}")
        self.log(f"State: {HIVE_STATE}")
        
        try:
            while self.running:
                # Check for messages from Hermes
                messages = self.receive_from_hermes()
                
                for message in messages:
                    self.process_hermes_message(message)
                
                # Save state periodically
                if self.message_count % 10 == 0:
                    self.save_state()
                
                # Small delay to prevent busy-wait
                time.sleep(1)
                
        except KeyboardInterrupt:
            self.log("Bridge stopped by user")
        finally:
            self.running = False
            self.save_state()
            self.log("Bridge shutdown complete")
    
    def stop(self):
        """Stop the bridge"""
        self.running = False

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Hive-Hermes Integration Bridge')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    parser.add_argument('--status', action='store_true', help='Show status')
    parser.add_argument('--send', help='Send test message to Hermes')
    
    args = parser.parse_args()
    
    bridge = HermesBridge()
    
    if args.status:
        status = bridge.get_hive_status()
        print(json.dumps(status, indent=2))
    
    elif args.send:
        bridge.send_to_hermes("test", {"message": args.send})
        print("Message sent to Hermes")
    
    else:
        # Run bridge
        bridge.run()

if __name__ == "__main__":
    main()
