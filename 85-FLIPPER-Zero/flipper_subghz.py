#!/usr/bin/env python3
"""
HIVE OS — Flipper Zero Sub-GHz Tool
Generate .sub files for Flipper, analyze captured signals.

Supported protocols:
  - raw       : Raw signal data
  - keeloq    : KeeLoq (garage doors)
  - came      : CAME gates
  - nice      : NICE gates
  - princeton : Princeton remotes
  - linear    : Linear 10bit
  - static    : Fixed-code (simple replay)

Usage:
  flipper_subghz.py --protocol keeloq --freq 433.92 --key 0x123456 --file out.sub
  flipper_subghz.py --analyze captured.sub
  flipper_subghz.py --list-db
"""

import sys
import os
import json
import struct
import argparse
from pathlib import Path
from datetime import datetime

# ── Constants ───────────────────────────────────────────────
FLIPPER_FILE_VERSION = 1
DB_PATH = Path(__file__).parent / 'flipper_db.json'

# ── Known Signal Database ──────────────────────────────────
DEFAULT_DB = {
    "garage_doors": [
        {"name": "CAME 433", "freq": 433.92, "protocol": "came", "preset": "FAM", "note": "Common EU gate"},
        {"name": "Linear 318", "freq": 318.0, "protocol": "linear", "preset": "FAM", "note": "US garage"},
        {"name": "Nice FLO", "freq": 433.92, "protocol": "nice", "preset": "FAM", "note": "Nice gates"},
        {"name": "Princeton PT", "freq": 433.92, "protocol": "princeton", "preset": "FAM", "note": "PT2262/PT2272"},
    ],
    "car_keys": [
        {"name": "Toyota Key", "freq": 315.0, "protocol": "keeloq", "preset": "FAM", "note": "KeeLoq HCS"},
        {"name": "Honda Key", "freq": 433.92, "protocol": "keeloq", "preset": "FAM", "note": "KeeLoq HCS"},
        {"name": "Ford Key", "freq": 315.0, "protocol": "keeloq", "preset": "FAM", "note": "KeeLoq HCS"},
    ],
    "alarms": [
        {"name": "Generic Alarm", "freq": 433.92, "protocol": "static", "preset": "FAM", "note": "Fixed code"},
    ],
}

