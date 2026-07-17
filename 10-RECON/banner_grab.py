#!/usr/bin/env python3
"""
HIVE TOOL: banner_grab
Service banner grabber for reconnaissance
"""

import sys
import socket

class BannerGrab:
    """Service banner grabber"""
    
    def __init__(self, target, port, timeout=5):
        self.target = target
        self.port = port
        self.timeout = timeout
        
    def grab(self):
        """Grab banner from service"""
        print(f"🎯 Banner Grab: {self.target}:{self.port}")
        print()
        
        sock = None
        try:
            # Create socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(self.timeout)
            
            # Connect
            result = sock.connect_ex((self.target, self.port))
            
            if result != 0:
                print(f"✗ Connection failed (port closed/filtered)")
                return None
            
            # Try to receive banner
            try:
                banner = sock.recv(1024)
                if banner:
                    try:
                        decoded = banner.decode('utf-8', errors='ignore').strip()
                        print(f"✓ Banner received:")
                        print(f"  {decoded}")
                        return decoded
                    except:
                        print(f"✓ Raw bytes received ({len(banner)} bytes)")
                        return banner.hex()
                else:
                    print(f"⚠ Connected but no banner received")
                    return None
                    
            except socket.timeout:
                print(f"⚠ Connection timeout waiting for banner")
                return None
                
        except Exception as e:
            print(f"✗ Error: {e}")
            return None
        finally:
            if sock:
                sock.close()

def main():
    if len(sys.argv) < 3:
        print("Usage: banner_grab.py <target> <port>")
        print("Example: banner_grab.py example.com 80")
        print("Example: banner_grab.py 192.168.1.1 22")
        sys.exit(1)
    
    target = sys.argv[1]
    port = int(sys.argv[2])
    
    grabber = BannerGrab(target, port)
    grabber.grab()

if __name__ == "__main__":
    main()
