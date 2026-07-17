#!/usr/bin/env python3
"""
HIVE TOOL: wifi_scanner
WiFi network scanner for Android/Termux
"""

import sys
import subprocess

class WiFiScanner:
    """WiFi network scanner"""
    
    def __init__(self):
        self.networks = []
        
    def scan(self):
        """Scan for WiFi networks"""
        print("📡 WiFi Scanner")
        print("-" * 60)
        
        # Note: Requires root and proper WiFi interface on Android
        try:
            # Try to use termux-wifi-scaninfo if available
            result = subprocess.run(
                ['termux-wifi-scaninfo'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(result.stdout)
            else:
                print("⚠ termux-wifi-scaninfo not available")
                print()
                print("Alternative: Use 'iw' command if available:")
                print("  iw dev wlan0 scan")
                print()
                print("Or use Android WiFi settings")
                
        except FileNotFoundError:
            print("⚠ termux-api not installed")
            print()
            print("Install with: pkg install termux-api")
            print("Then: termux-wifi-scaninfo")
            
        except Exception as e:
            print(f"✗ Error: {e}")
    
    def show_interfaces(self):
        """Show network interfaces"""
        print("\n🌐 Network Interfaces:")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                ['ifconfig'] if sys.platform != 'win32' else ['ipconfig'],
                capture_output=True,
                text=True
            )
            
            print(result.stdout[:2000])
            
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    print("""
╔══════════════════════════════════════════╗
║  📡 HIVE WiFi Scanner                   ║
║  Requires Termux API on Android         ║
╚══════════════════════════════════════════╝
    """)
    
    scanner = WiFiScanner()
    
    print("\nOptions:")
    print("  1. Scan WiFi networks")
    print("  2. Show interfaces")
    print("  3. Exit")
    
    choice = input("\nSelect: ").strip()
    
    if choice == '1':
        scanner.scan()
    elif choice == '2':
        scanner.show_interfaces()
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
