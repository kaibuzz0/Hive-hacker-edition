#!/usr/bin/env python3
"""
HIVE TOOL: tor_manager
Tor anonymity network manager
"""

import sys
import subprocess
import socket

class TorManager:
    """Tor proxy manager"""
    
    def __init__(self):
        self.proxy_host = '127.0.0.1'
        self.proxy_port = 9050
        
    def check_tor(self):
        """Check if Tor is running"""
        print("🧅 Checking Tor Status...")
        print("-" * 50)
        
        try:
            # Check if Tor process is running
            result = subprocess.run(
                ['pgrep', '-x', 'tor'],
                capture_output=True
            )
            
            if result.returncode == 0:
                print("  ✓ Tor process is running")
                
                # Test SOCKS5 proxy
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.settimeout(5)
                result = sock.connect_ex((self.proxy_host, self.proxy_port))
                sock.close()
                
                if result == 0:
                    print(f"  ✓ SOCKS5 proxy available at {self.proxy_host}:{self.proxy_port}")
                    return True
                else:
                    print(f"  ⚠ Tor running but SOCKS5 proxy not responding")
                    return False
            else:
                print("  ✗ Tor is not running")
                print("  Start with: tor &")
                return False
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
            return False
    
    def show_commands(self):
        """Show useful Tor commands"""
        print("\n📋 Tor Management Commands:")
        print("-" * 50)
        print("  Start Tor:     tor &")
        print("  Stop Tor:      pkill tor")
        print("  Restart Tor:   pkill -HUP tor")
        print("  Check IP:      curl --socks5 127.0.0.1:9050 https://check.torproject.org")
        print("  New identity:  pkill -HUP tor")
        print()
        print("  Proxy settings:")
        print("    HTTP_PROXY=socks5://127.0.0.1:9050")
        print("    HTTPS_PROXY=socks5://127.0.0.1:9050")
    
    def test_connection(self):
        """Test Tor connection"""
        print("\n🌐 Testing Tor Connection...")
        print("-" * 50)
        
        try:
            result = subprocess.run(
                ['curl', '--socks5', f'{self.proxy_host}:{self.proxy_port}', 
                 '-s', 'https://check.torproject.org'],
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if 'Congratulations' in result.stdout:
                print("  ✓ Tor is working!")
                print("  Your connection is anonymized")
            else:
                print("  ⚠ Could not verify Tor connection")
                print("  Response:", result.stdout[:200])
                
        except FileNotFoundError:
            print("  ✗ curl not installed")
        except Exception as e:
            print(f"  ✗ Test failed: {e}")

def main():
    print("""
╔══════════════════════════════════════════╗
║  🧅 HIVE Tor Manager                    ║
║  Anonymity network management            ║
╚══════════════════════════════════════════╝
    """)
    
    manager = TorManager()
    
    print("\nOptions:")
    print("  1. Check Tor status")
    print("  2. Test connection")
    print("  3. Show commands")
    print("  4. Exit")
    
    choice = input("\nSelect: ").strip()
    
    if choice == '1':
        manager.check_tor()
    elif choice == '2':
        manager.test_connection()
    elif choice == '3':
        manager.show_commands()
    else:
        print("Goodbye!")

if __name__ == "__main__":
    main()
