#!/usr/bin/env python3
"""
HIVE TOOL: port_scanner
Fast multi-threaded port scanner for authorized penetration testing
"""

import sys
import socket
import threading
from queue import Queue
from datetime import datetime

# Common ports and services
COMMON_PORTS = {
    21: "FTP", 22: "SSH", 23: "Telnet", 25: "SMTP", 53: "DNS",
    80: "HTTP", 110: "POP3", 143: "IMAP", 443: "HTTPS", 445: "SMB",
    3306: "MySQL", 3389: "RDP", 5432: "PostgreSQL", 5900: "VNC",
    6379: "Redis", 8080: "HTTP-Proxy", 8443: "HTTPS-Alt", 9200: "Elasticsearch"
}

class PortScanner:
    def __init__(self, target, ports=None, threads=100):
        self.target = target
        self.ports = ports or list(COMMON_PORTS.keys())
        self.threads = threads
        self.queue = Queue()
        self.results = []
        self.lock = threading.Lock()
        
    def scan_port(self, port):
        """Scan a single port"""
        try:
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(1)
            result = sock.connect_ex((self.target, port))
            
            if result == 0:
                service = COMMON_PORTS.get(port, "Unknown")
                with self.lock:
                    self.results.append({
                        'port': port,
                        'state': 'OPEN',
                        'service': service
                    })
                    print(f"  ✓ Port {port}/tcp OPEN ({service})")
            
            sock.close()
        except:
            pass
    
    def worker(self):
        """Worker thread"""
        while True:
            port = self.queue.get()
            if port is None:
                break
            self.scan_port(port)
            self.queue.task_done()
    
    def run(self):
        """Run the port scan"""
        print(f"\n🔍 Scanning {self.target}")
        print(f"   Ports: {len(self.ports)} common ports")
        print(f"   Threads: {self.threads}")
        print(f"   Started: {datetime.now().strftime('%H:%M:%S')}")
        print()
        
        # Resolve hostname if needed
        try:
            target_ip = socket.gethostbyname(self.target)
            if target_ip != self.target:
                print(f"   Resolved: {self.target} -> {target_ip}")
                self.target = target_ip
        except:
            print(f"   ⚠ Could not resolve {self.target}")
            return []
        
        # Populate queue
        for port in self.ports:
            self.queue.put(port)
        
        # Start threads
        thread_list = []
        for _ in range(min(self.threads, len(self.ports))):
            t = threading.Thread(target=self.worker)
            t.start()
            thread_list.append(t)
        
        # Wait for completion
        self.queue.join()
        
        # Stop threads
        for _ in thread_list:
            self.queue.put(None)
        for t in thread_list:
            t.join()
        
        print(f"\n✓ Scan complete: {len(self.results)} open ports found")
        return self.results

def main():
    if len(sys.argv) < 2:
        print("Usage: port_scanner.py <target> [port-range]")
        print("Example: port_scanner.py 192.168.1.1")
        print("Example: port_scanner.py example.com 1-1000")
        sys.exit(1)
    
    target = sys.argv[1]
    
    ports = None
    if len(sys.argv) > 2:
        if '-' in sys.argv[2]:
            start, end = map(int, sys.argv[2].split('-'))
            ports = list(range(start, end + 1))
        else:
            ports = [int(p) for p in sys.argv[2].split(',')]
    
    scanner = PortScanner(target, ports)
    results = scanner.run()
    
    # Summary
    if results:
        print("\n📊 RESULTS:")
        for r in sorted(results, key=lambda x: x['port']):
            print(f"  {r['port']}/tcp  {r['state']:6}  {r['service']}")
    else:
        print("\n📊 No open ports found")

if __name__ == "__main__":
    main()
