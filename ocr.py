import easyocr
import os
import cv2

# --- Paths ---
PROCESSED_DIR = "images/processed"

# Initialise EasyOCR once — loading it inside a loop would be very slow.
# gpu=False because neither machine has a supported GPU.
# 'en' is sufficient — European plates use Latin characters only.
print("Loading EasyOCR model...")
reader = easyocr.Reader(['en'], gpu=False)
print("Model ready.\n")

files = sorted(os.listdir(PROCESSED_DIR))
results = {}

for filename in files:
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue

    img_path = os.path.join(PROCESSED_DIR, filename)

    # Read the image and run OCR
    # detail=0 means return just the text strings, not bounding box coordinates
    detections = reader.readtext(img_path, detail=0)

    # Join multiple detected text regions into one string
    plate_text = " ".join(detections).strip()

    results[filename] = plate_text
    print(f"  {filename:40s}  →  {plate_text if plate_text else '(nothing detected)'}")

# Summary
print(f"\n--- Summary ---")
print(f"Images processed : {len(results)}")
detected = sum(1 for v in results.values() if v)
print(f"Text detected    : {detected}/{len(results)}")