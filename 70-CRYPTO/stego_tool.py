#!/usr/bin/env python3
"""
HIVE TOOL: stego_tool
Steganography encoder/decoder for hiding data in images
"""

import sys
import os
from pathlib import Path

class StegoTool:
    """Simple LSB steganography tool"""
    
    @staticmethod
    def hide_text_in_png(input_path, output_path, message):
        """Hide text message in PNG file"""
        try:
            with open(input_path, 'rb') as f:
                data = bytearray(f.read())
            
            # Check if PNG
            if data[:8] != b'\\x89PNG\\r\\n\\x1a\\n':
                return False, "Not a valid PNG file"
            
            # Convert message to binary
            binary_msg = ''.join(format(ord(c), '08b') for c in message)
            binary_msg += '00000000'  # End marker
            
            if len(binary_msg) > len(data) - 100:
                return False, "Message too long for this image"
            
            # Embed in LSB of pixel data (skip header)
            header_size = 100  # Skip header
            for i, bit in enumerate(binary_msg):
                data[header_size + i] = (data[header_size + i] & 0xFE) | int(bit)
            
            with open(output_path, 'wb') as f:
                f.write(data)
            
            return True, f"Message hidden: {len(message)} chars"
            
        except Exception as e:
            return False, str(e)
    
    @staticmethod
    def extract_text_from_png(input_path):
        """Extract hidden text from PNG"""
        try:
            with open(input_path, 'rb') as f:
                data = bytearray(f.read())
            
            # Check if PNG
            if data[:8] != b'\\x89PNG\\r\\n\\x1a\\n':
                return None, "Not a valid PNG file"
            
            # Extract LSB data
            header_size = 100
            binary_data = ''
            
            for i in range(header_size, min(header_size + 10000, len(data))):
                binary_data += str(data[i] & 1)
            
            # Convert binary to text
            message = ''
            for i in range(0, len(binary_data) - 8, 8):
                byte = binary_data[i:i+8]
                char = chr(int(byte, 2))
                if char == '\\x00':
                    break
                message += char
            
            return message, "Extraction complete"
            
        except Exception as e:
            return None, str(e)
    
    @staticmethod
    def text_to_zero_width(text):
        """Encode text to zero-width characters"""
        binary = ''.join(format(ord(c), '08b') for c in text)
        zero_width = ''
        for bit in binary:
            if bit == '0':
                zero_width += '\\u200B'  # Zero-width space
            else:
                zero_width += '\\u200C'  # Zero-width non-joiner
        return zero_width
    
    @staticmethod
    def zero_width_to_text(zero_width_text):
        """Decode zero-width characters to text"""
        binary = ''
        for char in zero_width_text:
            if char == '\\u200B':
                binary += '0'
            elif char == '\\u200C':
                binary += '1'
        
        text = ''
        for i in range(0, len(binary) - 8, 8):
            byte = binary[i:i+8]
            text += chr(int(byte, 2))
        return text

def main():
    print("""
╔══════════════════════════════════════════╗
║  🕵️ HIVE Steganography Tool             ║
║  Hide messages in plain sight           ║
╚══════════════════════════════════════════╝
    """)
    
    print("\n📋 Modes:\n")
    print("  1. Hide text in PNG image")
    print("  2. Extract text from PNG image")
    print("  3. Encode to zero-width characters")
    print("  4. Decode zero-width characters")
    
    choice = input("\nSelect [1-4]: ").strip()
    
    stego = StegoTool()
    
    if choice == '1':
        input_file = input("Input PNG file: ").strip()
        output_file = input("Output PNG file: ").strip()
        message = input("Message to hide: ").strip()
        
        if not Path(input_file).exists():
            print(f"✗ File not found: {input_file}")
            return
        
        success, msg = stego.hide_text_in_png(input_file, output_file, message)
        if success:
            print(f"✓ {msg}")
            print(f"  Hidden in: {output_file}")
        else:
            print(f"✗ Error: {msg}")
    
    elif choice == '2':
        input_file = input("Input PNG file: ").strip()
        
        if not Path(input_file).exists():
            print(f"✗ File not found: {input_file}")
            return
        
        message, msg = stego.extract_text_from_png(input_file)
        if message:
            print(f"✓ {msg}")
            print(f"\n📝 Hidden message:")
            print(f"  {message}")
        else:
            print(f"✗ Error: {msg}")
    
    elif choice == '3':
        text = input("Text to encode: ").strip()
        encoded = stego.text_to_zero_width(text)
        print(f"\n📝 Encoded (copy the invisible characters):")
        print(f"  {encoded}")
        print(f"\n  Length: {len(encoded)} zero-width chars")
    
    elif choice == '4':
        encoded = input("Zero-width text: ").strip()
        text = stego.zero_width_to_text(encoded)
        print(f"\n📝 Decoded message:")
        print(f"  {text}")
    
    else:
        print("✗ Invalid choice")

if __name__ == "__main__":
    main()
