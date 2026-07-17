#!/bin/bash
#===============================================================================
# HIVE OS - Port Configuration & Proxy Manager
# Manages port switching, proxy settings, and network integration
#===============================================================================

HIVE_ROOT="${HIVE_ROOT:-$HOME/.hive}"
CONFIG_FILE="$HIVE_ROOT/config/network.conf"
PID_FILE="$HIVE_ROOT/run/proxy.pid"

create_network_config() {
    mkdir -p "$HIVE_ROOT/config"
    mkdir -p "$HIVE_ROOT/run"
    
    cat > "$CONFIG_FILE" << 'CONFIG'
# Hive OS Network Configuration

# Daemon Ports
HIVE_DAEMON_PORT=8765
HERMES_BRIDGE_PORT=8766
SWARM_COMM_PORT=8767
BACKUP_PORT=8768

# Proxy Settings
PROXY_ENABLED=true
PROXY_TYPE=socks5
PROXY_HOST=127.0.0.1
PROXY_PORT=9050

# Port Forwarding
FORWARD_LOCAL=8080
FORWARD_REMOTE=80

# Hermes Integration
HERMES_HOST=127.0.0.1
HERMES_PORT=8080
HERMES_PROTOCOL=http

# Self-Healing Network Checks
CHECK_INTERVAL=300
AUTO_REPAIR=true
BACKUP_PROXY_PORT=9150
CONFIG
    
    echo "✓ Network configuration created"
}

start_proxy() {
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        create_network_config
        source "$CONFIG_FILE"
    fi
    
    echo "🌐 Starting Hive Network Proxy..."
    
    # Check if proxy is already running
    if [ -f "$PID_FILE" ] && kill -0 $(cat "$PID_FILE") 2>/dev/null; then
        echo "⚠ Proxy already running (PID: $(cat $PID_FILE))"
        return
    fi
    
    # Start proxy daemon (simplified for Termux)
    # In production, this would start a proper SOCKS5/HTTP proxy
    (
        while true; do
            # Port health check
            for port in $HIVE_DAEMON_PORT $HERMES_BRIDGE_PORT $SWARM_COMM_PORT; do
                if ! nc -z 127.0.0.1 $port 2>/dev/null; then
                    echo "[$(date)] Port $port not responding" >> "$HIVE_ROOT/logs/proxy.log"
                fi
            done
            sleep $CHECK_INTERVAL
        done
    ) &
    
    echo $! > "$PID_FILE"
    echo "✓ Proxy daemon started (PID: $!)"
}

stop_proxy() {
    if [ -f "$PID_FILE" ]; then
        PID=$(cat "$PID_FILE")
        if kill -0 "$PID" 2>/dev/null; then
            kill "$PID"
            rm "$PID_FILE"
            echo "✓ Proxy stopped"
        else
            echo "⚠ Proxy not running"
            rm -f "$PID_FILE"
        fi
    else
        echo "⚠ Proxy not running"
    fi
}

switch_port() {
    local service=$1
    local new_port=$2
    
    echo "🔄 Switching $service to port $new_port..."
    
    # Update config
    case $service in
        daemon)
            sed -i "s/HIVE_DAEMON_PORT=.*/HIVE_DAEMON_PORT=$new_port/" "$CONFIG_FILE"
            ;;
        hermes)
            sed -i "s/HERMES_BRIDGE_PORT=.*/HERMES_BRIDGE_PORT=$new_port/" "$CONFIG_FILE"
            ;;
        swarm)
            sed -i "s/SWARM_COMM_PORT=.*/SWARM_COMM_PORT=$new_port/" "$CONFIG_FILE"
            ;;
        *)
            echo "✗ Unknown service: $service"
            return 1
            ;;
    esac
    
    echo "✓ Port switched. Restart services to apply."
}

setup_port_forward() {
    local local_port=$1
    local remote_port=$2
    
    echo "📡 Setting up port forward: $local_port -> $remote_port"
    
    # For Termux, use simple TCP forward
    (
        nc -l -p "$local_port" -c "nc 127.0.0.1 $remote_port" &
    )
    
    echo "✓ Port forward established"
}

check_ports() {
    echo "🔍 Checking Hive Port Status..."
    echo ""
    
    if [ -f "$CONFIG_FILE" ]; then
        source "$CONFIG_FILE"
    else
        echo "✗ No configuration found"
        return 1
    fi
    
    ports=(
        "Hive Daemon:$HIVE_DAEMON_PORT"
        "Hermes Bridge:$HERMES_BRIDGE_PORT"
        "Swarm Comm:$SWARM_COMM_PORT"
        "Backup:$BACKUP_PORT"
    )
    
    for service_port in "${ports[@]}"; do
        IFS=: read -r service port <<< "$service_port"
        if nc -z 127.0.0.1 "$port" 2>/dev/null; then
            echo "  ✓ $service: port $port (active)"
        else
            echo "  ✗ $service: port $port (inactive)"
        fi
    done
}

repair_ports() {
    echo "🔧 Repairing Hive Network..."
    
    # Restart proxy
    stop_proxy
    sleep 1
    start_proxy
    
    # Check all services
    check_ports
    
    echo "✓ Network repair complete"
}

show_help() {
    echo ""
    echo "Hive OS Network Manager"
    echo ""
    echo "Usage: port_manager.sh [command]"
    echo ""
    echo "Commands:"
    echo "  init           - Create initial network config"
    echo "  start          - Start proxy daemon"
    echo "  stop           - Stop proxy daemon"
    echo "  status         - Check port status"
    echo "  switch <svc> <port>  - Switch service port"
    echo "  forward <local> <remote> - Port forwarding"
    echo "  repair         - Repair network issues"
    echo "  help           - Show this help"
    echo ""
}

# Main
case "${1:-help}" in
    init)
        create_network_config
        ;;
    start)
        start_proxy
        ;;
    stop)
        stop_proxy
        ;;
    status)
        check_ports
        ;;
    switch)
        switch_port "$2" "$3"
        ;;
    forward)
        setup_port_forward "$2" "$3"
        ;;
    repair)
        repair_ports
        ;;
    help|--help|-h)
        show_help
        ;;
    *)
        echo "✗ Unknown command: $1"
        show_help
        exit 1
        ;;
esac
