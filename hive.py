#!/usr/bin/env python3
"""
HIVE HACKER EDITION - Core Arsenal
Ultimate Penetration Testing & Security Research Toolkit
For Termux / Mobile / Embedded Systems

DISCLAIMER: For authorized security testing only.
"""

import sys
import os
import subprocess
import json
from pathlib import Path
from datetime import datetime

# Module categories
MODULES = {
    "recon": {
        "name": "Reconnaissance",
        "tools": ["domain_enum", "subdomain_brute", "port_scan", "service_detect"],
        "path": "10-RECON"
    },
    "scanning": {
        "name": "Vulnerability Scanning", 
        "tools": ["web_scan", "api_fuzz", "dir_brute", "tech_fingerprint"],
        "path": "20-SCANNING"
    },
    "exploitation": {
        "name": "Exploitation",
        "tools": ["payload_gen", "shell_handler", "privesc_check", "lateral_move"],
        "path": "30-EXPLOITATION"
    },
    "post_exploit": {
        "name": "Post-Exploitation",
        "tools": ["persistence", "data_exfil", "log_wipe", "backdoor"],
        "path": "40-POST-EXPLOIT"
    },
    "reporting": {
        "name": "Reporting",
        "tools": ["screenshot", "evidence_collector", "report_gen", "timeline"],
        "path": "50-REPORTING"
    },
    "anonymity": {
        "name": "Anonymity & OPSEC",
        "tools": ["tor_route", "mac_spoof", "dns_tunnel", "traffic_shape"],
        "path": "60-ANONYMITY"
    },
    "crypto": {
        "name": "Cryptography",
        "tools": ["hash_crack", "cipher_break", "stego", "blockchain_analyze"],
        "path": "70-CRYPTO"
    },
    "wireless": {
        "name": "Wireless",
        "tools": ["wifi_scan", "wpa_crack", "evil_twin", "bluetooth_sniff"],
        "path": "80-WIRELESS"
    },
    "social": {
        "name": "Social Engineering",
        "tools": ["phish_template", "sms_spoof", "caller_id", "pretext_gen"],
        "path": "90-SOCIAL-ENG"
    }
}

