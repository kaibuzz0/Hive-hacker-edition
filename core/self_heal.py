#!/usr/bin/env python3
"""
HIVE OS - Self-Healing System
Automatically detects and repairs system issues
"""

import os
import sys
import json
import time
import subprocess
from pathlib import Path
from datetime import datetime

HIVE_ROOT = Path.home() / ".hive"
LOG_FILE = HIVE_ROOT / "logs" / "healing.log"
STATE_FILE = HIVE_ROOT / "state" / "system.json"
REPAIR_LOG = HIVE_ROOT / "logs" / "repairs.json"

class SelfHealingSystem:
    """Self-healing and monitoring system"""
    
    def __init__(self):
        self.checks = []
        self.repairs = []
        self._ensure_dirs()
        
    def _ensure_dirs(self):
        """Ensure log directories exist"""
        LOG_FILE.parent.mkdir(parents=True, exist_ok=True)
        (HIVE_ROOT / "state").mkdir(parents=True, exist_ok=True)
    
    def log(self, message, level="INFO"):
        """Log to healing log"""
        timestamp = datetime.now().isoformat()
        entry = f"[{timestamp}] [{level}] {message}"
        print(entry)
        
        with open(LOG_FILE, 'a') as f:
            f.write(entry + "\n")
    
    def check_registry(self):
        """Check if registry is valid"""
        registry_file = HIVE_ROOT / "registry.json"
        
        if not registry_file.exists():
            self.log("Registry missing - creating", "REPAIR")
            self._create_default_registry()
            return False
        
        try:
            with open(registry_file) as f:
                data = json.load(f)
            
            # Check required keys
            required = ['version', 'agents', 'tasks']
            for key in required:
                if key not in data:
                    self.log(f"Registry missing key: {key}", "WARNING")
                    return False
            
            return True
        except json.JSONDecodeError:
            self.log("Registry corrupted - repairing", "REPAIR")
            self._backup_and_recreate_registry()
            return False
    
    def _create_default_registry(self):
        """Create default registry"""
        default = {
            "version": "2.0.0",
            "initialized": datetime.now().isoformat(),
            "agents": {},
            "tasks": {},
            "messages": [],
            "system": {
                "self_healing": True,
                "auto_backup": True,
                "verify_chains": True
            }
        }
        
        with open(HIVE_ROOT / "registry.json", 'w') as f:
            json.dump(default, f, indent=2)
        
        self.log("Default registry created", "REPAIR")
    
    def _backup_and_recreate_registry(self):
        """Backup corrupted registry and recreate"""
        registry_file = HIVE_ROOT / "registry.json"
        backup_file = HIVE_ROOT / "backups" / f"registry_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        # Backup
        backup_file.parent.mkdir(parents=True, exist_ok=True)
        if registry_file.exists():
            os.rename(registry_file, backup_file)
            self.log(f"Corrupted registry backed up to {backup_file}", "REPAIR")
        
        # Recreate
        self._create_default_registry()
    
    def check_agents(self):
        """Check if agent modules exist"""
        agents_dir = HIVE_ROOT / "agents"
        required_agents = ['orchestrator.py']
        
        missing = []
        for agent in required_agents:
            if not (agents_dir / agent).exists():
                missing.append(agent)
        
        if missing:
            self.log(f"Missing agents: {missing}", "WARNING")
            return False
        
        return True
    
    def check_ports(self):
        """Check if required ports are available"""
        import socket
        
        ports = [8765, 8766, 8767]  # Hive daemon, Hermes, Swarm
        
        for port in ports:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex(('127.0.0.1', port))
            sock.close()
            
            if result == 0:
                self.log(f"Port {port} active", "INFO")
            else:
                self.log(f"Port {port} not responding", "WARNING")
        
        return True
    
    def check_disk_space(self):
        """Check available disk space"""
        stat = os.statvfs(HIVE_ROOT)
        free_gb = (stat.f_bavail * stat.f_frsize) / (1024**3)
        
        if free_gb < 1.0:
            self.log(f"Low disk space: {free_gb:.2f}GB remaining", "WARNING")
            return False
        
        self.log(f"Disk space OK: {free_gb:.2f}GB free", "INFO")
        return True
    
    def run_health_check(self):
        """Run full health check"""
        self.log("=" * 60)
        self.log("Starting health check...")
        
        checks = [
            ("Registry", self.check_registry),
            ("Agents", self.check_agents),
            ("Ports", self.check_ports),
            ("Disk Space", self.check_disk_space),
        ]
        
        results = {}
        for name, check_func in checks:
            try:
                result = check_func()
                results[name] = "PASS" if result else "FAIL"
            except Exception as e:
                self.log(f"Check {name} error: {e}", "ERROR")
                results[name] = "ERROR"
        
        # Update state
        self._update_state(results)
        
        self.log("Health check complete")
        self.log(f"Results: {results}")
        
        return results
    
    def _update_state(self, results):
        """Update system state file"""
        state = {}
        if STATE_FILE.exists():
            with open(STATE_FILE) as f:
                state = json.load(f)
        
        state['last_check'] = datetime.now().isoformat()
        state['health'] = results
        state['status'] = 'healthy' if all(r == 'PASS' for r in results.values()) else 'degraded'
        
        with open(STATE_FILE, 'w') as f:
            json.dump(state, f, indent=2)
    
    def repair_all(self):
        """Attempt to repair all issues"""
        self.log("Starting repair process...")
        
        repairs_made = []
        
        # Repair registry
        if not self.check_registry():
            self._create_default_registry()
            repairs_made.append("registry_recreated")
        
        # Clean old logs
        self._clean_old_logs()
        repairs_made.append("logs_cleaned")
        
        self.log(f"Repairs complete: {repairs_made}")
        
        # Save repair log
        repair_entry = {
            "timestamp": datetime.now().isoformat(),
            "repairs": repairs_made
        }
        
        repairs = []
        if REPAIR_LOG.exists():
            with open(REPAIR_LOG) as f:
                repairs = json.load(f)
        
        repairs.append(repair_entry)
        
        with open(REPAIR_LOG, 'w') as f:
            json.dump(repairs[-100:], f, indent=2)  # Keep last 100
    
    def _clean_old_logs(self):
        """Clean old log files"""
        logs_dir = HIVE_ROOT / "logs"
        if logs_dir.exists():
            # Keep only last 30 days of logs
            cutoff = time.time() - (30 * 24 * 60 * 60)
            
            for log_file in logs_dir.glob("*.log"):
                if log_file.stat().st_mtime < cutoff:
                    log_file.unlink()
                    self.log(f"Cleaned old log: {log_file.name}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Hive OS Self-Healing System')
    parser.add_argument('--check', action='store_true', help='Run health check')
    parser.add_argument('--repair', action='store_true', help='Run repairs')
    parser.add_argument('--daemon', action='store_true', help='Run as daemon')
    
    args = parser.parse_args()
    
    healer = SelfHealingSystem()
    
    if args.daemon:
        print("🔄 Self-healing daemon started")
        while True:
            healer.run_health_check()
            time.sleep(300)  # Check every 5 minutes
    
    elif args.repair:
        healer.repair_all()
    
    else:
        healer.run_health_check()

if __name__ == "__main__":
    main()
