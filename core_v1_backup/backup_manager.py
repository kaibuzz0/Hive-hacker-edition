#!/usr/bin/env python3
"""
HIVE OS - Backup Manager
Complete system backup and restore utility
"""

import os
import sys
import json
import shutil
import tarfile
from pathlib import Path
from datetime import datetime

HIVE_ROOT = Path.home() / ".hive"
BACKUP_DIR = HIVE_ROOT / "backups"

class HiveBackupManager:
    """Manage Hive OS backups"""
    
    def __init__(self):
        self.backup_dir = BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        
    def create_backup(self, name=None):
        """Create full system backup"""
        if not name:
            name = f"hive_backup_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        backup_path = self.backup_dir / name
        
        print(f"📦 Creating backup: {name}")
        print(f"   Source: {HIVE_ROOT}")
        print(f"   Destination: {backup_path}")
        
        # Create archive
        archive_file = f"{backup_path}.tar.gz"
        
        with tarfile.open(archive_file, "w:gz") as tar:
            # Add core files
            for item in ['agents', 'tools', 'state', 'registry.json']:
                item_path = HIVE_ROOT / item
                if item_path.exists():
                    tar.add(item_path, arcname=item)
                    print(f"   ✓ Added {item}")
        
        # Create manifest
        manifest = {
            "version": "2.0.0",
            "created": datetime.now().isoformat(),
            "source": str(HIVE_ROOT),
            "components": ['agents', 'tools', 'state', 'registry'],
            "size": os.path.getsize(archive_file)
        }
        
        with open(f"{backup_path}.json", 'w') as f:
            json.dump(manifest, f, indent=2)
        
        print(f"\n✓ Backup complete: {archive_file}")
        print(f"   Size: {manifest['size']:,} bytes")
        
        return archive_file
    
    def list_backups(self):
        """List available backups"""
        print("📋 Available Backups:")
        print("-" * 60)
        
        backups = sorted(self.backup_dir.glob("hive_backup_*.tar.gz"), 
                        key=lambda x: x.stat().st_mtime, reverse=True)
        
        if not backups:
            print("  No backups found")
            return
        
        for i, backup in enumerate(backups, 1):
            size_mb = backup.stat().st_size / (1024 * 1024)
            manifest_file = backup.with_suffix('').with_suffix('.json')
            
            info = ""
            if manifest_file.exists():
                try:
                    with open(manifest_file) as f:
                        data = json.load(f)
                        info = f"| v{data.get('version', '?')}"
                except:
                    pass
            
            print(f"  [{i}] {backup.name}")
            print(f"      Size: {size_mb:.1f} MB {info}")
    
    def restore_backup(self, backup_file):
        """Restore from backup"""
        backup_path = Path(backup_file)
        
        if not backup_path.exists():
            print(f"✗ Backup not found: {backup_file}")
            return False
        
        print(f"🔄 Restoring from: {backup_path.name}")
        print(f"   Target: {HIVE_ROOT}")
        
        # Confirm
        confirm = input("\n⚠ This will overwrite current Hive data. Continue? (yes/no): ")
        if confirm.lower() != 'yes':
            print("Restore cancelled")
            return False
        
        # Backup current first
        print("   Creating safety backup of current state...")
        self.create_backup(f"pre_restore_{datetime.now().strftime('%Y%m%d_%H%M%S')}")
        
        # Extract
        with tarfile.open(backup_path, "r:gz") as tar:
            tar.extractall(HIVE_ROOT)
        
        print("\n✓ Restore complete!")
        print("   Run 'hive --status' to verify")
        
        return True
    
    def export_to_github(self, output_dir):
        """Export clean backup for GitHub"""
        print("📤 Exporting for GitHub...")
        print(f"   Output: {output_dir}")
        
        output_path = Path(output_dir)
        output_path.mkdir(parents=True, exist_ok=True)
        
        # Copy essential files (no private data)
        essentials = {
            'agents': HIVE_ROOT / 'agents',
            'tools': HIVE_ROOT / 'tools',
            'config': HIVE_ROOT / 'config',
        }
        
        for name, src in essentials.items():
            if src.exists():
                dst = output_path / name
                if dst.exists():
                    shutil.rmtree(dst)
                shutil.copytree(src, dst)
                print(f"   ✓ Exported {name}")
        
        # Create clean registry template
        clean_registry = {
            "version": "2.0.0",
            "initialized": datetime.now().isoformat(),
            "agents": {},
            "tasks": {},
            "messages": [],
            "system": {
                "self_healing": True,
                "auto_backup": True,
                "verify_chains": True
            }
        }
        
        with open(output_path / 'registry.json', 'w') as f:
            json.dump(clean_registry, f, indent=2)
        
        print("\n✓ GitHub export complete")
        print(f"   Ready to commit: {output_path}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Hive OS Backup Manager')
    parser.add_argument('action', choices=['create', 'list', 'restore', 'export'])
    parser.add_argument('--file', help='Backup file for restore')
    parser.add_argument('--name', help='Name for new backup')
    parser.add_argument('--output', help='Output directory for export')
    
    args = parser.parse_args()
    
    manager = HiveBackupManager()
    
    if args.action == 'create':
        manager.create_backup(args.name)
    
    elif args.action == 'list':
        manager.list_backups()
    
    elif args.action == 'restore':
        if not args.file:
            print("✗ --file required for restore")
            sys.exit(1)
        manager.restore_backup(args.file)
    
    elif args.action == 'export':
        manager.export_to_github(args.output or './hive-export')

if __name__ == "__main__":
    main()
