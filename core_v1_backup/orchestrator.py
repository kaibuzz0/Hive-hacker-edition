#!/usr/bin/env python3
"""
HIVE SWARM ORCHESTRATOR
Bidirectional multi-agent coordination hub with verification loops.
Core component of the Hive System.
"""

import json
import os
import sys
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Any, Callable, Dict, List, Optional
from dataclasses import dataclass, asdict
from enum import Enum
import threading

class TaskStatus(Enum):
    PENDING = "pending"
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    NEEDS_CLARIFICATION = "needs_clarification"
    COMPLETED = "completed"
    VERIFIED = "verified"
    REJECTED = "rejected"
    FAILED = "failed"

class AgentType(Enum):
    ORCHESTRATOR = "orchestrator"
    ASSISTANT = "assistant"      # Verification/audit
    ARCHITECT = "architect"      # Code review/structure
    TOOLSMITH = "toolsmith"      # Tool building
    EXECUTOR = "executor"        # Task execution

@dataclass
class Message:
    id: str
    from_agent: str
    to_agent: str
    type: str
    content: Dict[str, Any]
    timestamp: str
    requires_response: bool = False
    
    def to_dict(self):
        d = asdict(self)
        d['timestamp'] = self.timestamp
        return d

@dataclass  
class Task:
    id: str
    description: str
    assigned_to: Optional[str]
    status: TaskStatus
    created_at: str
    completed_at: Optional[str] = None
    verified_by: Optional[str] = None
    verification_result: Optional[Dict] = None
    parent_task: Optional[str] = None
    messages: List[str] = None
    
    def __post_init__(self):
        if self.messages is None:
            self.messages = []

class SwarmRegistry:
    """Persistent registry for agents, tasks, and messages."""
    
    REGISTRY_PATH = Path("~/.hive/swarm_registry.json").expanduser()
    
    def __init__(self):
        self.agents: Dict[str, Dict] = {}
        self.tasks: Dict[str, Task] = {}
        self.messages: List[Message] = []
        self._lock = threading.RLock()
        self._ensure_dir()
        self._load()
    
    def _ensure_dir(self):
        self.REGISTRY_PATH.parent.mkdir(parents=True, exist_ok=True)
    
    def _load(self):
        if self.REGISTRY_PATH.exists():
            try:
                with open(self.REGISTRY_PATH) as f:
                    data = json.load(f)
                self.agents = data.get('agents', {})
                for tid, tdata in data.get('tasks', {}).items():
                    self.tasks[tid] = Task(
                        id=tdata['id'],
                        description=tdata['description'],
                        assigned_to=tdata.get('assigned_to'),
                        status=TaskStatus(tdata['status']),
                        created_at=tdata['created_at'],
                        completed_at=tdata.get('completed_at'),
                        verified_by=tdata.get('verified_by'),
                        verification_result=tdata.get('verification_result'),
                        parent_task=tdata.get('parent_task'),
                        messages=tdata.get('messages', [])
                    )
            except Exception as e:
                print(f"[REGISTRY] Load error: {e}")
    
    def save(self):
        with self._lock:
            data = {
                'agents': self.agents,
                'tasks': {tid: {
                    'id': t.id,
                    'description': t.description,
                    'assigned_to': t.assigned_to,
                    'status': t.status.value,
                    'created_at': t.created_at,
                    'completed_at': t.completed_at,
                    'verified_by': t.verified_by,
                    'verification_result': t.verification_result,
                    'parent_task': t.parent_task,
                    'messages': t.messages
                } for tid, t in self.tasks.items()},
                'messages': [m.to_dict() for m in self.messages]
            }
            with open(self.REGISTRY_PATH, 'w') as f:
                json.dump(data, f, indent=2)
    
    def register_agent(self, agent_id: str, agent_type: AgentType, capabilities: List[str]):
        with self._lock:
            self.agents[agent_id] = {
                'id': agent_id,
                'type': agent_type.value,
                'capabilities': capabilities,
                'status': 'active',
                'registered_at': datetime.now().isoformat()
            }
        self.save()
    
    def create_task(self, description: str, assigned_to: Optional[str] = None, parent: Optional[str] = None) -> str:
        task_id = str(uuid.uuid4())[:8]
        task = Task(
            id=task_id,
            description=description,
            assigned_to=assigned_to,
            status=TaskStatus.PENDING,
            created_at=datetime.now().isoformat(),
            parent_task=parent
        )
        with self._lock:
            self.tasks[task_id] = task
        self.save()
        return task_id
    
    def get_task(self, task_id: str) -> Optional[Task]:
        return self.tasks.get(task_id)
    
    def update_task_status(self, task_id: str, status: TaskStatus, result: Optional[Dict] = None):
        with self._lock:
            if task_id in self.tasks:
                self.tasks[task_id].status = status
                if status in [TaskStatus.COMPLETED, TaskStatus.VERIFIED, TaskStatus.FAILED]:
                    self.tasks[task_id].completed_at = datetime.now().isoformat()
                if result:
                    self.tasks[task_id].verification_result = result
        self.save()
    
    def get_pending_tasks(self) -> List[Task]:
        return [t for t in self.tasks.values() if t.status == TaskStatus.PENDING]
    
    def get_tasks_for_agent(self, agent_id: str) -> List[Task]:
        return [t for t in self.tasks.values() if t.assigned_to == agent_id]

