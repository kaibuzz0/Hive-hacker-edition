#!/usr/bin/env python3
"""
HIVE OS — Flipper Zero NFC Tool
Generate .nfc files for Flipper: Mifare Classic, Ultralight, DESFire stubs.

Supported:
  - mifare_classic   : Mifare Classic 1K/4K
  - mifare_ultralight: NTAG213/215/216, Ultralight C
  - mifare_desfire   : DESFire EV1/EV2 (stub)
  - em4100           : EM4100 HID prox (125 kHz cross)
  - 14a_raw          : ISO14443A raw

Usage:
  flipper_nfc.py --type mifare_classic --uid 0xA1B2C3D4 --file card.nfc
  flipper_nfc.py --type mifare_ultralight --uid 0x04AABBCCDDEEFF --data "hello" --file tag.nfc
  flipper_nfc.py --emulate --file card.nfc  # Show raw bytes
  flipper_nfc.py --analyze captured.nfc
"""

import sys
import os
import json
import struct
import argparse
from pathlib import Path
from datetime import datetime

class NFCGenerator:
    """Generate Flipper NFC files."""
    
    TYPES = ['mifare_classic', 'mifare_ultralight', 'mifare_desfire', 'em4100', '14a_raw']
    
    def __init__(self, nfc_type='mifare_ultralight'):
        self.nfc_type = nfc_type
        self.uid = []
        self.data = {}
        self.atqa = [0x00, 0x04]
        self.sak = 0x08
    
    def set_uid(self, uid_hex):
        """Set UID from hex string or int."""
        if isinstance(uid_hex, str):
            uid_hex = uid_hex.replace('0x', '')
            self.uid = [int(uid_hex[i:i+2], 16) for i in range(0, len(uid_hex), 2)]
        elif isinstance(uid_hex, int):
            # Convert int to bytes
            byte_length = 4 if self.nfc_type == 'mifare_classic' else 7
            self.uid = list(uid_hex.to_bytes(byte_length, 'big'))
    
    def set_data(self, text_data):
        """Set NDEF text payload."""
        self.data['text'] = text_data
    
    def generate_mifare_classic(self):
        """Generate Mifare Classic 1K structure."""
        sectors = []
        for i in range(16):
            sector = {
                'key_a': 'FFFFFFFFFFFF',
                'key_b': 'FFFFFFFFFFFF',
                'blocks': ['00000000000000000000000000000000'] * 4
            }
            # If we have data, put it in first sectors
            if i == 1 and 'text' in self.data:
                text = self.data['text'].encode('utf-8').hex()
                text += '00' * (48 - len(text)//2)
                for b in range(3):
                    sector['blocks'][b] = text[b*32:(b+1)*32]
            sectors.append(sector)
        return sectors
    
    def generate_ultralight(self):
        """Generate NTAG/Ultralight pages."""
        pages = []
        # UID pages
        pages.append(''.join(f'{b:02X}' for b in self.uid[:4]))
        if len(self.uid) > 4:
            pages.append(''.join(f'{b:02X}' for b in self.uid[4:]) + '4800')
        else:
            pages.append('00000048')
        
        # BCC + internal
        pages.append('E1100600')
        
        # User data (NTAG213 = 36 pages, NTAG215 = 132, NTAG216 = 230)
        if 'text' in self.data:
            # NDEF TLV
            text_bytes = self.data['text'].encode('utf-8')
            ndef = [
                0x03, len(text_bytes) + 5,  # NDEF Message TLV
                0xD1, 0x01, len(text_bytes) + 1, 0x54, 0x02, 0x65, 0x6E,  # Text record header + lang
            ] + list(text_bytes)
            
            # Pad to pages
            while len(ndef) % 4 != 0:
                ndef.append(0x00)
            
            for i in range(0, len(ndef), 4):
                pages.append(''.join(f'{b:02X}' for b in ndef[i:i+4]))
        
        # Fill remaining with zeros (simplified)
        while len(pages) < 16:
            pages.append('00000000')
        
        return pages
    
    def generate_em4100(self):
        """Generate EM4100 (125 kHz cross-over)."""
        # 40-bit code: 8 header + 32 data + 4 col
        return ''.join(f'{b:02X}' for b in self.uid[:5])
    
    def write_file(self, filename):
        """Write Flipper .nfc file."""
        lines = [
            "Filetype: Flipper NFC device",
            "Version: 2",
            "# Nfc device type",
        ]
        
        if self.nfc_type == 'mifare_classic':
            lines.append("Device type: Mifare Classic")
            lines.append(f"UID: {' '.join(f'{b:02X}' for b in self.uid)}")
            lines.append(f"ATQA: {' '.join(f'{b:02X}' for b in self.atqa)}")
            lines.append(f"SAK: {self.sak:02X}")
            lines.append("Mifare Classic type: 1K")
            lines.append("Data format version: 2")
            lines.append("# Mifare Classic data")
            sectors = self.generate_mifare_classic()
            for i, sector in enumerate(sectors):
                lines.append(f"Sector {i}:")
                for j, block in enumerate(sector['blocks']):
                    lines.append(f"  Block {i*4 + j}: {block}")
                lines.append(f"  Key A: {sector['key_a']}")
                lines.append(f"  Key B: {sector['key_b']}")
                lines.append(f"  Access bits: FF0780")
        
        elif self.nfc_type == 'mifare_ultralight':
            lines.append("Device type: NTAG215")  # Most common
            lines.append(f"UID: {' '.join(f'{b:02X}' for b in self.uid)}")
            lines.append("ATQA: 00 44")
            lines.append("SAK: 00")
            lines.append("Data format version: 2")
            lines.append("# NTAG data")
            pages = self.generate_ultralight()
            for i, page in enumerate(pages):
                lines.append(f"Page {i}: {page}")
        
        elif self.nfc_type == 'em4100':
            lines.append("Device type: EM4100")
            lines.append(f"UID: {self.generate_em4100()}")
            lines.append("Data: " + self.generate_em4100())
        
        else:
            lines.append(f"Device type: {self.nfc_type}")
            lines.append(f"UID: {' '.join(f'{b:02X}' for b in self.uid)}")
        
        content = '\n'.join(lines) + '\n'
        with open(filename, 'w') as f:
            f.write(content)
        return content
    
    @staticmethod
    def analyze(filename):
        """Analyze NFC file."""
        print(f"\n📶 NFC Tag Analysis")
        print(f"  File: {filename}")
        with open(filename, 'r') as f:
            lines = f.readlines()
        
        device_type = None
        uid = None
        for line in lines:
            if line.startswith('Device type:'):
                device_type = line.split(': ')[1].strip()
            elif line.startswith('UID:'):
                uid = line.split(': ')[1].strip()
        
        print(f"  Type: {device_type or 'Unknown'}")
        print(f"  UID:  {uid or 'Unknown'}")
        
        if device_type and 'Mifare' in device_type:
            print(f"  ⚠️  Mifare — check default keys: FFFFFFFFFFFF")
        elif device_type and 'NTAG' in device_type:
            print(f"  ℹ️  NTAG — likely NDEF formatted")
        
        return device_type, uid

def main():
    parser = argparse.ArgumentParser(description='Hive OS Flipper NFC Tool')
    parser.add_argument('--type', choices=NFCGenerator.TYPES, default='mifare_ultralight')
    parser.add_argument('--uid', default='0x04AABBCCDDEEFF')
    parser.add_argument('--data', default='', help='NDEF text payload')
    parser.add_argument('--file', required=True)
    parser.add_argument('--analyze', action='store_true')
    
    args = parser.parse_args()
    
    if args.analyze and os.path.exists(args.file):
        NFCGenerator.analyze(args.file)
        return
    
    gen = NFCGenerator(args.type)
    gen.set_uid(args.uid)
    if args.data:
        gen.set_data(args.data)
    
    content = gen.write_file(args.file)
    
    print(f"\n✅ Generated NFC file: {args.file}")
    print(f"  Type: {args.type}")
    print(f"  UID:  {args.uid}")
    print(f"\nTransfer to Flipper:")
    print(f"  qFlipper → SD card → /ext/nfc/{Path(args.file).name}")
    print()

if __name__ == '__main__':
    main()
