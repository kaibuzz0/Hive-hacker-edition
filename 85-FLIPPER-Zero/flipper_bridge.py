#!/usr/bin/env python3
"""
HIVE OS — Flipper Zero Serial Bridge
Connect to a real Flipper Zero via USB OTG serial and control it from Hive.

Requirements:
  - USB OTG cable
  - Flipper Zero with USB-UART Bridge app (or qFlipper CLI mode)
  - pyserial (pip install pyserial)

Usage:
  flipper_bridge.py --scan              # Find connected Flipper
  flipper_bridge.py --port /dev/ttyACM0 --subghz send --file garage.sub
  flipper_bridge.py --port /dev/ttyACM0 --nfc read
  flipper_bridge.py --port /dev/ttyACM0 --ir transmit --file tv.ir
  flipper_bridge.py --interactive       # Interactive shell
"""

import sys
import os
import time
import glob
import json
import argparse
import subprocess
from pathlib import Path
from datetime import datetime

try:
    import serial
    import serial.tools.list_ports
    HAS_SERIAL = True
except ImportError:
    HAS_SERIAL = False

FLIPPER_VID = 0x0483  # STM32 vendor ID
FLIPPER_PID = 0x5740  # STM32 CDC

class FlipperBridge:
    """Serial bridge to Flipper Zero."""
    
    def __init__(self, port=None, baudrate=115200, timeout=5):
        self.port = port
        self.baudrate = baudrate
        self.timeout = timeout
        self.ser = None
        self.connected = False
    
    @staticmethod
    def find_flipper():
        """Auto-detect Flipper serial port."""
        if not HAS_SERIAL:
            print("❌ pyserial not installed. Run: pip install pyserial")
            return None
        import serial.tools.list_ports
        
        # Try by USB VID/PID
        for p in serial.tools.list_ports.comports():
            if p.vid == FLIPPER_VID and p.pid == FLIPPER_PID:
                print(f"✅ Found Flipper at {p.device} ({p.description})")
                return p.device
        
        # Fallback: common Linux/Android serial paths
        for pattern in ['/dev/ttyACM*', '/dev/ttyUSB*', '/dev/tty.usbmodem*']:
            devices = glob.glob(pattern)
            for dev in devices:
                print(f"⚠️  Possible Flipper at {dev} (unverified)")
                return dev
        
        print("❌ No Flipper found. Check USB OTG connection.")
        return None
    
    def connect(self):
        """Open serial connection."""
        if not HAS_SERIAL:
            print("❌ pyserial not installed")
            return False
        
        if not self.port:
            self.port = self.find_flipper()
            if not self.port:
                return False
        
        try:
            self.ser = serial.Serial(self.port, self.baudrate, timeout=self.timeout)
            self.connected = True
            print(f"✅ Connected to Flipper on {self.port}")
            
            # Send hello
            self.send_command("device_info\r\n")
            time.sleep(0.5)
            response = self.read_response()
            if response:
                print(f"📡 Flipper says: {response.strip()[:100]}")
            
            return True
        except serial.SerialException as e:
            print(f"❌ Serial error: {e}")
            return False
    
    def disconnect(self):
        """Close connection."""
        if self.ser:
            self.ser.close()
            self.ser = None
        self.connected = False
        print("🔌 Disconnected")
    
    def send_command(self, cmd):
        """Send command to Flipper."""
        if not self.ser:
            print("❌ Not connected")
            return False
        
        self.ser.write(cmd.encode('utf-8'))
        return True
    
    def read_response(self, timeout=5):
        """Read response from Flipper."""
        if not self.ser:
            return ""
        
        start = time.time()
        lines = []
        while time.time() - start < timeout:
            if self.ser.in_waiting:
                line = self.ser.readline().decode('utf-8', errors='ignore')
                lines.append(line)
                if line.strip().endswith('>') or line.strip().endswith('OK'):
                    break
            time.sleep(0.1)
        
        return ''.join(lines)
    
    def subghz_send(self, sub_file):
        """Send Sub-GHz file via serial CLI."""
        if not os.path.exists(sub_file):
            print(f"❌ File not found: {sub_file}")
            return False
        
        print(f"📡 Sending Sub-GHz: {sub_file}")
        
        # Read and parse .sub file
        with open(sub_file, 'r') as f:
            content = f.read()
        
        # Send via CLI if Flipper CLI supports it
        self.send_command(f"subghz tx_file {sub_file}\r\n")
        time.sleep(2)
        resp = self.read_response()
        print(f"  Response: {resp.strip()[:200]}")
        return True
    
    def nfc_read(self):
        """Read NFC tag."""
        print("📡 NFC Read: Hold tag near Flipper...")
        self.send_command("nfc read\r\n")
        time.sleep(3)
        resp = self.read_response(timeout=10)
        print(f"  Response:\n{resp}")
        return resp
    
    def nfc_emulate(self, nfc_file):
        """Emulate NFC tag."""
        print(f"📡 NFC Emulate: {nfc_file}")
        self.send_command(f"nfc emulate {nfc_file}\r\n")
        time.sleep(2)
        resp = self.read_response()
        print(f"  Response: {resp.strip()[:200]}")
        return True
    
    def ir_transmit(self, ir_file):
        """Transmit IR signal."""
        print(f"📡 IR Transmit: {ir_file}")
        self.send_command(f"ir tx {ir_file}\r\n")
        time.sleep(1)
        resp = self.read_response()
        print(f"  Response: {resp.strip()[:200]}")
        return True
    
    def interactive(self):
        """Interactive CLI to Flipper."""
        print("\n📡 Flipper Interactive Shell")
        print("  Type commands and press Enter")
        print("  'exit' to quit\n")
        
        while True:
            try:
                cmd = input("flipper> ").strip()
                if cmd.lower() in ['exit', 'quit', 'q']:
                    break
                
                self.send_command(cmd + "\r\n")
                time.sleep(0.5)
                resp = self.read_response()
                print(resp)
            except KeyboardInterrupt:
                break
            except EOFError:
                break