class SwarmOrchestrator:
    """Main orchestrator coordinating the Hive Swarm."""
    
    def __init__(self):
        self.registry = SwarmRegistry()
        self._running = False
        self._message_handlers: Dict[str, Callable] = {}
    
    def register_handler(self, message_type: str, handler: Callable):
        self._message_handlers[message_type] = handler
    
    def create_task_chain(self, description: str, chain: List[AgentType]) -> List[str]:
        """Create a chain of dependent tasks."""
        task_ids = []
        parent_id = None
        
        for agent_type in chain:
            agent_id = f"{agent_type.value}_{uuid.uuid4().hex[:6]}"
            task_id = self.registry.create_task(
                f"{description} [{agent_type.value}]",
                assigned_to=agent_id,
                parent=parent_id
            )
            task_ids.append(task_id)
            parent_id = task_id
        
        return task_ids
    
    def delegate_task(self, description: str, to_agent: str, require_verification: bool = True) -> str:
        """Delegate a task to an agent."""
        task_id = self.registry.create_task(description, assigned_to=to_agent)
        
        if require_verification:
            verifier_id = f"assistant_{uuid.uuid4().hex[:6]}"
            verify_task_id = self.registry.create_task(
                f"Verify: {description}",
                assigned_to=verifier_id,
                parent=task_id
            )
        
        return task_id
    
    def verify_chain(self, task_id: str) -> bool:
        """Verify completion of a task and its chain."""
        task = self.registry.get_task(task_id)
        if not task:
            return False
        
        # Check if task is complete
        if task.status != TaskStatus.COMPLETED:
            return False
        
        # Check parent task if exists
        if task.parent_task:
            parent = self.registry.get_task(task.parent_task)
            if parent and parent.status != TaskStatus.VERIFIED:
                return False
        
        # Mark as verified
        self.registry.update_task_status(task_id, TaskStatus.VERIFIED, 
                                         {'verified_by': 'orchestrator', 'timestamp': datetime.now().isoformat()})
        return True
    
    def get_status_report(self) -> Dict:
        """Get current swarm status."""
        return {
            'agents': len(self.registry.agents),
            'tasks_total': len(self.registry.tasks),
            'tasks_pending': len([t for t in self.registry.tasks.values() if t.status == TaskStatus.PENDING]),
            'tasks_in_progress': len([t for t in self.registry.tasks.values() if t.status == TaskStatus.IN_PROGRESS]),
            'tasks_completed': len([t for t in self.registry.tasks.values() if t.status == TaskStatus.COMPLETED]),
            'tasks_verified': len([t for t in self.registry.tasks.values() if t.status == TaskStatus.VERIFIED]),
            'tasks_failed': len([t for t in self.registry.tasks.values() if t.status == TaskStatus.FAILED])
        }
    
    def run(self):
        """Main orchestrator loop."""
        self._running = True
        print("[ORCHESTRATOR] Swarm coordination started")
        
        while self._running:
            pending = self.registry.get_pending_tasks()
            
            for task in pending:
                print(f"[TASK] {task.id}: {task.description}")
                self.registry.update_task_status(task.id, TaskStatus.ASSIGNED)
            
            time.sleep(5)
    
    def stop(self):
        self._running = False

def main():
    print("""
╔══════════════════════════════════════════════════╗
║  🐝 HIVE SWARM ORCHESTRATOR                       ║
║  Multi-agent coordination system                  ║
║                                                   ║
║  Registry: ~/.hive/swarm_registry.json           ║
╚══════════════════════════════════════════════════╝
    """)
    
    orchestrator = SwarmOrchestrator()
    
    # Show status
    status = orchestrator.get_status_report()
    print("\n📊 Current Status:")
    for key, value in status.items():
        print(f"  {key}: {value}")
    
    print("\n✓ Orchestrator ready")

if __name__ == "__main__":
    main()
