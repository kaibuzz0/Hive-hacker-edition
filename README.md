# 🐝 HIVE OS - Hacker Edition

**Self-Healing | Multi-Agent | Termux-Ready Operating System**

Complete Hive Operating System for penetration testing, security research, and AI-powered automation. Designed for Termux on Android.

## 📱 ONE-LINE INSTALL (EASIEST)

**Open Termux and paste this single command:**

```bash
curl -sSL https://raw.githubusercontent.com/kaibuzz0/Hive-hacker-edition/main/install.sh | bash
```

That's it! The installer handles everything automatically.

## 📱 PHONE REPLACEMENT WORKFLOW

**Lost your phone? Get a new one and restore everything in minutes:**

```bash
# 1. Install Termux from F-Droid
# 2. Open Termux and paste:

curl -sSL https://raw.githubusercontent.com/kaibuzz0/Hive-hacker-edition/main/install.sh | bash

# Done! Your complete Hive OS is restored.
```

## 🏗️ SYSTEM ARCHITECTURE

```
Hive OS v2.0.0
├── Core Swarm (AI Multi-Agent System)
│   ├── orchestrator.py      - Task delegation & verification
│   ├── assistant_agent.py   - Quality verification
│   ├── architect_agent.py   - Code & security review
│   ├── self_heal.py         - Auto-repair system
│   ├── port_manager.sh      - Network configuration
│   └── backup_manager.py    - Backup & restore
│
├── Security Tools (17+ tools)
│   ├── 10-RECON/            - Reconnaissance
│   ├── 20-SCANNING/         - Network scanning
│   ├── 30-EXPLOITATION/     - Exploitation
│   ├── 40-POST-EXPLOIT/     - Post-exploitation
│   ├── 50-REPORTING/        - Reporting & forensics
│   ├── 60-ANONYMITY/        - Tor & privacy
│   ├── 70-CRYPTO/           - Cryptography
│   └── 80-WIRELESS/         - Wireless tools
│
└── Integration
    ├── setup.sh             - One-command installer
    ├── manifest.json        - Dependencies
    └── hive.py              - Unified launcher
```

## 🚀 QUICK START

### Fresh Installation

```bash
./setup.sh
```

This will:
- Install all dependencies (Termux packages + Python modules)
- Create `~/.hive/` directory structure
- Initialize Swarm registry
- Install 17+ security tools
- Configure Hermes integration
- Create `hive` command

### Launch Hive OS

```bash
hive                    # Interactive menu
hive --swarm            # Enter Swarm AI mode
hive --status           # System health check
hive --help             # Show help
```

## 🔧 SYSTEM COMPONENTS

### Self-Healing System

```bash
# Check system health
python3 ~/.hive/core/self_heal.py

# Run repairs
python3 ~/.hive/core/self_heal.py --repair

# Run as daemon (auto-heal every 5 minutes)
python3 ~/.hive/core/self_heal.py --daemon
```

### Port Management

```bash
# Initialize network config
~/.hive/core/port_manager.sh init

# Check port status
~/.hive/core/port_manager.sh status

# Switch service ports
~/.hive/core/port_manager.sh switch daemon 8765

# Repair network issues
~/.hive/core/port_manager.sh repair
```

### Backup & Restore

```bash
# Create backup
python3 ~/.hive/core/backup_manager.py create --name my_backup

# List backups
python3 ~/.hive/core/backup_manager.py list

# Restore from backup
python3 ~/.hive/core/backup_manager.py restore --file backup.tar.gz

# Export for GitHub (clean, no private data)
python3 ~/.hive/core/backup_manager.py export --output ./hive-clean
```

## 🧠 SWARM MODE

The Hive Swarm provides AI-powered task delegation:

```
User → Main AI → Swarm → Agent → Architect Review → Assistant Verification → Delivery
```

### Using Swarm

```python
from core.orchestrator import SwarmOrchestrator

orch = SwarmOrchestrator()

# Delegate task
task_id = orch.delegate_task("Scan network 192.168.1.0/24", "executor_agent")

# Check status
status = orch.get_status_report()
print(status)
```

## 📦 DEPENDENCIES

### System Packages
- python, python-pip, git, curl, wget
- nmap, net-tools, openssh
- termux-api, jq

### Python Packages
- requests, beautifulsoup4, dnspython, scapy
- cryptography, pyyaml, jsonschema
- colorama, rich, prompt-toolkit

## 🔐 SECURITY FEATURES

- **Self-healing**: Auto-detects and repairs registry corruption
- **Verification chains**: Every task verified before delivery
- **Clean backups**: Export removes all private data (tokens, paths)
- **Port isolation**: Services run on isolated ports with proxy support
- **Auto-backup**: Automatic backups before any restore operation

## 🔄 HERMES INTEGRATION

The Hive OS connects to Hermes Agent via:
- Port 8766 (Hermes Bridge)
- Shared JSON queue at `~/.hive/hermes_queue.json`
- Bidirectional message passing

## 📊 SYSTEM STATUS

Check complete system status:

```bash
hive --status
```

Shows:
- Agent status
- Task queue
- Port availability
- Disk space
- Registry health

## 🆘 TROUBLESHOOTING

### Registry Corrupted?
```bash
python3 ~/.hive/core/self_heal.py --repair
```

### Ports Not Responding?
```bash
~/.hive/core/port_manager.sh repair
```

### Need Clean Slate?
```bash
rm -rf ~/.hive
./setup.sh
```

## 📝 MANIFEST

See `manifest.json` for complete dependency and configuration specification.

## 🤝 WORKFLOW

1. **Daily Use**: Run `hive` and use tools/swarm
2. **Before Changes**: `backup_manager.py create`
3. **Phone Breaks**: New phone → `git clone` → `./setup.sh` → Restored!

## ⚠️ DISCLAIMER

For authorized security testing only. All tools included are for educational and professional security research purposes.

---

**Hive OS v2.0.0** | Self-Healing Multi-Agent System | Termux-Ready