# ── Flipper .sub File Generator ────────────────────────────
class SubGHzGenerator:
    """Generate Flipper Zero .sub files."""
    
    PROTOCOLS = ['raw', 'keeloq', 'came', 'nice', 'princeton', 'linear', 'static']
    
    def __init__(self, protocol='raw', frequency=433.92, preset='FAM'):
        self.protocol = protocol
        self.frequency = frequency
        self.preset = preset
        self.data = []
    
    def add_raw(self, timings):
        """Add raw signal timings (µs on/off pairs)."""
        self.data = timings
    
    def generate_keeloq(self, serial=0x123456, btn=0, sync=0x0F):
        """Generate KeeLoq packet (simplified)."""
        # KeeLoq: 64-bit packet
        # Serial (28) + Button (4) + Sync (16) + CRC (16)
        # Simplified: just generate placeholder
        packet = ((serial & 0x0FFFFFFF) << 36) | ((btn & 0xF) << 32) | ((sync & 0xFFFF) << 16)
        # Encode as pulse timings (very simplified)
        timings = []
        for i in range(64):
            bit = (packet >> (63 - i)) & 1
            if bit:
                timings.extend([400, 900])   # 1 = short-long
            else:
                timings.extend([900, 400])  # 0 = long-short
        return timings
    
    def generate_came(self, code=0x123):
        """Generate CAME 12-bit packet (simplified)."""
        # CAME: 12-bit code + inverted
        timings = []
        # Preamble
        timings.extend([3200, 700])
        for i in range(12):
            bit = (code >> (11 - i)) & 1
            if bit:
                timings.extend([700, 1400])
            else:
                timings.extend([1400, 700])
        return timings
    
    def generate_nice(self, code=0x1234):
        """Generate Nice FLO packet (simplified)."""
        timings = []
        for i in range(52):
            bit = (code >> (51 - i)) & 1
            if bit:
                timings.extend([700, 1400])
            else:
                timings.extend([1400, 700])
        return timings
    
    def generate_princeton(self, code=0x123456):
        """Generate PT2262 packet."""
        timings = []
        for i in range(24):
            bit = (code >> (23 - i)) & 1
            if bit:
                timings.extend([350, 1050])
            else:
                timings.extend([1050, 350])
        return timings
    
    def generate_linear(self, code=0x123):
        """Generate Linear 10-bit."""
        timings = []
        for i in range(10):
            bit = (code >> (9 - i)) & 1
            if bit:
                timings.extend([1000, 2000])
            else:
                timings.extend([2000, 1000])
        return timings
    
    def generate_static(self, code=0x12345678):
        """Generate fixed-code packet."""
        timings = []
        for i in range(32):
            bit = (code >> (31 - i)) & 1
            if bit:
                timings.extend([500, 1000])
            else:
                timings.extend([1000, 500])
        return timings
    
    def generate(self, **kwargs):
        """Generate signal based on protocol."""
        if self.protocol == 'raw':
            pass  # Already set
        elif self.protocol == 'keeloq':
            self.data = self.generate_keeloq(**kwargs)
        elif self.protocol == 'came':
            self.data = self.generate_came(**kwargs)
        elif self.protocol == 'nice':
            self.data = self.generate_nice(**kwargs)
        elif self.protocol == 'princeton':
            self.data = self.generate_princeton(**kwargs)
        elif self.protocol == 'linear':
            self.data = self.generate_linear(**kwargs)
        elif self.protocol == 'static':
            self.data = self.generate_static(**kwargs)
        else:
            raise ValueError(f"Unknown protocol: {self.protocol}")
    
    def write_file(self, filename):
        """Write Flipper .sub file."""
        lines = [
            "Filetype: Flipper SubGhz Key File",
            f"Version: {FLIPPER_FILE_VERSION}",
            f"Frequency: {int(self.frequency * 1000000)}",
            f"Preset: {self.preset}",
            f"Protocol: {self.protocol}",
        ]
        
        if self.protocol == 'raw':
            lines.append(f"RAW_Data: {' '.join(str(t) for t in self.data)}")
        else:
            # For protocol-specific, encode differently
            lines.append(f"Data: {hex(self._pack_data())}")
            if self.data:
                lines.append(f"RAW_Data: {' '.join(str(t) for t in self.data)}")
        
        content = '\n'.join(lines) + '\n'
        
        with open(filename, 'w') as f:
            f.write(content)
        
        return content
    
    def _pack_data(self):
        """Pack data for protocol-specific files."""
        # Simplified
        return 0
    
    @staticmethod
    def read_file(filename):
        """Read and parse .sub file."""
        result = {}
        with open(filename, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('Filetype:'):
                    result['filetype'] = line.split(': ', 1)[1]
                elif line.startswith('Frequency:'):
                    result['frequency'] = int(line.split(': ', 1)[1]) / 1000000
                elif line.startswith('Protocol:'):
                    result['protocol'] = line.split(': ', 1)[1]
                elif line.startswith('RAW_Data:'):
                    raw = line.split(': ', 1)[1].strip()
                    result['raw'] = [int(x) for x in raw.split()]
        return result
    
    @staticmethod
    def analyze(filename):
        """Analyze a .sub file."""
        data = SubGHzGenerator.read_file(filename)
        print(f"\n📡 Sub-GHz Signal Analysis")
        print(f"  File:     {filename}")
        print(f"  Protocol: {data.get('protocol', 'unknown')}")
        print(f"  Frequency: {data.get('frequency', 'unknown')} MHz")
        if 'raw' in data:
            raw = data['raw']
            print(f"  Pulses:   {len(raw)}")
            print(f"  Timing range: {min(raw)}µs to {max(raw)}µs")
            print(f"  Average:  {sum(raw)//len(raw)}µs")
            
            # Try to detect protocol from timing
            avg = sum(raw) / len(raw)
            if 300 < avg < 600:
                print(f"  ⚠️  Possible CAME / Princeton signal")
            elif 600 < avg < 1000:
                print(f"  ⚠️  Possible KeeLoq / Nice signal")
            elif 1000 < avg < 2000:
                print(f"  ⚠️  Possible Linear signal")
        
        return data

# ── Main ───────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(description='Hive OS Flipper Sub-GHz Tool')
    parser.add_argument('--protocol', choices=SubGHzGenerator.PROTOCOLS, default='raw',
                       help='Signal protocol')
    parser.add_argument('--freq', type=float, default=433.92,
                       help='Frequency in MHz (default: 433.92)')
    parser.add_argument('--preset', default='FAM',
                       help='Modulation preset (FAM, etc.)')
    parser.add_argument('--file', required=True,
                       help='Output .sub file')
    parser.add_argument('--key', type=lambda x: int(x, 0), default=0x123456,
                       help='Key/serial value (hex or decimal)')
    parser.add_argument('--analyze', metavar='FILE',
                       help='Analyze existing .sub file')
    parser.add_argument('--list-db', action='store_true',
                       help='List known signal database')
    
    args = parser.parse_args()
    
    if args.list_db:
        print("\n📚 Known Signal Database\n")
        for category, items in DEFAULT_DB.items():
            print(f"  {category.upper()}:")
            for item in items:
                print(f"    • {item['name']}: {item['freq']} MHz ({item['protocol']}) — {item['note']}")
        print()
        return
    
    if args.analyze:
        SubGHzGenerator.analyze(args.analyze)
        return
    
    # Generate new file
    gen = SubGHzGenerator(args.protocol, args.freq, args.preset)
    gen.generate(code=args.key)
    content = gen.write_file(args.file)
    
    print(f"\n✅ Generated: {args.file}")
    print(f"  Protocol:  {args.protocol}")
    print(f"  Frequency: {args.freq} MHz")
    print(f"  Size:      {len(content)} bytes")
    print(f"\nTransfer to Flipper:")
    print(f"  qFlipper → SD card → /ext/subghz/{Path(args.file).name}")
    print()

if __name__ == '__main__':
    main()