class HiveHacker:
    """Main controller for the HIVE HACKER EDITION"""
    
    def __init__(self, base_path="~/hive-hacker"):
        self.base_path = Path(base_path).expanduser()
        self.session_id = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.base_path / "logs" / f"session_{self.session_id}.log"
        
        # Ensure log directory exists
        self.log_file.parent.mkdir(parents=True, exist_ok=True)
        
    def banner(self):
        """Display the HIVE banner"""
        print("""
╔══════════════════════════════════════════════════════════════════╗
║  🐝 HIVE HACKER EDITION - Red Team Arsenal v2.0 🐝              ║
║                                                                  ║
║  "With great power comes great responsibility"                  ║
║                                                                  ║
║  ⚠️  AUTHORIZED TESTING ONLY - See LEGAL_NOTICE.txt             ║
╚══════════════════════════════════════════════════════════════════╝
        """)
    
    def menu(self):
        """Display main menu"""
        print("\n📋 MODULES AVAILABLE:\n")
        print("  ID  | Category              | Tools")
        print("  " + "-" * 50)
        
        for idx, (key, mod) in enumerate(MODULES.items(), 1):
            tool_count = len(mod['tools'])
            print(f"  {idx:2}  | {mod['name']:21} | {tool_count} tools")
        
        print("\n  99  | 🚀 Quick Launch         | Automated engagement")
        print("  00  | 📊 System Status        | Check environment")
        print("  q   | ❌ Quit                  | Exit HIVE")
    
    def check_environment(self):
        """Check if the environment is ready"""
        print("\n🔍 SYSTEM STATUS:\n")
        
        checks = {
            "Python 3": self._check_command("python3 --version"),
            "Git": self._check_command("git --version"),
            "cURL": self._check_command("curl --version"),
            "OpenSSL": self._check_command("openssl version"),
            "Tor": self._check_command("tor --version"),
            "Termux-API": self._check_file("/data/data/com.termux/files/usr/bin/termux-api-start"),
        }
        
        for name, status in checks.items():
            icon = "✓" if status else "✗"
            print(f"  {icon} {name}")
        
        ready = sum(checks.values())
        total = len(checks)
        print(f"\n  Status: {ready}/{total} components ready")
        
        if ready < total:
            print("\n  ⚠️  Run: ./00-INSTALL/setup.sh")
    
    def _check_command(self, cmd):
        """Check if a command exists"""
        try:
            result = subprocess.run(cmd.split(), 
                                  capture_output=True, 
                                  timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def _check_file(self, path):
        """Check if a file exists"""
        return Path(path).exists()
    
    def run_tool(self, module_key, tool_name, target=None):
        """Execute a specific tool"""
        module = MODULES.get(module_key)
        if not module:
            print(f"✗ Unknown module: {module_key}")
            return
        
        tool_path = self.base_path / module['path'] / f"{tool_name}.py"
        
        if not tool_path.exists():
            print(f"✗ Tool not found: {tool_path}")
            return
        
        print(f"\n🚀 Launching: {module['name']} > {tool_name}")
        print("-" * 50)
        
        cmd = ["python3", str(tool_path)]
        if target:
            cmd.append(target)
        
        try:
            subprocess.run(cmd, timeout=300)
        except subprocess.TimeoutExpired:
            print("⚠️ Tool timed out after 5 minutes")
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def quick_launch(self):
        """Run automated reconnaissance sequence"""
        print("\n🚀 QUICK LAUNCH - Automated Engagement")
        print("=" * 50)
        
        target = input("\nEnter authorized target (IP/Domain): ").strip()
        if not target:
            print("✗ No target specified")
            return
        
        print(f"\n⚠️  You are about to scan: {target}")
        confirm = input("Do you have explicit authorization? (yes/no): ").lower()
        if confirm != "yes":
            print("✗ Aborted - Authorization required")
            return
        
        # Run sequence
        sequence = [
            ("recon", "domain_enum", target),
            ("scanning", "port_scan", target),
            ("scanning", "web_scan", target),
        ]
        
        for module, tool, tgt in sequence:
            self.run_tool(module, tool, tgt)
            input("\nPress Enter to continue to next phase...")
    
    def interactive(self):
        """Main interactive loop"""
        self.banner()
        
        while True:
            self.menu()
            choice = input("\nSelect module [1-9, 99, 00, q]: ").strip().lower()
            
            if choice == 'q':
                print("\n👋 Goodbye, ethical hacker!")
                break
            
            elif choice == '00':
                self.check_environment()
            
            elif choice == '99':
                self.quick_launch()
            
            elif choice.isdigit() and 1 <= int(choice) <= 9:
                module_key = list(MODULES.keys())[int(choice) - 1]
                self.module_menu(module_key)
            
            else:
                print("\n✗ Invalid choice")
    
    def module_menu(self, module_key):
        """Display module-specific menu"""
        module = MODULES[module_key]
        
        while True:
            print(f"\n📁 {module['name']}")
            print("-" * 40)
            
            for idx, tool in enumerate(module['tools'], 1):
                print(f"  {idx}. {tool}")
            
            print(f"\n  0. Back to main menu")
            
            choice = input(f"\nSelect tool [0-{len(module['tools'])}]: ").strip()
            
            if choice == '0':
                break
            
            elif choice.isdigit() and 1 <= int(choice) <= len(module['tools']):
                tool_name = module['tools'][int(choice) - 1]
                target = input("Enter target (optional): ").strip() or None
                self.run_tool(module_key, tool_name, target)
            
            else:
                print("✗ Invalid choice")

def main():
    """Entry point"""
    hive = HiveHacker()
    
    # Check if running with arguments
    if len(sys.argv) > 1:
        # Command line mode
        if sys.argv[1] == "--status":
            hive.check_environment()
        elif sys.argv[1] == "--quick":
            hive.quick_launch()
        else:
            print(f"Usage: {sys.argv[0]} [--status|--quick]")
    else:
        # Interactive mode
        hive.interactive()

if __name__ == "__main__":
    main()
