#!/usr/bin/env python3
"""
HIVE TOOL: dir_bruter
Directory and file brute forcer for web servers
"""

import sys
import requests
import threading
from queue import Queue

class DirBruter:
    """Directory brute forcer"""
    
    COMMON_PATHS = [
        'admin', 'admin/', 'login', 'login/', 'dashboard', 'dashboard/',
        'api', 'api/', 'config', 'config/', 'backup', 'backup/',
        '.env', '.git/', '.svn/', '.htaccess', '.htpasswd',
        'robots.txt', 'sitemap.xml', 'phpmyadmin/', 'wp-admin/',
        'wp-login.php', 'administrator/', 'panel/', 'cp/',
        'phpinfo.php', 'info.php', 'test/', 'tmp/', 'temp/',
        'upload/', 'uploads/', 'files/', 'assets/', 'static/',
        'js/', 'css/', 'images/', 'img/', 'media/',
        'README', 'readme.txt', 'INSTALL', 'LICENSE',
        'api/v1/', 'api/v2/', 'swagger/', 'docs/',
        'console/', 'status/', 'health/', 'metrics/'
    ]
    
    def __init__(self, url, wordlist=None, threads=30, extensions=None):
        self.url = url if url.startswith('http') else f'http://{url}'
        self.wordlist = wordlist
        self.threads = threads
        self.extensions = extensions or ['', '.php', '.html', '.txt', '.bak', '.zip', '.tar.gz']
        self.queue = Queue()
        self.found = []
        self.lock = threading.Lock()
        self.total = 0
        
    def check_path(self, path):
        """Check if path exists"""
        try:
            full_url = f"{self.url}/{path}"
            resp = requests.get(full_url, timeout=5, allow_redirects=False)
            
            if resp.status_code in [200, 201, 204, 301, 302, 401, 403, 405]:
                with self.lock:
                    self.found.append({'path': path, 'status': resp.status_code, 'size': len(resp.content)})
                    print(f"  ✓ /{path} - {resp.status_code} ({len(resp.content)} bytes)")
                return True
        except:
            pass
        return False
    
    def worker(self):
        """Worker thread"""
        while True:
            path = self.queue.get()
            if path is None:
                break
            self.check_path(path)
            self.queue.task_done()
    
    def run(self):
        """Run brute force"""
        print(f"🕸️ Directory Brute Force: {self.url}")
        print(f"   Threads: {self.threads}")
        
        # Load wordlist
        if self.wordlist:
            with open(self.wordlist) as f:
                paths = [line.strip() for line in f if line.strip()]
        else:
            paths = self.COMMON_PATHS
        
        # Add extensions
        all_paths = []
        for path in paths:
            for ext in self.extensions:
                all_paths.append(f"{path}{ext}")
        
        self.total = len(all_paths)
        print(f"   Paths to check: {self.total}")
        print()
        print("Found:")
        print("-" * 60)
        
        # Populate queue
        for path in all_paths:
            self.queue.put(path)
        
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
        
        print("-" * 60)
        print(f"✓ Found: {len(self.found)} paths")
        return self.found

def main():
    if len(sys.argv) < 2:
        print("Usage: dir_bruter.py <url> [wordlist]")
        print("Example: dir_bruter.py http://example.com")
        sys.exit(1)
    
    url = sys.argv[1]
    wordlist = sys.argv[2] if len(sys.argv) > 2 else None
    
    brute = DirBruter(url, wordlist)
    brute.run()

if __name__ == "__main__":
    main()
