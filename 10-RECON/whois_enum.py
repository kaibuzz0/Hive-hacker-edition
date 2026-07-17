#!/usr/bin/env python3
"""
HIVE TOOL: whois_enum
WHOIS enumeration and domain analysis
"""

import sys
import socket
import subprocess

class WhoisEnum:
    """WHOIS enumeration tool"""
    
    def __init__(self, domain):
        self.domain = domain
        
    def get_whois(self):
        """Get WHOIS data"""
        print(f"🌐 WHOIS Lookup: {self.domain}")
        print()
        
        try:
            # Try whois command first
            result = subprocess.run(
                ['whois', self.domain],
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return result.stdout
            else:
                return "WHOIS command not available or domain not found"
                
        except FileNotFoundError:
            return "whois command not installed"
        except Exception as e:
            return f"Error: {e}"
    
    def get_dns_records(self):
        """Get basic DNS records"""
        print(f"📋 DNS Records for {self.domain}:")
        print("-" * 50)
        
        # A record
        try:
            ip = socket.gethostbyname(self.domain)
            print(f"  A Record:    {ip}")
        except:
            print(f"  A Record:    Not found")
        
        # Try MX and NS by simple socket lookup
        try:
            # Get hostname info
            info = socket.getaddrinfo(self.domain, None)
            ips = set(str(x[4][0]) for x in info)
            print(f"  IPs found:   {', '.join(list(ips)[:5])}")
        except:
            pass
        
        print()
    
    def analyze(self):
        """Run full analysis"""
        self.get_dns_records()
        
        whois_data = self.get_whois()
        print("WHOIS Data:")
        print("-" * 50)
        
        # Parse key fields
        key_fields = [
            'Registrar:', 'Creation Date:', 'Expiration Date:',
            'Name Server:', 'Registrant', 'Admin', 'Tech'
        ]
        
        for line in whois_data.split('\n'):
            for field in key_fields:
                if field in line:
                    print(f"  {line.strip()}")
        
        print("-" * 50)

def main():
    if len(sys.argv) < 2:
        print("Usage: whois_enum.py <domain>")
        print("Example: whois_enum.py example.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    enum = WhoisEnum(domain)
    enum.analyze()

if __name__ == "__main__":
    main()
