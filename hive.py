#!/usr/bin/env python3
"""
HIVE LAUNCHER
Main entry point for the Hive System
Combines penetration testing tools with Swarm AI orchestration
"""

import sys
import os
from pathlib import Path

# Add core to path
sys.path.insert(0, str(Path(__file__).parent / 'core'))

BANNER = """
╔══════════════════════════════════════════════════════════════╗
║  🐝 HIVE SYSTEM v2.0 - Hacker Edition                          ║
║                                                                ║
║  AI-Powered Penetration Testing & Security Research Platform   ║
║  Multi-Agent Swarm with Verification Loops                      ║
╚══════════════════════════════════════════════════════════════╝
"""

MODULES = {
    '1': ('Core Swarm', 'core', [
        ('orchestrator', 'Swarm Orchestrator', 'python3 core/orchestrator.py'),
        ('assistant', 'Assistant Agent', 'python3 core/agents/assistant_agent.py'),
        ('architect', 'Architect Agent', 'python3 core/agents/architect_agent.py'),
    ]),
    '2': ('Reconnaissance', '10-RECON', [
        ('dns_enum', 'DNS Enumeration', '10-RECON/dns_enum.py'),
        ('subdomain_brute', 'Subdomain Brute', '10-RECON/subdomain_brute.py'),
        ('whois_enum', 'WHOIS Lookup', '10-RECON/whois_enum.py'),
        ('banner_grab', 'Banner Grabber', '10-RECON/banner_grab.py'),
    ]),
    '3': ('Scanning', '20-SCANNING', [
        ('port_scanner', 'Port Scanner', '20-SCANNING/port_scanner.py'),
        ('dir_bruter', 'Directory Brute', '20-SCANNING/dir_bruter.py'),
        ('web_scanner', 'Web Vulnerability Scanner', '20-SCANNING/web_scanner.py'),
        ('net_sniffer', 'Network Sniffer', '20-SCANNING/net_sniffer.py'),
    ]),
    '4': ('Exploitation', '30-EXPLOITATION', [
        ('payload_gen', 'Payload Generator', '30-EXPLOITATION/payload_generator.py'),
        ('ssh_brute', 'SSH Brute Force', '30-EXPLOITATION/ssh_brute.py'),
        ('sql_injector', 'SQL Injection Tester', '30-EXPLOITATION/sql_injector.py'),
        ('xss_tester', 'XSS Tester', '30-EXPLOITATION/xss_tester.py'),
        ('exploit_search', 'Exploit Database', '30-EXPLOITATION/exploit_search.py'),
    ]),
    '5': ('Post-Exploitation', '40-POST-EXPLOIT', [
        ('backdoor', 'Backdoor Manager', '40-POST-EXPLOIT/backdoor_manager.py'),
        ('privesc', 'Privilege Escalation Checker', '40-POST-EXPLOIT/privesc_checker.py'),
        ('cred_harvester', 'Credential Harvester', '40-POST-EXPLOIT/cred_harvester.py'),
    ]),
    '6': ('Reporting', '50-REPORTING', [
        ('report_gen', 'Report Generator', '50-REPORTING/report_generator.py'),
        ('forensic', 'Forensic Analyzer', '50-REPORTING/forensic_analyzer.py'),
        ('keylogger_det', 'Keylogger Detector', '50-REPORTING/keylogger_detector.py'),
    ]),
    '7': ('Cryptography', '70-CRYPTO', [
        ('hash_cracker', 'Hash Cracker', '70-CRYPTO/hash_cracker.py'),
        ('stego', 'Steganography Tool', '70-CRYPTO/stego_tool.py'),
        ('cipher_decoder', 'Cipher Decoder', '70-CRYPTO/cipher_decoder.py'),
    ]),
    '8': ('Anonymity', '60-ANONYMITY', [
        ('tor_mgr', 'Tor Manager', '60-ANONYMITY/tor_manager.py'),
    ]),
    '9': ('Wireless', '80-WIRELESS', [
        ('wifi_scan', 'WiFi Scanner', '80-WIRELESS/wifi_scanner.py'),
    ]),
}

