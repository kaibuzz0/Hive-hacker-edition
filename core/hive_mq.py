#!/usr/bin/env python3
"""
HIVE MESSAGE QUEUE v2
File-based message queue for Termux (no Redis dependencies)
Honest capability: JSON file queue with file locking

This is NOT a high-performance message broker.
It IS a working message queue for local agent communication.
"""

import json
import os
import time
import uuid
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from dataclasses import dataclass, asdict

# Platform detection for file locking
IS_ANDROID = os.path.exists('/system/build.prop') or 'ANDROID_ROOT' in os.environ

HIVE_ROOT = Path.home() / ".hive"
QUEUE_DIR = HIVE_ROOT / "hive_mq"

@dataclass
class Message:
    """A message in the queue."""
    id: str
    sender: str
    recipient: str
    type: str
    payload: dict
    timestamp: str
    delivered: bool = False
    processed: bool = False
    
    def to_dict(self):
        return asdict(self)
    
    @classmethod
    def from_dict(cls, data: dict) -> 'Message':
        return cls(**data)

class FileMessageQueue:
    """
    File-based message queue for local agent communication.
    
    CAPABILITIES:
    - Send messages between processes via JSON files
    - Receive messages with file locking
    - Acknowledge/processing tracking
    - Cleanup of old messages
    
    LIMITATIONS:
    - NOT for high-throughput (uses file I/O)
    - NOT for distributed systems (local filesystem only)
    - Poll-based (not push)
    
    HONEST LABEL: "Local file-based message queue"
    """
    
    def __init__(self, name: str = "default"):
        self.queue_dir = QUEUE_DIR / name
        self.queue_dir.mkdir(parents=True, exist_ok=True)
        self.lock_file = self.queue_dir / ".lock"
        
        # Create lock file if needed
        self.lock_file.touch()
    
    def _acquire_lock(self, timeout: float = 5.0):
        """Acquire exclusive lock on queue (Android-safe)."""
        self._lock_path = self.queue_dir / ".lock"
        start_time = time.time()
        
        while True:
            try:
                # Try to create lock file atomically
                fd = os.open(str(self._lock_path), os.O_CREAT | os.O_EXCL | os.O_WRONLY)
                os.write(fd, str(os.getpid()).encode())
                os.close(fd)
                # Open for later removal
                self._lock_fd = open(self._lock_path, 'w')
                return True
            except FileExistsError:
                # Check if lock is stale (owning process died)
                try:
                    if self._lock_path.exists():
                        with open(self._lock_path) as f:
                            content = f.read().strip()
                        if content:
                            old_pid = int(content)
                            # Check if process still exists
                            try:
                                os.kill(old_pid, 0)
                            except ProcessLookupError:
                                # Process is dead, remove stale lock
                                try:
                                    os.remove(self._lock_path)
                                except:
                                    pass
                                continue
                        else:
                            # Empty lock file, remove it
                            try:
                                os.remove(self._lock_path)
                            except:
                                pass
                            continue
                except (ValueError, FileNotFoundError, OSError):
                    # Lock file corrupted or I/O error, try to remove
                    try:
                        os.remove(self._lock_path)
                    except:
                        pass
                    continue
                
                # Lock held, check timeout
                if time.time() - start_time > timeout:
                    # Force remove stale lock
                    try:
                        os.remove(self._lock_path)
                    except:
                        pass
                    continue
                
                time.sleep(0.05)
    
    def _release_lock(self):
        """Release exclusive lock."""
        try:
            self._lock_fd.close()
        except:
            pass
        try:
            if hasattr(self, '_lock_path') and self._lock_path.exists():
                os.remove(self._lock_path)
        except:
            pass
    
    def send(self, sender: str, recipient: str, msg_type: str, payload: dict) -> str:
        """
        Send a message to a recipient.
        
        Args:
            sender: ID of sending agent/orchestrator
            recipient: ID of target agent (or "broadcast")
            msg_type: Message type (e.g., "task", "result", "heartbeat")
            payload: Message data dict
            
        Returns:
            Message ID
        """
        msg_id = str(uuid.uuid4())[:8]
        
        msg = Message(
            id=msg_id,
            sender=sender,
            recipient=recipient,
            type=msg_type,
            payload=payload,
            timestamp=datetime.now().isoformat()
        )
        
        msg_file = self.queue_dir / f"{msg_id}.json"
        
        try:
            with open(msg_file, 'w') as f:
                json.dump(msg.to_dict(), f, indent=2)
            return msg_id
        except Exception as e:
            print(f"[MQ ERROR] Failed to send message: {e}")
            return None
    
    def receive(self, recipient: str, block: bool = False, timeout: float = None) -> Optional[Message]:
        """
        Receive a message for a recipient.
        
        Args:
            recipient: ID of receiving agent (or "broadcast" for any)
            block: If True, wait for message
            timeout: Max seconds to wait if blocking
            
        Returns:
            Message or None
        """
        start_time = time.time()
        
        while True:
            self._acquire_lock()
            
            try:
                # Find undelivered messages for recipient
                for msg_file in sorted(self.queue_dir.glob("*.json")):
                    if msg_file.name.startswith('.'):
                        continue
                    
                    try:
                        with open(msg_file) as f:
                            data = json.load(f)
                        
                        msg = Message.from_dict(data)
                        
                        # Check if for this recipient (or broadcast)
                        if not msg.delivered and (msg.recipient == recipient or msg.recipient == "broadcast"):
                            # Mark delivered
                            msg.delivered = True
                            with open(msg_file, 'w') as f:
                                json.dump(msg.to_dict(), f, indent=2)
                            
                            self._release_lock()
                            return msg
                            
                    except Exception as e:
                        print(f"[MQ WARN] Corrupted message file {msg_file}: {e}")
                        continue
                
            finally:
                self._release_lock()
            
            # If not blocking, return None
            if not block:
                return None
            
            # Check timeout
            if timeout and (time.time() - start_time) > timeout:
                return None
            
            # Wait and retry
            time.sleep(0.1)
    
    def acknowledge(self, msg_id: str, processed: bool = True) -> bool:
        """
        Mark message as processed.
        
        Args:
            msg_id: Message ID to acknowledge
            processed: Whether processing succeeded
            
        Returns:
            True if acknowledged
        """
        self._acquire_lock()
        
        try:
            msg_file = self.queue_dir / f"{msg_id}.json"
            
            if not msg_file.exists():
                return False
            
            with open(msg_file) as f:
                data = json.load(f)
            
            data['processed'] = processed
            
            with open(msg_file, 'w') as f:
                json.dump(data, f, indent=2)
            
            return True
            
        finally:
            self._release_lock()
    
    def get_stats(self) -> dict:
        """Get queue statistics."""
        total = 0
        delivered = 0
        processed = 0
        
        for msg_file in self.queue_dir.glob("*.json"):
            if msg_file.name.startswith('.'):
                continue
            
            try:
                with open(msg_file) as f:
                    data = json.load(f)
                
                total += 1
                if data.get('delivered'):
                    delivered += 1
                if data.get('processed'):
                    processed += 1
            except:
                continue
        
        return {
            'total_messages': total,
            'delivered': delivered,
            'processed': processed,
            'pending': total - delivered
        }
    
    def cleanup(self, max_age_hours: int = 24) -> int:
        """
        Remove old processed messages.
        
        Args:
            max_age_hours: Remove messages older than this
            
        Returns:
            Number of messages removed
        """
        from datetime import timedelta
        
        cutoff = datetime.now() - timedelta(hours=max_age_hours)
        removed = 0
        
        self._acquire_lock()
        
        try:
            for msg_file in self.queue_dir.glob("*.json"):
                if msg_file.name.startswith('.'):
                    continue
                
                try:
                    with open(msg_file) as f:
                        data = json.load(f)
                    
                    # Only remove processed messages
                    if not data.get('processed'):
                        continue
                    
                    # Check age
                    msg_time = datetime.fromisoformat(data['timestamp'])
                    if msg_time < cutoff:
                        msg_file.unlink()
                        removed += 1
                        
                except Exception as e:
                    print(f"[MQ WARN] Cleanup error for {msg_file}: {e}")
                    continue
            
            return removed
            
        finally:
            self._release_lock()


