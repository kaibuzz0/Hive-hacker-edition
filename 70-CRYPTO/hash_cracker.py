#!/usr/bin/env python3
"""
HIVE TOOL: hash_cracker
Fast hash cracker supporting multiple algorithms
For authorized penetration testing and CTFs
"""

import sys
import hashlib
import itertools
import string
from pathlib import Path
from concurrent.futures import ThreadPoolExecutor, as_completed

class HashCracker:
    """Multi-threaded hash cracker"""
    
    ALGORITHMS = {
        'md5': hashlib.md5,
        'sha1': hashlib.sha1,
        'sha256': hashlib.sha256,
        'sha512': hashlib.sha512,
    }
    
    def __init__(self, target_hash, algorithm='md5', wordlist=None, threads=10):
        self.target = target_hash.lower().strip()
        self.algo = algorithm.lower()
        self.wordlist = wordlist
        self.threads = threads
        self.found = False
        self.result = None
        
    def crack_single(self, word):
        """Hash a single word and compare"""
        if self.found:
            return None
            
        word = word.strip()
        if not word:
            return None
            
        hasher = self.ALGORITHMS[self.algo]()
        hasher.update(word.encode())
        
        if hasher.hexdigest().lower() == self.target:
            self.found = True
            return word
        return None
    
    def crack_wordlist(self):
        """Crack using wordlist"""
        if not self.wordlist or not Path(self.wordlist).exists():
            return None
            
        print(f"🚀 Loading wordlist: {self.wordlist}")
        words = Path(self.wordlist).read_text().split('\n')
        total = len(words)
        print(f"   {total:,} words loaded")
        print(f"   Threads: {self.threads}")
        print(f"   Algorithm: {self.algo.upper()}")
        print()
        
        with ThreadPoolExecutor(max_workers=self.threads) as executor:
            futures = {executor.submit(self.crack_single, word): word for word in words[:100000]}
            
            for i, future in enumerate(as_completed(futures), 1):
                if i % 10000 == 0:
                    print(f"   Progress: {i:,}/{total:,} words...")
                
                result = future.result()
                if result:
                    return result
        
        return None
    
    def brute_force(self, min_len=1, max_len=4, charset=None):
        """Brute force attack"""
        charset = charset or string.ascii_lowercase + string.digits
        
        print(f"🔨 Brute force attack")
        print(f"   Length: {min_len}-{max_len}")
        print(f"   Charset: {charset}")
        print(f"   Estimated combinations: {sum(len(charset) ** i for i in range(min_len, max_len+1)):,}")
        print()
        
        for length in range(min_len, max_len + 1):
            print(f"   Trying length {length}...")
            
            for attempt in itertools.product(charset, repeat=length):
                if self.found:
                    return None
                
                word = ''.join(attempt)
                result = self.crack_single(word)
                if result:
                    return result
        
        return None

def main():
    print("""
╔══════════════════════════════════════════╗
║  🔓 HIVE Hash Cracker                     ║
║  Multi-algorithm password recovery        ║
╚══════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        print("Usage: hash_cracker.py <hash> [algorithm] [wordlist]")
        print("Example: hash_cracker.py 5f4dcc3b5aa765d61d8327deb882cf99 md5 /usr/share/wordlists/rockyou.txt")
        print()
        print("Supported algorithms:", ', '.join(HashCracker.ALGORITHMS.keys()))
        sys.exit(1)
    
    target_hash = sys.argv[1]
    algorithm = sys.argv[2] if len(sys.argv) > 2 else 'md5'
    wordlist = sys.argv[3] if len(sys.argv) > 3 else None
    
    if algorithm not in HashCracker.ALGORITHMS:
        print(f"✗ Unsupported algorithm: {algorithm}")
        print(f"Supported: {', '.join(HashCracker.ALGORITHMS.keys())}")
        sys.exit(1)
    
    cracker = HashCracker(target_hash, algorithm, wordlist)
    
    # Try wordlist first
    if wordlist:
        result = cracker.crack_wordlist()
        if result:
            print(f"\n✓ PASSWORD FOUND: {result}")
            return
    
    # Try brute force for short passwords
    print("\n⚠ Wordlist exhausted, trying brute force...")
    result = cracker.brute_force(min_len=1, max_len=4)
    
    if result:
        print(f"\n✓ PASSWORD FOUND: {result}")
    else:
        print("\n✗ Password not found")

if __name__ == "__main__":
    main()
