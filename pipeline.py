import subprocess
import sys

steps = [
    ("Cropping plates from annotations...", "crop.py"),
    ("Preprocessing cropped images...",     "pretraitement.py"),
    ("Running OCR...",                       "ocr.py"),
    ("Evaluating OCR results...", "evaluate.py"),
]

for message, script in steps:
    print(f"\n{'='*50}")
    print(f" {message}")
    print(f"{'='*50}")
    result = subprocess.run([sys.executable, script])
    if result.returncode != 0:
        print(f"\nERROR: {script} failed. Stopping pipeline.")
        sys.exit(1)

print("\n Pipeline complete.")