"""
copy_images.py
--------------
Script to copy game images from the website folder to the bot's images folder.
This ensures the bot has all images for the expanded 200 games list.

Run this script ONCE to set up the images directory.
"""

import os
import shutil
from pathlib import Path

# Source directories (website images)
SOURCE_PG_SOFT = Path(r"D:\WORK PROGRAM\rtp-main\TEST-RTP-BARU-2\images\PG SOFT")
SOURCE_PRAGMATIC = Path(r"D:\WORK PROGRAM\rtp-main\TEST-RTP-BARU-2\images\Pragmatic Play")

# Destination directory (bot images)
SCRIPT_DIR = Path(__file__).parent
DEST_DIR = SCRIPT_DIR / "images"

def copy_images():
    """Copy all .webp images from source directories to destination."""
    
    # Create destination directory if it doesn't exist
    DEST_DIR.mkdir(exist_ok=True)
    
    copied_count = 0
    skipped_count = 0
    
    print("=" * 60)
    print("📁 COPYING GAME IMAGES TO BOT FOLDER")
    print("=" * 60)
    
    # Copy PG SOFT images
    print(f"\n🎰 Copying PG SOFT images from: {SOURCE_PG_SOFT}")
    if SOURCE_PG_SOFT.exists():
        for img_file in SOURCE_PG_SOFT.glob("*.webp"):
            dest_file = DEST_DIR / img_file.name
            if not dest_file.exists():
                shutil.copy2(img_file, dest_file)
                copied_count += 1
                print(f"   ✅ Copied: {img_file.name}")
            else:
                skipped_count += 1
    else:
        print(f"   ⚠️ Source directory not found!")
    
    # Copy Pragmatic Play images
    print(f"\n🎲 Copying Pragmatic Play images from: {SOURCE_PRAGMATIC}")
    if SOURCE_PRAGMATIC.exists():
        for img_file in SOURCE_PRAGMATIC.glob("*.webp"):
            dest_file = DEST_DIR / img_file.name
            if not dest_file.exists():
                shutil.copy2(img_file, dest_file)
                copied_count += 1
                print(f"   ✅ Copied: {img_file.name}")
            else:
                skipped_count += 1
    else:
        print(f"   ⚠️ Source directory not found!")
    
    print("\n" + "=" * 60)
    print(f"📊 SUMMARY:")
    print(f"   • Images copied: {copied_count}")
    print(f"   • Images skipped (already exist): {skipped_count}")
    print(f"   • Total images in folder: {len(list(DEST_DIR.glob('*.webp')))}")
    print("=" * 60)


if __name__ == "__main__":
    copy_images()

