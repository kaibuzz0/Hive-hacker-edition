# 🐬 Hive OS — Flipper Zero Plugin

Turn your phone into a **Flipper Zero command center** via Hive OS.

## What This Plugin Does

Since phones lack Flipper hardware (CC1101, 125 kHz RFID, etc.), this plugin operates in **two modes**:

| Mode | How | Use Case |
|------|-----|----------|
| **Standalone** | Generate Flipper files (.sub, .rfid, .nfc, .ir) on phone, transfer via SD or USB | Build payloads offline |
| **Bridge** | Connect real Flipper via USB OTG or Bluetooth, send commands from Hive | Remote control + automation |

## Capabilities

| Protocol | Generate Files | Analyze | Bridge to Real Flipper |
|----------|---------------|---------|------------------------|
| **Sub-GHz** (.sub) | ✅ | ✅ | ✅ Via serial |
| **RFID 125 kHz** (.rfid) | ✅ | ✅ | ✅ Via serial |
| **NFC** (.nfc) | ✅ | ✅ | ✅ Via serial |
| **IR** (.ir) | ✅ | ✅ | ✅ Via serial |
| **BadUSB** (.badusb) | ✅ | — | ✅ Via serial |
| **GPIO/UART** | ✅ Scripts | — | ✅ Direct pin access |

## Quick Start

```bash
# Generate a Sub-GHz file for a common garage door
cd 85-FLIPPER-Zero
python3 flipper_subghz.py --freq 433.92 --protocol keeloq --file garage.sub

# Transfer to Flipper via qFlipper or copy to SD card
# Location on Flipper: /ext/subghz/
```

## Requirements

- USB OTG cable (for bridge mode)
- qFlipper desktop app (for file transfer)
- OR: Bluetooth serial app (for wireless bridge)

## File Format Reference

All generated files are valid Flipper format — copy directly to `/ext/` on SD card.

| Directory on Flipper | File Type |
|---------------------|-----------|
| `/ext/subghz/` | `.sub` |
| `/ext/lfrfid/` | `.rfid` |
| `/ext/nfc/` | `.nfc` |
| `/ext/infrared/` | `.ir` |
| `/ext/badusb/` | `.badusb` / `.txt` |
| `/ext/apps/` | `.fap` |

---

**Note:** This is a software companion. It does NOT give your phone a CC1101 chip. For actual RF transmission, you need a real Flipper Zero or an RTL-SDR dongle via USB OTG.
