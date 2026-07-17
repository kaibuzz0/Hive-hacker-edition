#!/bin/bash
#===============================================================================
# HIVE OS - ONE-LINE INSTALLER
# curl -sSL https://raw.githubusercontent.com/kaibuzz0/Hive-hacker-edition/main/install.sh | bash
#===============================================================================

set -e

REPO_URL="https://github.com/kaibuzz0/Hive-hacker-edition.git"
INSTALL_DIR="$HOME/Hive-hacker-edition"
HIVE_ROOT="$HOME/.hive"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
CYAN='\033[0;36m'
NC='\033[0m'

print_banner() {
    clear
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                                                              ║"
    echo "║                 🐝 HIVE OS INSTALLER                         ║"
    echo "║                                                              ║"
    echo "║              One-Command Installation                        ║"
    echo "║        Termux • Android • Self-Healing • Multi-Agent         ║"
    echo "║                                                              ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
}

check_termux() {
    echo -e "${BLUE}📱 Checking environment...${NC}"
    
    if [ -z "$TERMUX_VERSION" ] && [ ! -d "/data/data/com.termux" ]; then
        echo -e "${YELLOW}⚠ Warning: Not in Termux${NC}"
        echo "  This installer is optimized for Termux on Android"
        echo ""
        read -p "Continue anyway? [y/N]: " -n 1 -r
        echo ""
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            exit 1
        fi
    else
        echo -e "${GREEN}✓ Termux detected${NC}"
    fi
}

install_prerequisites() {
    echo ""
    echo -e "${BLUE}📦 Installing prerequisites...${NC}"
    echo ""
    
    # Update packages
    echo "  Updating package lists..."
    pkg update -y >/dev/null 2>&1
    
    # Install required packages
    echo "  Installing git..."
    pkg install -y git >/dev/null 2>&1
    
    echo -e "${GREEN}✓ Prerequisites installed${NC}"
}

clone_repo() {
    echo ""
    echo -e "${BLUE}⬇️  Downloading Hive OS...${NC}"
    echo ""
    
    if [ -d "$INSTALL_DIR" ]; then
        echo -e "${YELLOW}⚠ Hive OS already exists at $INSTALL_DIR${NC}"
        read -p "  Reinstall? [y/N]: " -n 1 -r
        echo ""
        if [[ $REPLY =~ ^[Yy]$ ]]; then
            rm -rf "$INSTALL_DIR"
        else
            echo "  Using existing installation..."
            return
        fi
    fi
    
    echo "  Cloning from GitHub..."
    git clone --depth 1 "$REPO_URL" "$INSTALL_DIR" >/dev/null 2>&1
    
    echo -e "${GREEN}✓ Downloaded to $INSTALL_DIR${NC}"
}

run_setup() {
    echo ""
    echo -e "${BLUE}🔧 Running Hive OS Setup...${NC}"
    echo ""
    
    cd "$INSTALL_DIR"
    
    if [ -f "setup.sh" ]; then
        chmod +x setup.sh
        ./setup.sh
    else
        echo -e "${RED}✗ Setup script not found!${NC}"
        exit 1
    fi
}

show_complete() {
    echo ""
    echo ""
    echo "╔══════════════════════════════════════════════════════════════╗"
    echo "║                   🎉 INSTALLATION COMPLETE                   ║"
    echo "╚══════════════════════════════════════════════════════════════╝"
    echo ""
    echo -e "${GREEN}Hive OS is now installed and ready!${NC}"
    echo ""
    echo "Quick Commands:"
    echo "  hive              - Launch Hive OS menu"
    echo "  hive --swarm      - Enter AI Swarm mode"
    echo "  ./start.sh        - Start Hive + Hermes integration"
    echo ""
    echo "Directories:"
    echo "  ~/.hive/          - Hive OS root"
    echo "  ~/.hive/logs/     - System logs"
    echo "  ~/.hive/agents/   - AI agents"
    echo "  ~/.hive/tools/    - Security tools"
    echo ""
    echo "Documentation:"
    echo "  cat README.md     - Main documentation"
    echo "  cat integration/README.md - Hermes integration"
    echo ""
    echo -e "${CYAN}Type 'hive' to get started!${NC}"
    echo ""
}

# Main
main() {
    print_banner
    check_termux
    install_prerequisites
    clone_repo
    run_setup
    show_complete
}

# Run
main
