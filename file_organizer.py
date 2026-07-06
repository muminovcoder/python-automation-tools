import os
import shutil
from pathlib import Path

FILE_CATEGORIES = {
    "Images": [".jpg", ".jpeg", ".png", ".gif", ".bmp", ".svg", ".webp", ".ico", ".tiff"],
    "Documents": [".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx", ".odt", ".txt", ".md", ".csv"],
    "Videos": [".mp4", ".mkv", ".avi", ".mov", ".wmv", ".flv", ".webm"],
    "Audio": [".mp3", ".wav", ".flac", ".aac", ".ogg", ".wma"],
    "Archives": [".zip", ".rar", ".tar", ".gz", ".7z", ".bz2"],
    "Code": [".py", ".js", ".ts", ".jsx", ".tsx", ".html", ".css", ".scss", ".json", ".xml", ".yaml", ".yml", ".sql"],
    "Executables": [".exe", ".msi", ".bat", ".sh", ".dmg", ".app"],
    "Fonts": [".ttf", ".otf", ".woff", ".woff2", ".eot"],
}


def organize_directory(directory: str, dry_run: bool = False):
    path = Path(directory).resolve()
    if not path.exists():
        print(f"Directory not found: {directory}")
        return
    organized_count = 0
    skipped_count = 0
    for item in path.iterdir():
        if item.is_dir():
            continue
        ext = item.suffix.lower()
        target_category = None
        for category, extensions in FILE_CATEGORIES.items():
            if ext in extensions:
                target_category = category
                break
        if not target_category:
            target_category = "Others"
        target_dir = path / target_category
        if dry_run:
            print(f"[DRY RUN] {item.name} -> {target_category}/")
            organized_count += 1
            continue
        target_dir.mkdir(exist_ok=True)
        dest = target_dir / item.name
        counter = 1
        while dest.exists():
            stem = item.stem
            dest = target_dir / f"{stem}_{counter}{ext}"
            counter += 1
        shutil.move(str(item), str(dest))
        print(f"Moved: {item.name} -> {target_category}/{dest.name}")
        organized_count += 1
    print(f"\nDone! Organized {organized_count} files. Skipped {skipped_count} directories.")


def main():
    print("=" * 50)
    print("  FILE ORGANIZER")
    print("=" * 50)
    target = input("Enter directory path (default: current): ").strip()
    if not target:
        target = "."
    dry_run_input = input("Dry run? (y/N): ").strip().lower()
    dry_run = dry_run_input == "y"
    organize_directory(target, dry_run)


if __name__ == "__main__":
    main()
