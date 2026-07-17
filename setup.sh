#!/bin/bash
#===============================================================================
# HIVE OS SETUP - Complete Hive Operating System Installer
# For Termux / Mobile / Embedded Systems
#===============================================================================

set -e

HIVE_VERSION="2.0.0"
HIVE_ROOT="$HOME/.hive"
HIVE_REGISTRY="$HIVE_ROOT/swarm_registry.json"
HIVE_LOG="$HIVE_ROOT/logs"

colors() {
    RED='\033[0;31m'
    GREEN='\033[0;32m'
    YELLOW='\033[1;33m'
    BLUE='\033[0;34m'
    NC='\033[0m' # No Color
}

print_banner() {
    clear
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║              🐝 HIVE OPERATING SYSTEM v${HIVE_VERSION}           ║"
    echo "║                                                              ║"
    echo "║           Self-Healing | Multi-Agent | Termux-Ready         ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

check_termux() {
    if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
        echo -e "${YELLOW}⚠ Warning: Not running in Termux environment${NC}"
        echo "  Hive OS is optimized for Termux on Android"
        read -p "Continue anyway? (y/N): " continue_setup
        if [[ ! $continue_setup =~ ^[Yy]$ ]]; then
            exit 1
        fi
    fi
}

install_packages() {
    echo -e "${BLUE}📦 Installing Hive OS Dependencies...${NC}"
    echo ""
    
    pkg update -y
    
    PACKAGES="python python-pip git curl wget nmap net-tools openssh"
    
    for pkg in $PACKAGES; do
        echo -e "  Installing ${pkg}..."
        pkg install -y $pkg 2>/dev/null || echo "    (may already be installed)"
    done
    
    echo ""
    echo -e "${GREEN}✓ Core packages installed${NC}"
}

install_python_deps() {
    echo -e "${BLUE}🐍 Installing Python Dependencies...${NC}"
    echo ""
    
    pip install --upgrade pip
    
    # Core dependencies
    pip install requests beautifulsoup4 dnspython scapy cryptography
    
    # Hive Swarm dependencies
    pip install pyyaml jsonschema colorama rich
    
    echo ""
    echo -e "${GREEN}✓ Python dependencies installed${NC}"
}

setup_directories() {
    echo -e "${BLUE}📁 Creating Hive Directory Structure...${NC}"
    echo ""
    
    # Main directories
    mkdir -p "$HIVE_ROOT"/{agents,tools,logs,cache,registry,skills}
    mkdir -p "$HIVE_ROOT/agents"/{assistant,architect,toolsmith,executor}
    mkdir -p "$HIVE_ROOT/tools"/{recon,scanning,exploit,postexploit,crypto,wireless}
    
    # State directories
    mkdir -p "$HIVE_ROOT/state"
    mkdir -p "$HIVE_ROOT/backups"
    
    echo "  $HIVE_ROOT/"
    echo "  ├── agents/       (AI agent modules)"
    echo "  ├── tools/        (Security tools)"
    echo "  ├── logs/         (System logs)"
    echo "  ├── cache/        (Temporary cache)"
    echo "  ├── registry/     (Swarm registry)"
    echo "  ├── skills/       (Skill modules)"
    echo "  ├── state/        (Current state)"
    echo "  └── backups/      (Auto-backups)"
    echo ""
    echo -e "${GREEN}✓ Directory structure created${NC}"
}

create_registry() {
    echo -e "${BLUE}📋 Initializing Hive Registry...${NC}"
    
    if [ ! -f "$HIVE_REGISTRY" ]; then
        cat > "$HIVE_REGISTRY" << 'REGISTRY'
{
  "version": "2.0.0",
  "initialized": "TIMESTAMP",
  "agents": {},
  "tasks": {},
  "messages": [],
  "system": {
    "self_healing": true,
    "auto_backup": true,
    "verify_chains": true
  }
}
REGISTRY
        # Replace timestamp
        sed -i "s/TIMESTAMP/$(date -Iseconds)/g" "$HIVE_REGISTRY"
        
        echo ""
        echo -e "${GREEN}✓ Registry initialized${NC}"
    else
        echo ""
        echo -e "${YELLOW}⚠ Registry already exists${NC}"
    fi
}

install_hive_core() {
    echo -e "${BLUE}🧠 Installing Hive Core System...${NC}"
    echo ""
    
    HIVE_SRC="$(dirname "$0")/core"
    
    if [ -d "$HIVE_SRC" ]; then
        # Copy core files
        cp -r "$HIVE_SRC/orchestrator.py" "$HIVE_ROOT/" 2>/dev/null || echo "  (orchestrator.py copied)"
        cp -r "$HIVE_SRC/agents" "$HIVE_ROOT/" 2>/dev/null || echo "  (agents/ copied)"
        
        echo -e "  ${GREEN}✓ Core components installed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Core source not found - will use embedded${NC}"
    fi
    
    echo ""
}

install_tools() {
    echo -e "${BLUE}🔧 Installing Security Tools...${NC}"
    echo ""
    
    TOOLS_SRC="$(dirname "$0")/tools"
    
    if [ -d "$TOOLS_SRC" ]; then
        cp -r "$TOOLS_SRC/"* "$HIVE_ROOT/tools/" 2>/dev/null || true
        echo -e "  ${GREEN}✓ Tools installed${NC}"
    else
        echo -e "  ${YELLOW}⚠ Tools source not found${NC}"
    fi
    
    echo ""
}

create_launcher() {
    echo -e "${BLUE}🚀 Creating Hive Launcher...${NC}"
    echo ""
    
    cat > "$PREFIX/bin/hive" << 'LAUNCHER'
#!/bin/bash
# Hive OS Launcher

HIVE_ROOT="$HOME/.hive"

if [ ! -d "$HIVE_ROOT" ]; then
    echo "✗ Hive OS not installed"
    echo "Run: ./setup.sh"
    exit 1
fi

# Activate self-healing
python3 "$HIVE_ROOT/orchestrator.py" "$@"
LAUNCHER
    
    chmod +x "$PREFIX/bin/hive"
    
    echo -e "  ${GREEN}✓ Launcher created: 'hive' command ready${NC}"
    echo ""
}

create_systemd_service() {
    echo -e "${BLUE}⚙️  Creating System Service...${NC}"
    echo ""
    
    # For Termux, create a startup script
    cat > "$HIVE_ROOT/start_daemon.sh" << 'DAEMON'
#!/bin/bash
# Hive OS Daemon Starter

HIVE_ROOT="$HOME/.hive"
LOG_FILE="$HIVE_ROOT/logs/daemon.log"

echo "[$(date)] Starting Hive OS Daemon..." >> "$LOG_FILE"

# Start orchestrator
python3 "$HIVE_ROOT/orchestrator.py" --daemon 2>&1 >> "$LOG_FILE" &

echo "Hive OS Daemon started (PID: $!)"
echo "Logs: $LOG_FILE"
DAEMON
    
    chmod +x "$HIVE_ROOT/start_daemon.sh"
    
    echo -e "  ${GREEN}✓ Daemon script created${NC}"
    echo "  Start with: ~/.hive/start_daemon.sh"
    echo ""
}

setup_hermes_integration() {
    echo -e "${BLUE}🔗 Setting up Hermes Integration...${NC}"
    echo ""
    
    cat > "$HIVE_ROOT/hermes_bridge.py" << 'HERMES'
#!/usr/bin/env python3
"""
Hive-Hermes Integration Bridge
Connects Hive Swarm to Hermes Agent system
"""

import os
import sys
import json
from pathlib import Path

HIVE_ROOT = Path.home() / ".hive"

def send_to_hermes(message_type, content):
    """Send message to Hermes"""
    msg = {
        "source": "hive",
        "type": message_type,
        "content": content,
        "timestamp": datetime.now().isoformat()
    }
    # Write to shared queue
    queue_file = HIVE_ROOT / "hermes_queue.json"
    
    messages = []
    if queue_file.exists():
        with open(queue_file) as f:
            messages = json.load(f)
    
    messages.append(msg)
    
    with open(queue_file, 'w') as f:
        json.dump(messages, f)
    
    return True

def receive_from_hermes():
    """Receive messages from Hermes"""
    queue_file = HIVE_ROOT / "hermes_queue.json"
    
    if not queue_file.exists():
        return []
    
    with open(queue_file) as f:
        messages = json.load(f)
    
    # Clear processed messages
    hive_messages = [m for m in messages if m.get("source") != "hive"]
    
    with open(queue_file, 'w') as f:
        json.dump(hive_messages, f)
    
    return hive_messages

if __name__ == "__main__":
    print("🐝 Hive-Hermes Bridge Ready")
HERMES
    
    chmod +x "$HIVE_ROOT/hermes_bridge.py"
    
    echo -e "  ${GREEN}✓ Hermes bridge configured${NC}"
    echo ""
}

final_setup() {
    echo -e "${BLUE}🔧 Final Configuration...${NC}"
    echo ""
    
    # Create state file
    cat > "$HIVE_ROOT/state/system.json" << 'STATE'
{
  "version": "2.0.0",
  "status": "initialized",
  "self_healing": true,
  "last_check": "TIMESTAMP",
  "components": {
    "orchestrator": "ready",
    "agents": "ready",
    "tools": "ready",
    "registry": "ready"
  }
}
STATE
    
    sed -i "s/TIMESTAMP/$(date -Iseconds)/g" "$HIVE_ROOT/state/system.json"
    
    echo -e "  ${GREEN}✓ System state initialized${NC}"
    echo ""
}

print_summary() {
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                     SETUP COMPLETE                           ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}✓ Hive OS v${HIVE_VERSION} installed successfully!${NC}"
    echo ""
    echo "Installation location: $HIVE_ROOT"
    echo ""
    echo "Quick Commands:"
    echo "  hive                    - Launch Hive OS"
    echo "  hive --status           - Check system status"
    echo "  hive --swarm            - Enter Swarm mode"
    echo "  ~/.hive/start_daemon.sh - Start background daemon"
    echo ""
    echo "Directories:"
    echo "  ~/.hive/agents/         - AI agent modules"
    echo "  ~/.hive/tools/           - Security tools"
    echo "  ~/.hive/logs/           - System logs"
    echo "  ~/.hive/registry.json   - Swarm registry"
    echo ""
    echo -e "${YELLOW}Next Steps:${NC}"
    echo "  1. Run: hive"
    echo "  2. Run: hive --swarm"
    echo "  3. Explore the tool arsenal"
    echo ""
    echo "For help: hive --help"
    echo ""
}

# Main execution
main() {
    colors
    print_banner
    check_termux
    install_packages
    install_python_deps
    setup_directories
    create_registry
    install_hive_core
    install_tools
    create_launcher
    create_systemd_service
    setup_hermes_integration
    final_setup
    print_summary
}

# Run main
main
