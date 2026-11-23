"""
create_submission_zip.py - Package all screening task files for FOSSEE submission
"""
import zipfile
import os
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
OUTPUT_ZIP = BASE_DIR / "OsdagBridge_Screening_Submission.zip"

print(f"Creating submission zip at: {OUTPUT_ZIP}")

with zipfile.ZipFile(OUTPUT_ZIP, "w", zipfile.ZIP_DEFLATED) as zf:
    for root, dirs, files in os.walk(BASE_DIR):
        # Exclude git objects and cache directories
        if ".git" in root or "__pycache__" in root or ".pytest_cache" in root:
            continue
        for f in files:
            if f.endswith(".zip"):
                continue
            full_path = Path(root) / f
            arc_name = full_path.relative_to(BASE_DIR)
            zf.write(full_path, arc_name)

print(f"ZIP created successfully! Size: {os.path.getsize(OUTPUT_ZIP) / (1024*1024):.2f} MB")