def main():
    parser = argparse.ArgumentParser(description='Hive OS Flipper Serial Bridge')
    parser.add_argument('--port', help='Serial port (auto-detect if omitted)')
    parser.add_argument('--scan', action='store_true', help='Scan for Flipper')
    parser.add_argument('--interactive', action='store_true', help='Interactive shell')
    parser.add_argument('--subghz-send', metavar='FILE', help='Send Sub-GHz file')
    parser.add_argument('--nfc-read', action='store_true', help='Read NFC tag')
    parser.add_argument('--nfc-emulate', metavar='FILE', help='Emulate NFC tag')
    parser.add_argument('--ir-transmit', metavar='FILE', help='Transmit IR file')
    
    args = parser.parse_args()
    
    if args.scan:
        print("🔍 Scanning for Flipper Zero...")
        FlipperBridge.find_flipper()
        return
    
    if not HAS_SERIAL:
        print("❌ pyserial not installed.")
        print("   Install: pip install pyserial")
        print("   Then re-run with USB OTG cable connected.")
        sys.exit(1)
    
    bridge = FlipperBridge(port=args.port)
    
    if not bridge.connect():
        sys.exit(1)
    
    try:
        if args.interactive:
            bridge.interactive()
        elif args.subghz_send:
            bridge.subghz_send(args.subghz_send)
        elif args.nfc_read:
            bridge.nfc_read()
        elif args.nfc_emulate:
            bridge.nfc_emulate(args.nfc_emulate)
        elif args.ir_transmit:
            bridge.ir_transmit(args.ir_transmit)
        else:
            print("No action specified. Use --interactive, --subghz-send, --nfc-read, etc.")
    finally:
        bridge.disconnect()

if __name__ == '__main__':
    main()
