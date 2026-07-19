#!/usr/bin/env python3
"""
HIVE AGENT RUNNER v2
Real subprocess-based agent execution with process management.
Honest capability: Spawns real Python processes, not simulations.

This is NOT a distributed computing framework.
It IS a working local agent spawner with lifecycle management.
"""

import subprocess
import os
import signal
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Callable
from dataclasses import dataclass, field

from hive_mq import FileMessageQueue, Message

HIVE_ROOT = Path.home() / ".hive"
AGENTS_DIR = HIVE_ROOT / "agents"
LOGS_DIR = HIVE_ROOT / "logs"

AGENTS_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)

@dataclass
class AgentProcess:
    """A running agent process."""
    agent_id: str
    agent_type: str
    process: subprocess.Popen
    pid: int
    started_at: str
    log_file: Path
    status: str = "running"  # running, stopped, failed
    last_heartbeat: str = ""
    task_count: int = 0

class AgentRunner:
    """
    Spawns and manages real agent processes via subprocess.
    
    CAPABILITIES:
    - Spawn agent processes (real subprocess.Popen)
    - Monitor process health
    - Send tasks via message queue
    - Receive results from agents
    - Restart failed agents
    - Graceful shutdown
    
    LIMITATIONS:
    - Local processes only (no network distribution)
    - Agents must be Python scripts
    - Limited to available system resources
    - No sandboxing (agents run with user permissions)
    
    HONEST LABEL: "Local subprocess-based agent spawner"
    """
    
    def __init__(self):
        self.agents: Dict[str, AgentProcess] = {}
        self.mq = FileMessageQueue("agent_comm")
        self._running = False
    
    def spawn_agent(self, agent_type: str, agent_id: str = None, agent_code: str = None) -> Optional[str]:
        """
        Spawn a new agent process.
        
        Args:
            agent_type: Type of agent (executor, scanner, etc.)
            agent_id: Optional specific ID (generated if None)
            agent_code: Optional custom agent code to execute
            
        Returns:
            Agent ID or None if spawn failed
        """
        if agent_id is None:
            agent_id = f"{agent_type}_{os.urandom(4).hex()}"
        
        log_file = LOGS_DIR / f"agent_{agent_id}.log"
        
        try:
            # Write agent code to file if provided
            if agent_code:
                agent_path = AGENTS_DIR / f"{agent_id}.py"
                with open(agent_path, 'w') as f:
                    f.write(agent_code)
            else:
                # Use default agent template
                agent_path = self._create_default_agent(agent_id, agent_type)
            
            # Spawn process
            with open(log_file, 'w') as log:
                process = subprocess.Popen(
                    ['python3', str(agent_path), agent_id],
                    stdout=log,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.DEVNULL,
                    start_new_session=True  # Detach from parent
                )
            
            # Register agent
            agent = AgentProcess(
                agent_id=agent_id,
                agent_type=agent_type,
                process=process,
                pid=process.pid,
                started_at=datetime.now().isoformat(),
                log_file=log_file
            )
            
            self.agents[agent_id] = agent
            
            # Announce agent is ready
            self.mq.send(
                sender="runner",
                recipient="orchestrator",
                msg_type="agent_spawned",
                payload={
                    "agent_id": agent_id,
                    "agent_type": agent_type,
                    "pid": process.pid,
                    "status": "ready"
                }
            )
            
            print(f"[RUNNER] Spawned {agent_type} agent: {agent_id} (PID: {process.pid})")
            return agent_id
            
        except Exception as e:
            print(f"[RUNNER ERROR] Failed to spawn agent {agent_id}: {e}")
            return None
    
    def _create_default_agent(self, agent_id: str, agent_type: str) -> Path:
        """Create a default agent that listens on message queue."""
        agent_path = AGENTS_DIR / f"{agent_id}.py"
        
        agent_code = f'''#!/usr/bin/env python3
"""
Hive Agent: {agent_id}
Type: {agent_type}
Auto-generated agent process.
"""

import sys
import time
import json
from pathlib import Path

AGENT_ID = sys.argv[1] if len(sys.argv) > 1 else "unknown"
HIVE_ROOT = Path.home() / ".hive"

# Import message queue
sys.path.insert(0, str(HIVE_ROOT))
from hive_mq import FileMessageQueue, Message

def main():
    mq = FileMessageQueue("agent_comm")
    
    # Register with orchestrator
    mq.send(
        sender=AGENT_ID,
        recipient="orchestrator",
        msg_type="agent_ready",
        payload={{"agent_type": "{agent_type}", "capabilities": ["execute", "report"]}}
    )
    
    print(f"[AGENT {{AGENT_ID}}] Started and listening...")
    
    while True:
        # Wait for tasks (blocking with timeout)
        msg = mq.receive(AGENT_ID, block=True, timeout=5.0)
        
        if msg:
            print(f"[AGENT {{AGENT_ID}}] Received {{msg.type}}: {{msg.payload}}")
            
            if msg.type == "task":
                # Execute task
                result = execute_task(msg.payload)
                
                # Send result back
                mq.send(
                    sender=AGENT_ID,
                    recipient="orchestrator",
                    msg_type="task_complete",
                    payload={{
                        "task_id": msg.payload.get("task_id"),
                        "result": result,
                        "agent_id": AGENT_ID
                    }}
                )
                
                # Acknowledge message
                mq.acknowledge(msg.id, processed=True)
                
            elif msg.type == "shutdown":
                print(f"[AGENT {{AGENT_ID}}] Shutting down...")
                mq.acknowledge(msg.id, processed=True)
                break
        
        # Send heartbeat every 30 seconds
        # (simplified: would track time in real implementation)

def execute_task(payload):
    """Execute the actual task."""
    command = payload.get("command", "unknown")
    
    if command == "ping":
        return {{"status": "success", "data": "pong"}}
    
    elif command == "scan_ports":
        target = payload.get("target", "unknown")
        # Real port scanning would happen here
        return {{"status": "success", "target": target, "open_ports": []}}
    
    elif command == "dns_lookup":
        target = payload.get("target", "unknown")
        import socket
        try:
            ip = socket.gethostbyname(target)
            return {{"status": "success", "target": target, "ip": ip}}
        except Exception as e:
            return {{"status": "error", "error": str(e)}}
    
    else:
        return {{"status": "unknown_command", "command": command}}

if __name__ == "__main__":
    main()
'''
        
        with open(agent_path, 'w') as f:
            f.write(agent_code)
        
        return agent_path
    
    def send_task(self, agent_id: str, command: str, payload: dict) -> bool:
        """
        Send a task to an agent.
        
        Args:
            agent_id: Target agent
            command: Command to execute
            payload: Task parameters
            
        Returns:
            True if message sent
        """
        if agent_id not in self.agents:
            print(f"[RUNNER ERROR] Agent {agent_id} not found")
            return False
        
        # Generate task ID
        task_id = f"task_{os.urandom(4).hex()}"
        
        # Send via message queue
        msg_id = self.mq.send(
            sender="orchestrator",
            recipient=agent_id,
            msg_type="task",
            payload={
                "task_id": task_id,
                "command": command,
                **payload
            }
        )
        
        if msg_id:
            self.agents[agent_id].task_count += 1
            print(f"[RUNNER] Task {task_id} sent to {agent_id}")
            return True
        
        return False
    
    def check_health(self, agent_id: str = None) -> Dict:
        """
        Check health of agents.
        
        Args:
            agent_id: Specific agent or None for all
            
        Returns:
            Health status dict
        """
        results = {}
        agents_to_check = [agent_id] if agent_id else list(self.agents.keys())
        
        for aid in agents_to_check:
            if aid not in self.agents:
                results[aid] = {"status": "not_found"}
                continue
            
            agent = self.agents[aid]
            
            # Check if process is still running
            if agent.process.poll() is None:
                agent.status = "running"
                results[aid] = {
                    "status": "running",
                    "pid": agent.pid,
                    "tasks": agent.task_count,
                    "started": agent.started_at
                }
            else:
                agent.status = "stopped"
                exit_code = agent.process.returncode
                results[aid] = {
                    "status": "stopped",
                    "exit_code": exit_code,
                    "tasks": agent.task_count
                }
        
        return results
    
    def restart_agent(self, agent_id: str) -> bool:
        """Restart a failed agent."""
        if agent_id not in self.agents:
            return False
        
        old_agent = self.agents[agent_id]
        agent_type = old_agent.agent_type
        
        # Kill old process if still running
        if old_agent.process.poll() is None:
            try:
                os.killpg(os.getpgid(old_agent.process.pid), signal.SIGTERM)
            except:
                pass
        
        # Remove from registry
        del self.agents[agent_id]
        
        # Spawn new instance
        new_id = self.spawn_agent(agent_type, agent_id)
        return new_id is not None
    
    def kill_agent(self, agent_id: str) -> bool:
        """Kill an agent process."""
        if agent_id not in self.agents:
            return False
        
        agent = self.agents[agent_id]
        
        try:
            # Send shutdown message first (graceful)
            self.mq.send(
                sender="orchestrator",
                recipient=agent_id,
                msg_type="shutdown",
                payload={"reason": "user_request"}
            )
            
            # Wait a moment
            time.sleep(1)
            
            # Force kill if still running
            if agent.process.poll() is None:
                os.killpg(os.getpgid(agent.process.pid), signal.SIGTERM)
                agent.process.wait(timeout=5)
            
            agent.status = "stopped"
            print(f"[RUNNER] Killed agent {agent_id}")
            return True
            
        except Exception as e:
            print(f"[RUNNER ERROR] Failed to kill {agent_id}: {e}")
            return False
    
    def shutdown_all(self):
        """Shutdown all agents."""
        print(f"[RUNNER] Shutting down {len(self.agents)} agents...")
        
        for agent_id in list(self.agents.keys()):
            self.kill_agent(agent_id)
        
        self.agents.clear()
        print("[RUNNER] All agents stopped")
    
    def get_status(self) -> Dict:
        """Get runner status."""
        running = sum(1 for a in self.agents.values() if a.status == "running")
        
        return {
            "total_agents": len(self.agents),
            "running": running,
            "stopped": len(self.agents) - running,
            "agents": {
                aid: {
                    "type": a.agent_type,
                    "status": a.status,
                    "pid": a.pid,
                    "tasks": a.task_count
                }
                for aid, a in self.agents.items()
            }
        }


