#!/usr/bin/env python3
"""
HIVE TOOL: keylogger_detector
Detect potential keyloggers and suspicious processes
"""

import sys
import subprocess
import os

class KeyloggerDetector:
    """Keylogger detection tool"""
    
    SUSPICIOUS_PATTERNS = [
        'keylog', 'keylogger', 'input', 'keyboard', 'hook',
        'sniff', 'capture', 'log', 'spy', 'record'
    ]
    
    def __init__(self):
        self.suspicious = []
        
    def check_processes(self):
        """Check running processes"""
        print("🔍 Checking Running Processes...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                ['ps', 'aux'],
                capture_output=True,
                text=True
            )
            
            lines = result.stdout.split('\n')
            
            for line in lines[1:]:  # Skip header
                for pattern in self.SUSPICIOUS_PATTERNS:
                    if pattern.lower() in line.lower():
                        parts = line.split()
                        if len(parts) > 10:
                            pid = parts[1]
                            cmd = ' '.join(parts[10:])
                            print(f"  ⚠ Suspicious: PID {pid} - {cmd[:50]}")
                            self.suspicious.append({'pid': pid, 'cmd': cmd})
                            break
            
            if not self.suspicious:
                print("  ✓ No obvious keyloggers detected")
            else:
                print(f"\n  Found {len(self.suspicious)} suspicious processes")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def check_devices(self):
        """Check input devices"""
        print("\n🖱️ Checking Input Devices...")
        print("-" * 60)
        
        try:
            if os.path.exists('/dev/input'):
                devices = os.listdir('/dev/input')
                print(f"  Input devices found: {len(devices)}")
                for dev in devices[:10]:
                    print(f"    - {dev}")
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def check_network(self):
        """Check network connections"""
        print("\n🌐 Checking Network Connections...")
        print("-" * 60)
        
        try:
            result = subprocess.run(
                ['netstat', '-tlnp'] if sys.platform != 'darwin' else ['netstat', '-an'],
                capture_output=True,
                text=True
            )
            
            # Look for suspicious outbound connections
            lines = result.stdout.split('\n')
            suspicious_ports = [4444, 5555, 6666, 7777, 8888, 9999]
            
            found = 0
            for line in lines:
                for port in suspicious_ports:
                    if f':{port}' in line:
                        print(f"  ⚠ Suspicious port {port}: {line[:60]}")
                        found += 1
            
            if found == 0:
                print("  ✓ No suspicious network connections")
            else:
                print(f"  Found {found} suspicious connections")
                
        except:
            print("  ℹ netstat not available")
    
    def run_check(self):
        """Run full keylogger detection"""
        print("""
╔══════════════════════════════════════════╗
║  🔍 HIVE Keylogger Detector             ║
║  Scan for suspicious input monitoring    ║
╚══════════════════════════════════════════╝
        """)
        
        self.check_processes()
        self.check_devices()
        self.check_network()
        
        print("\n" + "=" * 60)
        if self.suspicious:
            print(f"⚠ {len(self.suspicious)} suspicious items found")
            print("\nRecommendations:")
            print("  1. Investigate flagged processes")
            print("  2. Check for unknown software")
            print("  3. Review recent installations")
        else:
            print("✓ No keyloggers detected")

def main():
    detector = KeyloggerDetector()
    detector.run_check()

if __name__ == "__main__":
    main()