def show_main_menu():
    """Show main menu"""
    print(BANNER)
    print("\n📚 Module Categories:")
    print("-" * 60)
    
    for key, (name, path, tools) in MODULES.items():
        print(f"\n  [{key}] {name}")
        print(f"      {len(tools)} tools available")
    
    print("\n" + "-" * 60)
    print("\n  [S] Swarm Mode - AI-Powered Automation")
    print("  [A] View All Tools")
    print("  [Q] Quit")

def show_module_tools(module_key):
    """Show tools in a module"""
    if module_key not in MODULES:
        print("✗ Invalid module")
        return
    
    name, path, tools = MODULES[module_key]
    
    print(f"\n🔧 {name} Tools:")
    print("-" * 60)
    
    for i, (tool_id, tool_name, tool_path) in enumerate(tools, 1):
        print(f"  [{i}] {tool_name}")
        print(f"      Path: {tool_path}")
    
    print("\n" + "-" * 60)
    print("  [0] Back to main menu")

def run_tool(module_key, tool_idx):
    """Run a specific tool"""
    if module_key not in MODULES:
        return
    
    name, path, tools = MODULES[module_key]
    
    if tool_idx < 1 or tool_idx > len(tools):
        return
    
    tool_id, tool_name, tool_path = tools[tool_idx - 1]
    full_path = Path(__file__).parent / tool_path
    
    if full_path.exists():
        print(f"\n🚀 Launching {tool_name}...")
        print("-" * 60)
        os.system(f"python3 {full_path}")
    else:
        print(f"✗ Tool not found: {tool_path}")

def swarm_mode():
    """Launch Swarm orchestration mode"""
    print("""
╔══════════════════════════════════════════════════════════════╗
║  🐝 SWARM MODE                                                ║
║                                                                ║
║  Multi-Agent AI Orchestration                                  ║
║  Delegation: User → Main AI → Swarm → Agent → Verify → Deliver ║
╚══════════════════════════════════════════════════════════════╝
    """)
    
    try:
        from core.orchestrator import SwarmOrchestrator
        
        orch = SwarmOrchestrator()
        status = orch.get_status_report()
        
        print("\n📊 Swarm Status:")
        for key, value in status.items():
            print(f"  {key}: {value}")
        
        print("\n✓ Swarm system ready")
        
        # Interactive task creation
        print("\n" + "-" * 60)
        task = input("Enter task for Swarm (or press Enter to skip): ").strip()
        
        if task:
            task_id = orch.delegate_task(task, "assistant_agent")
            print(f"\n✓ Task created: {task_id}")
            print(f"  Description: {task}")
            print(f"  Status: Delegated to Swarm")
            
    except Exception as e:
        print(f"✗ Swarm error: {e}")
        print("  Ensure core/orchestrator.py exists")

def show_all_tools():
    """Show all available tools"""
    print("\n📚 Complete Tool Arsenal:")
    print("=" * 60)
    
    total = 0
    for key, (name, path, tools) in MODULES.items():
        print(f"\n{name}:")
        for tool_id, tool_name, tool_path in tools:
            print(f"  • {tool_name}")
            total += 1
    
    print("\n" + "=" * 60)
    print(f"Total: {total} tools")

def main():
    """Main loop"""
    while True:
        show_main_menu()
        
        choice = input("\n➤ Select: ").strip().upper()
        
        if choice == 'Q':
            print("\n✓ Hive system shutting down...")
            break
        
        elif choice == 'A':
            show_all_tools()
        
        elif choice == 'S':
            swarm_mode()
        
        elif choice in MODULES:
            while True:
                show_module_tools(choice)
                tool_choice = input("\n➤ Select tool: ").strip()
                
                if tool_choice == '0':
                    break
                
                try:
                    tool_idx = int(tool_choice)
                    run_tool(choice, tool_idx)
                except ValueError:
                    print("✗ Invalid choice")
        
        else:
            print("✗ Invalid selection")
        
        input("\nPress Enter to continue...")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n✓ Hive system shutting down...")
