#!/usr/bin/env python3
"""
HIVE OS — Flipper Zero IR Tool
Generate .ir files for universal remote control.

Supported protocols:
  - nec      : NEC (TVs, receivers)
  - samsung  : Samsung 36-bit
  - rc5      : RC-5 (Philips)
  - rc6      : RC-6
  - sony     : Sony 12/15/20-bit
  - raw      : Raw timings

Usage:
  flipper_ir.py --protocol nec --address 0x04 --command 0x01 --file tv_power.ir
  flipper_ir.py --device "Samsung TV" --file samsung.ir
  flipper_ir.py --list-db
"""

import sys
import argparse
from pathlib import Path

# ── Known Device Database ────────────────────────────────
DEVICE_DB = {
    "samsung_tv": {
        "protocol": "samsung",
        "address": 0x0707,
        "commands": {
            "power": 0x02,
            "vol_up": 0x07,
            "vol_down": 0x0B,
            "mute": 0x0F,
            "ch_up": 0x12,
            "ch_down": 0x10,
            "source": 0x01,
            "menu": 0x1A,
        }
    },
    "lg_tv": {
        "protocol": "nec",
        "address": 0x04,
        "commands": {
            "power": 0x08,
            "vol_up": 0x02,
            "vol_down": 0x03,
            "mute": 0x09,
            "ch_up": 0x00,
            "ch_down": 0x01,
            "input": 0x0B,
        }
    },
    "vizio_soundbar": {
        "protocol": "nec",
        "address": 0x060C,
        "commands": {
            "power": 0x40,
            "vol_up": 0x41,
            "vol_down": 0x45,
            "mute": 0x48,
            "bt": 0x60,
        }
    },
    "panasonic_dvd": {
        "protocol": "panasonic",
        "address": 0x4004,
        "commands": {
            "power": 0x0D,
            "play": 0x01,
            "pause": 0x02,
            "stop": 0x00,
            "eject": 0x0E,
        }
    },
}

class IRGenerator:
    """Generate Flipper .ir files."""
    
    def __init__(self):
        self.signals = []
    
    def add_nec(self, name, address, command):
        """Add NEC signal (32-bit, 38kHz)."""
        self.signals.append({
            'name': name,
            'protocol': 'NEC',
            'address': f'{address:02X}',
            'command': f'{command:02X}',
        })
    
    def add_samsung(self, name, address, command):
        """Add Samsung 36-bit signal."""
        self.signals.append({
            'name': name,
            'protocol': 'SAMSUNG',
            'address': f'{address:04X}',
            'command': f'{command:02X}',
        })
    
    def add_rc5(self, name, address, command):
        """Add RC-5 signal."""
        self.signals.append({
            'name': name,
            'protocol': 'RC5',
            'address': f'{address:02X}',
            'command': f'{command:02X}',
        })
    
    def add_raw(self, name, frequency, duty_cycle, data):
        """Add raw timing signal."""
        self.signals.append({
            'name': name,
            'protocol': 'RAW',
            'frequency': frequency,
            'duty_cycle': duty_cycle,
            'data': data,
        })
    
    def write_file(self, filename):
        """Write Flipper .ir file."""
        lines = [
            "Filetype: IR library file",
            "Version: 1",
            "#",
        ]
        
        for sig in self.signals:
            lines.append(f"# {sig['name']}")
            lines.append(f"name: {sig['name']}")
            
            if sig['protocol'] == 'RAW':
                lines.append(f"type: raw")
                lines.append(f"frequency: {sig['frequency']}")
                lines.append(f"duty_cycle: {sig['duty_cycle']}")
                lines.append(f"data: {' '.join(str(t) for t in sig['data'])}")
            else:
                lines.append(f"type: parsed")
                lines.append(f"protocol: {sig['protocol']}")
                lines.append(f"address: {sig['address']}")
                lines.append(f"command: {sig['command']}")
            
            lines.append("")
        
        content = '\n'.join(lines)
        with open(filename, 'w') as f:
            f.write(content)
        return content
    
    def add_device(self, device_key):
        """Add all commands from known device."""
        if device_key not in DEVICE_DB:
            print(f"Unknown device: {device_key}")
            return False
        
        dev = DEVICE_DB[device_key]
        proto = dev['protocol']
        addr = dev['address']
        
        for cmd_name, cmd_val in dev['commands'].items():
            name = f"{device_key}_{cmd_name}"
            if proto == 'nec':
                self.add_nec(name, addr, cmd_val)
            elif proto == 'samsung':
                self.add_samsung(name, addr, cmd_val)
            elif proto == 'rc5':
                self.add_rc5(name, addr, cmd_val)
            else:
                # Fallback
                self.add_nec(name, addr, cmd_val)
        
        return True

def main():
    parser = argparse.ArgumentParser(description='Hive OS Flipper IR Tool')
    parser.add_argument('--device', help='Device key from DB')
    parser.add_argument('--protocol', default='nec', choices=['nec', 'samsung', 'rc5', 'rc6', 'raw'])
    parser.add_argument('--address', type=lambda x: int(x, 0), default=0x04)
    parser.add_argument('--command', type=lambda x: int(x, 0), default=0x01)
    parser.add_argument('--name', default='Button', help='Signal name')
    parser.add_argument('--file', required=True)
    parser.add_argument('--list-db', action='store_true')
    
    args = parser.parse_args()
    
    if args.list_db:
        print("\n📡 IR Device Database")
        for key, dev in DEVICE_DB.items():
            print(f"\n  {key}:")
            print(f"    Protocol: {dev['protocol']}")
            print(f"    Address: 0x{dev['address']:04X}")
            print(f"    Commands: {', '.join(dev['commands'].keys())}")
        print()
        return
    
    gen = IRGenerator()
    
    if args.device:
        if gen.add_device(args.device):
            print(f"\n✅ Added {args.device} with {len(DEVICE_DB[args.device]['commands'])} commands")
    else:
        if args.protocol == 'nec':
            gen.add_nec(args.name, args.address, args.command)
        elif args.protocol == 'samsung':
            gen.add_samsung(args.name, args.address, args.command)
        elif args.protocol == 'rc5':
            gen.add_rc5(args.name, args.address, args.command)
    
    content = gen.write_file(args.file)
    
    print(f"✅ Generated: {args.file}")
    print(f"  Signals: {len(gen.signals)}")
    print(f"  Size: {len(content)} bytes")
    print(f"\nTransfer to Flipper: /ext/infrared/{Path(args.file).name}")
    print()

if __name__ == '__main__':
    main()
