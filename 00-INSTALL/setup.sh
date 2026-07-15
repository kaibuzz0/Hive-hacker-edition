#!/bin/bash
# Hive Hacker Edition - Installation Script

echo "========================================"
echo "  HIVE HACKER EDITION SETUP"
echo "========================================"
echo ""

# Update packages
echo "[1/5] Updating Termux packages..."
pkg update -y && pkg upgrade -y

# Install core dependencies
echo "[2/5] Installing core dependencies..."
pkg install -y python python-pip git curl wget nmap ncat openssl

# Install Python packages
echo "[3/5] Installing Python security tools..."
pip install requests cryptography scapy paramiko pycryptodome

# Setup environment
echo "[4/5] Configuring environment..."
mkdir -p ~/tools
cp -r ./* ~/tools/

# Add to PATH
echo "[5/5] Updating PATH..."
echo 'export PATH="$HOME/tools:$PATH"' >> ~/.bashrc

echo ""
echo "========================================"
echo "  SETUP COMPLETE!"
echo "========================================"
echo ""
echo "Next steps:"
echo "  1. source ~/.bashrc"
echo "  2. cd ~/tools"
echo "  3. Read LEGAL_NOTICE.txt"
echo "  4. Start with: ./00-INSTALL/verify.sh"
echo ""
echo "Happy (ethical) hacking! 🐝"
