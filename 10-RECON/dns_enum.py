#!/usr/bin/env python3
"""
HIVE TOOL: dns_enum
DNS enumeration and subdomain discovery
"""

import sys
import socket
import dns.resolver
from concurrent.futures import ThreadPoolExecutor, as_completed

class DNSEnum:
    """DNS enumeration tool"""
    
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api',
        'dev', 'test', 'staging', 'demo', 'beta', 'app',
        'webmail', 'remote', 'vpn', 'ns1', 'ns2', 'dns',
        'mx', 'smtp', 'pop', 'imap', 'web', 'secure',
        'portal', 'intranet', 'extranet', 'owa', 'autodiscover'
    ]
    
    def __init__(self, domain, threads=20):
        self.domain = domain
        self.threads = threads
        self.found = []
        
    def resolve_subdomain(self, subdomain):
        """Try to resolve a subdomain"""
        try:
            target = f"{subdomain}.{self.domain}"
            answers = dns.resolver.resolve(target, 'A')
            ips = [str(rdata) for rdata in answers]
            return {'subdomain': target, 'ips': ips}
        except:
            return None
    
    def enumerate(self):
        """Enumerate subdomains"""
        print(f"🌐 DNS Enumeration: {self.domain}")
        print(f"   Threads: {self.threads}")
        print(f"   Wordlist: {len(self.COMMON_SUBDOMAINS)} common subdomains")
        print()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.resolve_subdomain, sub): sub 
                      for sub in self.COMMON_SUBDOMAINS}
            
            for future in as_completed(futures):
                result = future.result()
                if result:
                    self.found.append(result)
                    print(f"  ✓ {result['subdomain']} -> {', '.join(result['ips'])}")
        
        return self.found
    
    def get_dns_records(self):
        """Get common DNS records"""
        print(f"\n📋 DNS Records for {self.domain}:\n")
        
        record_types = ['A', 'AAAA', 'MX', 'NS', 'TXT', 'SOA', 'CNAME']
        
        for rtype in record_types:
            try:
                answers = dns.resolver.resolve(self.domain, rtype)
                print(f"  {rtype} Records:")
                for rdata in answers:
                    print(f"    - {rdata}")
            except:
                pass

def main():
    if len(sys.argv) < 2:
        print("Usage: dns_enum.py <domain>")
        print("Example: dns_enum.py example.com")
        sys.exit(1)
    
    domain = sys.argv[1]
    
    enum = DNSEnum(domain)
    enum.get_dns_records()
    
    print()
    results = enum.enumerate()
    
    print(f"\n📊 Summary: {len(results)} subdomains found")

if __name__ == "__main__":
    try:
        import dns.resolver
    except ImportError:
        print("⚠ Install dnspython: pip3 install dnspython")
        sys.exit(1)
    
    main()
