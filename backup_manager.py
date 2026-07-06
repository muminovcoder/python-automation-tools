import os
import shutil
import datetime
import json
from pathlib import Path
from typing import Optional

CONFIG_FILE = "backup_config.json"

DEFAULT_CONFIG = {
    "source_dirs": [],
    "backup_root": "backups",
    "max_backups": 10,
    "compress": False,
}


def load_config() -> dict:
    config_path = Path(CONFIG_FILE)
    if config_path.exists():
        return json.loads(config_path.read_text())
    return DEFAULT_CONFIG.copy()


def save_config(config: dict):
    Path(CONFIG_FILE).write_text(json.dumps(config, indent=2))
    print(f"Configuration saved to {CONFIG_FILE}")


def create_backup(source: str, backup_root: str, compress: bool = False) -> Optional[Path]:
    source_path = Path(source).resolve()
    if not source_path.exists():
        print(f"Source not found: {source}")
        return None
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_name = f"{source_path.name}_{timestamp}"
    backup_path = Path(backup_root) / backup_name
    if compress:
        archive_name = str(Path(backup_root) / backup_name)
        backup_path = Path(shutil.make_archive(archive_name, "zip", source_path))
        print(f"Compressed backup: {backup_path}")
    else:
        shutil.copytree(source_path, backup_path, dirs_exist_ok=True)
        print(f"Backup created: {backup_path}")
    return backup_path


def cleanup_old_backups(backup_root: str, max_backups: int):
    backup_dir = Path(backup_root)
    if not backup_dir.exists():
        return
    backups = sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True)
    for old_backup in backups[max_backups:]:
        if old_backup.is_dir():
            shutil.rmtree(old_backup)
        else:
            old_backup.unlink()
        print(f"Removed old backup: {old_backup.name}")


def list_backups(backup_root: str):
    backup_dir = Path(backup_root)
    if not backup_dir.exists():
        print("No backups found.")
        return
    print(f"\nBackups in {backup_root}:")
    for bp in sorted(backup_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True):
        size = bp.stat().st_size
        mtime = datetime.datetime.fromtimestamp(bp.stat().st_mtime).strftime("%Y-%m-%d %H:%M")
        size_str = f"{size / 1024:.1f} KB" if size < 1024 * 1024 else f"{size / (1024*1024):.1f} MB"
        print(f"  {bp.name} ({size_str}) - {mtime}")


def configure():
    config = load_config()
    print("Configure Backup Manager")
    sources = input("Source directories (comma separated): ").strip()
    if sources:
        config["source_dirs"] = [s.strip() for s in sources.split(",")]
    root = input(f"Backup root [{config['backup_root']}]: ").strip()
    if root:
        config["backup_root"] = root
    mx = input(f"Max backups [{config['max_backups']}]: ").strip()
    if mx.isdigit():
        config["max_backups"] = int(mx)
    compress = input("Compress backups? (y/N): ").strip().lower()
    config["compress"] = compress == "y"
    save_config(config)


def run_backup():
    config = load_config()
    if not config["source_dirs"]:
        print("No source directories configured. Run setup first.")
        return
    backup_root = Path(config["backup_root"])
    backup_root.mkdir(parents=True, exist_ok=True)
    for source in config["source_dirs"]:
        create_backup(source, config["backup_root"], config["compress"])
    cleanup_old_backups(config["backup_root"], config["max_backups"])


def main():
    print("=" * 50)
    print("  BACKUP MANAGER")
    print("=" * 50)
    print("  [1] Run backup now")
    print("  [2] Configure settings")
    print("  [3] List backups")
    choice = input("\nSelect (1-3): ").strip()
    if choice == "1":
        run_backup()
    elif choice == "2":
        configure()
    elif choice == "3":
        config = load_config()
        list_backups(config["backup_root"])
    else:
        print("Invalid choice.")


if __name__ == "__main__":
    main()