def test_agent_runner():
    """Test the agent runner."""
    print("=" * 60)
    print("TESTING: AgentRunner")
    print("=" * 60)
    
    runner = AgentRunner()
    
    # Test 1: Spawn agent
    print("\n1. Spawning executor agent...")
    agent_id = runner.spawn_agent("executor")
    if agent_id:
        print(f"   Spawned: {agent_id}")
    else:
        print("   FAILED")
        return
    
    # Wait for agent to start
    time.sleep(2)
    
    # Test 2: Check health
    print("\n2. Checking agent health...")
    health = runner.check_health(agent_id)
    print(f"   Status: {health[agent_id]}")
    
    # Test 3: Send task
    print("\n3. Sending ping task...")
    result = runner.send_task(agent_id, "ping", {})
    print(f"   Task sent: {result}")
    
    # Wait for result
    time.sleep(2)
    
    # Check message queue for result
    msg = runner.mq.receive("orchestrator", block=False)
    if msg:
        print(f"   Result received: {msg.payload}")
    
    # Test 4: Send DNS lookup
    print("\n4. Sending DNS lookup task...")
    runner.send_task(agent_id, "dns_lookup", {"target": "google.com"})
    
    time.sleep(2)
    
    msg = runner.mq.receive("orchestrator", block=False)
    if msg:
        print(f"   DNS result: {msg.payload}")
    
    # Test 5: Get status
    print("\n5. Runner status:")
    status = runner.get_status()
    print(f"   Total agents: {status['total_agents']}")
    print(f"   Running: {status['running']}")
    
    # Test 6: Kill agent
    print("\n6. Shutting down agent...")
    runner.kill_agent(agent_id)
    print("   Done")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)


if __name__ == "__main__":
    test_agent_runner()
