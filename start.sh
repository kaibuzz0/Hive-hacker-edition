#!/bin/bash
#===============================================================================
# HIVE-HERMES STARTUP
# Launch both Hive OS and Hermes Agent with full integration
#===============================================================================

set -e

HIVE_ROOT="${HIVE_ROOT:-$HOME/.hive}"
HERMES_CONFIG="$HOME/.hermes"
PID_DIR="$HIVE_ROOT/run"

colors() {
    GREEN='\033[0;32m'
    BLUE='\033[0;34m'
    YELLOW='\033[1;33m'
    RED='\033[0;31m'
    NC='\033[0m'
}

print_banner() {
    clear
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║           🐝 HIVE + 🤖 HERMES INTEGRATED SYSTEM             ║"
    echo "║                                                              ║"
    echo "║              Termux AI-Powered Security Platform            ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

check_installation() {
    echo -e "${BLUE}🔍 Checking installation...${NC}"
    
    # Check Hive
    if [ ! -d "$HIVE_ROOT" ]; then
        echo -e "${RED}✗ Hive OS not installed${NC}"
        echo "   Run: ./setup.sh"
        exit 1
    fi
    
    # Check Hermes
    if [ ! -d "$HERMES_CONFIG" ]; then
        echo -e "${YELLOW}⚠ Hermes config not found${NC}"
        echo "   Hermes should be installed separately"
    fi
    
    echo -e "${GREEN}✓ Installation verified${NC}"
}

start_hive_daemon() {
    echo -e "${BLUE}🧠 Starting Hive Swarm Daemon...${NC}"
    
    # Start self-healing daemon
    if [ -f "$HIVE_ROOT/core/self_heal.py" ]; then
        nohup python3 "$HIVE_ROOT/core/self_heal.py" --daemon \
            > "$HIVE_ROOT/logs/healing.log" 2>&1 &
        echo $! > "$PID_DIR/healing.pid"
        echo -e "   ${GREEN}✓ Self-healing daemon started${NC}"
    fi
    
    # Start port manager
    if [ -f "$HIVE_ROOT/core/port_manager.sh" ]; then
        "$HIVE_ROOT/core/port_manager.sh" start
        echo -e "   ${GREEN}✓ Port manager started${NC}"
    fi
}

start_hermes_bridge() {
    echo -e "${BLUE}🔗 Starting Hermes Bridge...${NC}"
    
    if [ -f "$HIVE_ROOT/integration/hermes_bridge.py" ]; then
        nohup python3 "$HIVE_ROOT/integration/hermes_bridge.py" --daemon \
            > "$HIVE_ROOT/logs/hermes_bridge.log" 2>&1 &
        echo $! > "$PID_DIR/hermes_bridge.pid"
        echo -e "   ${GREEN}✓ Hermes bridge started${NC}"
    else
        echo -e "   ${YELLOW}⚠ Bridge not found${NC}"
    fi
}

show_status() {
    echo ""
    echo -e "${BLUE}📊 System Status:${NC}"
    echo "-" >&2
    
    # Check Hive daemon
    if [ -f "$PID_DIR/healing.pid" ] && kill -0 $(cat "$PID_DIR/healing.pid") 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} Hive Self-Healing: Running (PID: $(cat $PID_DIR/healing.pid))"
    else
        echo -e "   ${RED}✗${NC} Hive Self-Healing: Stopped"
    fi
    
    # Check Hermes bridge
    if [ -f "$PID_DIR/hermes_bridge.pid" ] && kill -0 $(cat "$PID_DIR/hermes_bridge.pid") 2>/dev/null; then
        echo -e "   ${GREEN}✓${NC} Hermes Bridge: Running (PID: $(cat $PID_DIR/hermes_bridge.pid))"
    else
        echo -e "   ${RED}✗${NC} Hermes Bridge: Stopped"
    fi
    
    # Check ports
    echo ""
    echo "   Ports:"
    for port in 8765 8766 8767; do
        if nc -z 127.0.0.1 $port 2>/dev/null; then
            echo -e "      ${GREEN}✓${NC} Port $port: Active"
        else
            echo -e "      ${YELLOW}⚠${NC} Port $port: Inactive"
        fi
    done
}

stop_all() {
    echo -e "${BLUE}🛑 Stopping all services...${NC}"
    
    # Stop Hive daemons
    for pid_file in "$PID_DIR"/*.pid; do
        if [ -f "$pid_file" ]; then
            pid=$(cat "$pid_file")
            if kill -0 "$pid" 2>/dev/null; then
                kill "$pid" 2>/dev/null || true
                echo -e "   ${GREEN}✓${NC} Stopped $(basename $pid_file .pid)"
            fi
            rm -f "$pid_file"
        fi
    done
    
    # Stop port manager
    "$HIVE_ROOT/core/port_manager.sh" stop 2>/dev/null || true
    
    echo -e "${GREEN}✓ All services stopped${NC}"
}

interactive_menu() {
    while true; do
        print_banner
        show_status
        
        echo ""
        echo "Options:"
        echo "  1. Start Hive Only"
        echo "  2. Start Full Integration (Hive + Hermes Bridge)"
        echo "  3. Stop All Services"
        echo "  4. View Logs"
        echo "  5. Run Health Check"
        echo "  6. Open Hive Menu"
        echo "  Q. Quit"
        echo ""
        
        read -p "Select: " choice
        
        case $choice in
            1)
                start_hive_daemon
                read -p "Press Enter to continue..."
                ;;
            2)
                start_hive_daemon
                start_hermes_bridge
                read -p "Press Enter to continue..."
                ;;
            3)
                stop_all
                read -p "Press Enter to continue..."
                ;;
            4)
                echo ""
                echo "Recent logs:"
                tail -20 "$HIVE_ROOT/logs/healing.log" 2>/dev/null || echo "No healing logs"
                echo ""
                tail -20 "$HIVE_ROOT/logs/hermes_bridge.log" 2>/dev/null || echo "No bridge logs"
                read -p "Press Enter to continue..."
                ;;
            5)
                python3 "$HIVE_ROOT/core/self_heal.py"
                read -p "Press Enter to continue..."
                ;;
            6)
                python3 "$HIVE_ROOT/hive.py"
                ;;
            Q|q)
                echo "Goodbye!"
                exit 0
                ;;
        esac
    done
}

# Main
case "${1:-menu}" in
    start)
        colors
        print_banner
        check_installation
        start_hive_daemon
        start_hermes_bridge
        show_status
        echo ""
        echo -e "${GREEN}✓ Hive + Hermes integration running!${NC}"
        ;;
    stop)
        colors
        stop_all
        ;;
    status)
        colors
        print_banner
        show_status
        ;;
    menu|*)
        colors
        interactive_menu
        ;;
esac
