#!/usr/bin/env python3
"""
HIVE TOOL: forensic_analyzer
Basic forensic analysis tool for file investigation
"""

import sys
import os
import hashlib
from pathlib import Path
from datetime import datetime

class ForensicAnalyzer:
    """File forensic analyzer"""
    
    def __init__(self, filepath):
        self.filepath = Path(filepath)
        self.metadata = {}
        
    def analyze(self):
        """Analyze file"""
        print(f"🔬 Forensic Analysis: {self.filepath}")
        print("-" * 60)
        
        if not self.filepath.exists():
            print(f"✗ File not found: {self.filepath}")
            return
        
        # Basic info
        stat = self.filepath.stat()
        self.metadata = {
            'size': stat.st_size,
            'created': datetime.fromtimestamp(stat.st_ctime),
            'modified': datetime.fromtimestamp(stat.st_mtime),
            'accessed': datetime.fromtimestamp(stat.st_atime),
        }
        
        print(f"📄 File: {self.filepath.name}")
        print(f"   Path: {self.filepath.absolute()}")
        print(f"   Size: {self.metadata['size']:,} bytes")
        print(f"   Created: {self.metadata['created']}")
        print(f"   Modified: {self.metadata['modified']}")
        print(f"   Accessed: {self.metadata['accessed']}")
        
        # Calculate hashes
        self.calculate_hashes()
        
        # File type detection (basic)
        self.detect_type()
    
    def calculate_hashes(self):
        """Calculate file hashes"""
        print("\n🔐 File Hashes:")
        print("-" * 40)
        
        hashes = {'md5': hashlib.md5(), 'sha1': hashlib.sha1(), 'sha256': hashlib.sha256()}
        
        try:
            with open(self.filepath, 'rb') as f:
                while chunk := f.read(8192):
                    for h in hashes.values():
                        h.update(chunk)
            
            for name, h in hashes.items():
                print(f"  {name.upper():8}: {h.hexdigest()}")
                
        except Exception as e:
            print(f"  ✗ Error calculating hashes: {e}")
    
    def detect_type(self):
        """Detect file type from magic bytes"""
        print("\n📋 File Type Detection:")
        print("-" * 40)
        
        magic_bytes = {
            b'\\x89PNG': 'PNG Image',
            b'\\xff\\xd8\\xff': 'JPEG Image',
            b'%PDF': 'PDF Document',
            b'PK\\x03\\x04': 'ZIP Archive',
            b'\\x1f\\x8b': 'GZIP Archive',
            b'\\x7fELF': 'ELF Executable',
            b'MZ': 'Windows Executable',
        }
        
        try:
            with open(self.filepath, 'rb') as f:
                header = f.read(8)
                
            for magic, ftype in magic_bytes.items():
                if header.startswith(magic):
                    print(f"  ✓ Detected: {ftype}")
                    return
            
            # Try text detection
            try:
                with open(self.filepath, 'r') as f:
                    f.read(1024)
                print(f"  ✓ Detected: Text File")
            except:
                print(f"  ? Unknown binary format")
                print(f"  Header (hex): {header.hex()}")
                
        except Exception as e:
            print(f"  ✗ Error: {e}")

def main():
    if len(sys.argv) < 2:
        print("Usage: forensic_analyzer.py <file>")
        print("Example: forensic_analyzer.py suspicious.pdf")
        sys.exit(1)
    
    filepath = sys.argv[1]
    analyzer = ForensicAnalyzer(filepath)
    analyzer.analyze()

if __name__ == "__main__":
    main()
