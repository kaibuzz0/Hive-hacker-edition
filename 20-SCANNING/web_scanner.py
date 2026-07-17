#!/usr/bin/env python3
"""
HIVE TOOL: web_scanner
Web application vulnerability scanner for authorized testing
"""

import sys
import requests
import urllib.parse
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse

class WebScanner:
    def __init__(self, target_url):
        self.target = target_url if target_url.startswith('http') else f'http://{target_url}'
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; HiveScanner/2.0; +https://github.com/kaibuzz0)'
        })
        self.findings = []
        
    def check_headers(self):
        """Check security headers"""
        print("\n🔒 Checking Security Headers...")
        
        try:
            resp = self.session.get(self.target, timeout=10)
            headers = resp.headers
            
            security_headers = {
                'X-Frame-Options': 'Clickjacking protection',
                'X-XSS-Protection': 'XSS filter',
                'Content-Security-Policy': 'CSP',
                'X-Content-Type-Options': 'MIME sniffing protection',
                'Strict-Transport-Security': 'HSTS',
                'Referrer-Policy': 'Referrer control'
            }
            
            for header, description in security_headers.items():
                if header in headers:
                    print(f"  ✓ {header}: {headers[header]}")
                else:
                    print(f"  ✗ {header}: MISSING ({description})")
                    self.findings.append(f"Missing header: {header}")
                    
        except Exception as e:
            print(f"  ✗ Error: {e}")
    
    def check_common_paths(self):
        """Check for common sensitive paths"""
        print("\n🗂️ Checking Common Paths...")
        
        paths = [
            '/.git/', '/.env', '/.htaccess', '/.htpasswd',
            '/admin', '/admin/', '/login', '/login/',
            '/wp-admin/', '/wp-login.php', '/phpmyadmin/',
            '/api/', '/swagger/', '/.svn/'
        ]
        
        for path in paths:
            try:
                url = urljoin(self.target, path)
                resp = self.session.get(url, timeout=5, allow_redirects=False)
                
                if resp.status_code == 200:
                    print(f"  ⚠ {path} - FOUND ({len(resp.content)} bytes)")
                    self.findings.append(f"Exposed path: {path}")
                elif resp.status_code in [301, 302]:
                    print(f"  • {path} - Redirects to {resp.headers.get('Location')}")
                    
            except:
                pass
    
    def check_sql_injection(self):
        """Basic SQL injection detection"""
        print("\n💉 Checking SQL Injection Points...")
        
        payloads = ["'", "''", "' OR '1'='1", "' OR 1=1--", "admin'--"]
        
        # Try on query parameters
        parsed = urlparse(self.target)
        if parsed.query:
            params = parsed.query.split('&')
            for param in params:
                if '=' in param:
                    key, value = param.split('=', 1)
                    for payload in payloads:
                        try:
                            test_url = self.target.replace(value, urllib.parse.quote(payload))
                            resp = self.session.get(test_url, timeout=5)
                            
                            errors = ['sql', 'mysql', 'sqlite', 'odbc', 'syntax', 'error']
                            if any(e in resp.text.lower() for e in errors):
                                print(f"  ⚠ Possible SQL injection in parameter: {key}")
                                self.findings.append(f"SQLi in param: {key}")
                                break
                        except:
                            pass
    
    def check_xss(self):
        """Check for XSS vulnerabilities"""
        print("\n🌐 Checking XSS Vulnerabilities...")
        
        xss_payload = "<script>alert('XSS')</script>"
        
        try:
            parsed = urlparse(self.target)
            if parsed.query:
                # Try reflected XSS
                test_url = f"{self.target}?test={urllib.parse.quote(xss_payload)}"
                resp = self.session.get(test_url, timeout=5)
                
                if xss_payload in resp.text:
                    print("  ⚠ Reflected XSS vulnerability detected")
                    self.findings.append("Reflected XSS")
        except:
            pass
    
    def crawl_links(self):
        """Crawl for links"""
        print("\n🕷️ Crawling Links...")
        
        try:
            resp = self.session.get(self.target, timeout=10)
            soup = BeautifulSoup(resp.text, 'html.parser')
            
            links = []
            for link in soup.find_all(['a', 'form']):
                href = link.get('href') or link.get('action')
                if href:
                    full_url = urljoin(self.target, href)
                    if full_url.startswith(self.target):
                        links.append(full_url)
            
            unique_links = list(set(links))[:20]  # Limit to 20
            print(f"  Found {len(unique_links)} internal links")
            
            for link in unique_links[:5]:
                print(f"    - {link}")
                
        except Exception as e:
            print(f"  ✗ Error crawling: {e}")
    
    def generate_report(self):
        """Generate findings report"""
        print("\n📊 SCAN SUMMARY")
        print("=" * 50)
        
        if self.findings:
            print(f"\n⚠ {len(self.findings)} security issues found:")
            for finding in self.findings:
                print(f"  • {finding}")
        else:
            print("\n✓ No immediate issues detected")
        
        print(f"\nTarget: {self.target}")
        print("\n💡 Next Steps:")
        print("  1. Verify findings manually")
        print("  2. Check for false positives")
        print("  3. Document in report")
        print("  4. Report responsibly")

def main():
    if len(sys.argv) < 2:
        print("Usage: web_scanner.py <url>")
        print("Example: web_scanner.py http://example.com")
        sys.exit(1)
    
    target = sys.argv[1]
    
    print(f"🌐 HIVE Web Scanner")
    print(f"   Target: {target}")
    
    scanner = WebScanner(target)
    
    scanner.check_headers()
    scanner.check_common_paths()
    scanner.check_sql_injection()
    scanner.check_xss()
    scanner.crawl_links()
    scanner.generate_report()

if __name__ == "__main__":
    main()
