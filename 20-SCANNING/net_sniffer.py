#!/usr/bin/env python3
"""
HIVE TOOL: net_sniffer
Basic network packet sniffer for analysis
"""

import sys
import socket
import struct
from datetime import datetime

class PacketSniffer:
    """Simple network packet sniffer"""
    
    def __init__(self, interface=None):
        self.interface = interface
        self.packets = []
        
    def parse_ethernet(self, data):
        """Parse Ethernet header"""
        dest_mac = data[0:6]
        src_mac = data[6:12]
        proto = struct.unpack('!H', data[12:14])[0]
        return {
            'dest_mac': ':'.join(f'{b:02x}' for b in dest_mac),
            'src_mac': ':'.join(f'{b:02x}' for b in src_mac),
            'protocol': proto,
            'payload': data[14:]
        }
    
    def parse_ip(self, data):
        """Parse IP header"""
        version_header = data[0]
        version = version_header >> 4
        header_len = (version_header & 0x0f) * 4
        
        ttl = data[8]
        protocol = data[9]
        src_ip = '.'.join(str(b) for b in data[12:16])
        dest_ip = '.'.join(str(b) for b in data[16:20])
        
        return {
            'version': version,
            'header_len': header_len,
            'ttl': ttl,
            'protocol': protocol,
            'src_ip': src_ip,
            'dest_ip': dest_ip,
            'payload': data[header_len:]
        }
    
    def parse_tcp(self, data):
        """Parse TCP header"""
        src_port = struct.unpack('!H', data[0:2])[0]
        dest_port = struct.unpack('!H', data[2:4])[0]
        seq = struct.unpack('!I', data[4:8])[0]
        ack = struct.unpack('!I', data[8:12])[0]
        
        return {
            'src_port': src_port,
            'dest_port': dest_port,
            'seq': seq,
            'ack': ack,
            'payload': data[20:]
        }
    
    def sniff(self, count=10):
        """Sniff packets"""
        print("🕸️ HIVE Network Sniffer")
        print("   Capturing packets...")
        print("-" * 60)
        
        try:
            # Create raw socket
            sock = socket.socket(socket.AF_INET, socket.SOCK_RAW, socket.IPPROTO_TCP)
            sock.settimeout(10)
            
            captured = 0
            while captured < count:
                try:
                    raw_data, addr = sock.recvfrom(65535)
                    captured += 1
                    
                    # Parse IP
                    ip_header = self.parse_ip(raw_data)
                    
                    # Parse TCP if applicable
                    if ip_header['protocol'] == 6:  # TCP
                        tcp_header = self.parse_tcp(ip_header['payload'])
                        
                        print(f"\n[Packet {captured}] {datetime.now().strftime('%H:%M:%S')}")
                        print(f"  {ip_header['src_ip']}:{tcp_header['src_port']} -> "
                              f"{ip_header['dest_ip']}:{tcp_header['dest_port']}")
                        print(f"  Protocol: TCP | TTL: {ip_header['ttl']}")
                        
                        if len(tcp_header['payload']) > 0:
                            try:
                                payload = tcp_header['payload'].decode('utf-8', errors='ignore')
                                if payload.strip():
                                    print(f"  Payload: {payload[:100]}...")
                            except:
                                pass
                    else:
                        print(f"[Packet {captured}] {ip_header['src_ip']} -> "
                              f"{ip_header['dest_ip']} (Protocol: {ip_header['protocol']})")
                
                except socket.timeout:
                    print("Timeout - no packets captured")
                    break
                except KeyboardInterrupt:
                    print("\nCapture stopped")
                    break
            
            sock.close()
            print(f"\n✓ Captured {captured} packets")
            
        except PermissionError:
            print("✗ Permission denied - run as root for raw sockets")
        except Exception as e:
            print(f"✗ Error: {e}")

def main():
    if len(sys.argv) > 1 and sys.argv[1] == '-h':
        print("Usage: net_sniffer.py [count]")
        print("Example: net_sniffer.py 20")
        sys.exit(0)
    
    count = int(sys.argv[1]) if len(sys.argv) > 1 else 10
    
    sniffer = PacketSniffer()
    sniffer.sniff(count)

if __name__ == "__main__":
    main()