def test_message_queue():
    """Test the message queue."""
    print("=" * 60)
    print("TESTING: FileMessageQueue")
    print("=" * 60)
    
    mq = FileMessageQueue("test")
    
    # Test 1: Send message
    print("\n1. Sending test message...")
    msg_id = mq.send(
        sender="orchestrator",
        recipient="agent_001",
        msg_type="task",
        payload={"command": "scan_ports", "target": "192.168.1.1"}
    )
    print(f"   Sent: {msg_id}")
    
    # Test 2: Receive message
    print("\n2. Receiving message...")
    msg = mq.receive("agent_001", block=False)
    if msg:
        print(f"   Received: {msg.type} from {msg.sender}")
        print(f"   Payload: {msg.payload}")
    
    # Test 3: Acknowledge
    print("\n3. Acknowledging message...")
    mq.acknowledge(msg_id, processed=True)
    print("   Done")
    
    # Test 4: Stats
    print("\n4. Queue stats:")
    stats = mq.get_stats()
    for k, v in stats.items():
        print(f"   {k}: {v}")
    
    # Test 5: Broadcast
    print("\n5. Testing broadcast...")
    broadcast_id = mq.send(
        sender="orchestrator",
        recipient="broadcast",
        msg_type="shutdown",
        payload={"reason": "maintenance"}
    )
    
    # Any recipient should get this
    msg = mq.receive("any_agent", block=False)
    if msg:
        print(f"   Broadcast received: {msg.type}")
    
    # Test 6: Empty receive
    print("\n6. Testing empty receive...")
    msg = mq.receive("no_messages_for_this", block=False)
    print(f"   Result: {'Got message (unexpected)' if msg else 'None (correct)'}")
    
    print("\n" + "=" * 60)
    print("All tests completed!")
    print("=" * 60)
    
    # Cleanup test messages
    mq.cleanup(max_age_hours=0)


if __name__ == "__main__":
    test_message_queue()
