#!/usr/bin/env python3
"""
HIVE TOOL: cipher_decoder
Decode various ciphers and encodings
"""

import sys
import base64
import binascii

class CipherDecoder:
    """Multi-cipher decoder"""
    
    @staticmethod
    def try_base64(text):
        """Try base64 decoding"""
        try:
            decoded = base64.b64decode(text).decode('utf-8')
            return decoded
        except:
            return None
    
    @staticmethod
    def try_hex(text):
        """Try hex decoding"""
        try:
            decoded = bytes.fromhex(text).decode('utf-8')
            return decoded
        except:
            return None
    
    @staticmethod
    def try_rot13(text):
        """Try ROT13"""
        result = ""
        for char in text:
            if char.isalpha():
                shift = 13
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result
    
    @staticmethod
    def try_caesar(text, shift=3):
        """Try Caesar cipher with given shift"""
        result = ""
        for char in text:
            if char.isalpha():
                base = ord('A') if char.isupper() else ord('a')
                result += chr((ord(char) - base + shift) % 26 + base)
            else:
                result += char
        return result
    
    @staticmethod
    def try_binary(text):
        """Try binary decoding"""
        try:
            # Remove spaces
            binary = text.replace(' ', '')
            if all(c in '01' for c in binary):
                chars = [chr(int(binary[i:i+8], 2)) for i in range(0, len(binary), 8)]
                return ''.join(chars)
        except:
            return None
        return None
    
    @staticmethod
    def try_morse(text):
        """Try Morse code"""
        morse_map = {
            '.-': 'A', '-...': 'B', '-.-.': 'C', '-..': 'D', '.': 'E',
            '..-.': 'F', '--.': 'G', '....': 'H', '..': 'I', '.---': 'J',
            '-.-': 'K', '.-..': 'L', '--': 'M', '-.': 'N', '---': 'O',
            '.--.': 'P', '--.-': 'Q', '.-.': 'R', '...': 'S', '-': 'T',
            '..-': 'U', '...-': 'V', '.--': 'W', '-..-': 'X', '-.--': 'Y',
            '--..': 'Z', '-----': '0', '.----': '1', '..---': '2',
            '...--': '3', '....-': '4', '.....': '5', '-....': '6',
            '--...': '7', '---..': '8', '----.': '9'
        }
        
        try:
            chars = text.split()
            result = ''.join(morse_map.get(c, '?') for c in chars)
            return result if '?' not in result else None
        except:
            return None
    
    def auto_decode(self, text):
        """Try all decoders"""
        results = []
        
        # Base64
        result = self.try_base64(text)
        if result:
            results.append(('Base64', result))
        
        # Hex
        result = self.try_hex(text)
        if result:
            results.append(('Hex', result))
        
        # Binary
        result = self.try_binary(text)
        if result:
            results.append(('Binary', result))
        
        # Morse
        result = self.try_morse(text)
        if result:
            results.append(('Morse', result))
        
        # ROT13
        results.append(('ROT13', self.try_rot13(text)))
        
        # Caesar (try common shifts)
        for shift in [1, 3, 5, 13, 25]:
            result = self.try_caesar(text, shift)
            results.append((f'Caesar({shift})', result))
        
        return results

def main():
    print("""
╔══════════════════════════════════════════╗
║  🔓 HIVE Cipher Decoder                   ║
║  Multi-algorithm decoder                 ║
╚══════════════════════════════════════════╝
    """)
    
    if len(sys.argv) < 2:
        text = input("Enter encoded text: ").strip()
    else:
        text = sys.argv[1]
    
    print(f"\n🔍 Analyzing: {text[:50]}...")
    print()
    
    decoder = CipherDecoder()
    results = decoder.auto_decode(text)
    
    print("Possible decodings:")
    print("-" * 60)
    
    found = False
    for name, result in results:
        if result and result != text:
            print(f"  {name:15} | {result}")
            found = True
    
    if not found:
        print("  No decodings found with common algorithms")
    
    print("-" * 60)

if __name__ == "__main__":
    main()
