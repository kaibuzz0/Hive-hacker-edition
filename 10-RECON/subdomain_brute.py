#!/usr/bin/env python3
"""
HIVE TOOL: subdomain_brute
Brute force subdomains using wordlist
"""

import sys
import socket
import threading
from queue import Queue

class SubdomainBrute:
    """Subdomain brute forcer"""
    
    COMMON_SUBDOMAINS = [
        'www', 'mail', 'ftp', 'admin', 'blog', 'shop', 'api', 'dev', 'test',
        'staging', 'demo', 'beta', 'app', 'webmail', 'remote', 'vpn', 'ns1',
        'ns2', 'dns', 'mx', 'smtp', 'pop', 'imap', 'web', 'secure', 'portal',
        'intranet', 'extranet', 'owa', 'autodiscover', 'cloud', 'cdn', 'img',
        'images', 'static', 'assets', 'media', 'video', 'download', 'files',
        'support', 'help', 'docs', 'wiki', 'kb', 'status', 'monitor', 'git',
        'svn', 'cvs', 'jenkins', 'ci', 'build', 'deploy', 'docker', 'kube',
        'db', 'database', 'mysql', 'postgres', 'mongo', 'redis', 'elastic',
        'search', 'solr', 'backup', 'archive', 'old', 'new', 'v1', 'v2', 'v3'
    ]
    
    def __init__(self, domain, wordlist=None, threads=50):
        self.domain = domain
        self.wordlist = wordlist
        self.threads = threads
        self.queue = Queue()
        self.found = []
        self.lock = threading.Lock()
        self.total = 0
        self.checked = 0
        
    def check_subdomain(self, subdomain):
        """Check if subdomain exists"""
        try:
            target = f"{subdomain}.{self.domain}"
            socket.gethostbyname(target)
            with self.lock:
                self.found.append(target)
                print(f"  ✓ {target}")
            return True
        except:
            return False
        finally:
            with self.lock:
                self.checked += 1
                if self.checked % 10 == 0:
                    print(f"    Progress: {self.checked}/{self.total}", end='\r')
    
    def worker(self):
        """Worker thread"""
        while True:
            subdomain = self.queue.get()
            if subdomain is None:
                break
            self.check_subdomain(subdomain)
            self.queue.task_done()
    
    def run(self):
        """Run brute force"""
        print(f"🌐 Subdomain Brute Force: {self.domain}")
        print(f"   Threads: {self.threads}")
        
        # Load wordlist
        if self.wordlist:
            with open(self.wordlist) as f:
                subdomains = [line.strip() for line in f if line.strip()]
        else:
            subdomains = self.COMMON_SUBDOMAINS
        
        self.total = len(subdomains)
        print(f"   Wordlist: {self.total} entries")
        print()
        print("Found subdomains:")
        print("-" * 50)
        
        # Populate queue
        for sub in subdomains:
            self.queue.put(sub)
        
        # Start threads
        thread_list = []
        for _ in range(min(self.threads, self.total)):
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
        
        print()
        print("-" * 50)
        print(f"✓ Found: {len(self.found)} subdomains")
        return self.found

def main():
    if len(sys.argv) < 2:
        print("Usage: subdomain_brute.py <domain> [wordlist]")
        print("Example: subdomain_brute.py example.com")
        print("Example: subdomain_brute.py example.com /path/to/wordlist.txt")
        sys.exit(1)
    
    domain = sys.argv[1]
    wordlist = sys.argv[2] if len(sys.argv) > 2 else None
    
    brute = SubdomainBrute(domain, wordlist)
    brute.run()

if __name__ == "__main__":
    main()
