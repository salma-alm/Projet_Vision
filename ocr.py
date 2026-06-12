import warnings
warnings.filterwarnings("ignore")

import easyocr
import os
import re

PROCESSED_DIR = "images/processed"
OUTPUT_FILE = "ocr_results.txt"

print("Loading EasyOCR model...")
reader = easyocr.Reader(['en'], gpu=False)
print("Model ready.\n")


# Known European plate format patterns.
# Each is a regex that matches the plate number after cleaning.
# These cover the most common formats — German, French, Spanish,
# Italian, Dutch, Belgian, Polish, Czech, Portuguese, Swiss.
# We don't try to be exhaustive — the goal is to catch obvious garbage,
# not to validate every edge case.

PLATE_PATTERNS = [
    # German: 1-3 letters, 1-2 letters, 1-4 digits
    # e.g. "WUG U 533", "DA F 9684", "BUS E 7844"
    (r'^[A-Z]{1,3}[\s\-]?[A-Z]{1,2}[\s\-]?\d{1,4}$', 'German'),

    # French: 2 letters, 3 digits, 2 letters (post-2009)
    # e.g. "AB 123 CD"
    (r'^[A-Z]{2}[\s\-]?\d{3}[\s\-]?[A-Z]{2}$', 'French'),

    # Spanish: 4 digits, 3 letters
    # e.g. "1234 BCD"
    (r'^\d{4}[\s\-]?[A-Z]{3}$', 'Spanish'),

    # Italian: 2 letters, 3 digits, 2 letters
    # e.g. "AB 123 CD"
    (r'^[A-Z]{2}[\s\-]?\d{3}[\s\-]?[A-Z]{2}$', 'Italian'),

    # Dutch: 2 letters, 2 digits, 2 letters or variations
    # e.g. "AB 12 CD", "12 AB 34"
    (r'^[A-Z0-9]{2}[\s\-]?[A-Z0-9]{2}[\s\-]?[A-Z0-9]{2}$', 'Dutch/Belgian'),

    # Polish: 2-3 letters, 4-5 alphanumeric
    # e.g. "WS DM 9230"
    (r'^[A-Z]{2,3}[\s\-]?[A-Z]{1,2}[\s\-]?\d{3,5}$', 'Polish/Czech'),

    # Generic fallback: 2-8 alphanumeric characters total
    # Catches valid-looking plates that don't fit named formats
    (r'^[A-Z0-9][\s\-]?[A-Z0-9]{1,7}$', 'Generic'),
]


def validate_plate(text):
    """
    Check if cleaned plate text matches any known European format.
    Returns (is_valid, format_name).
    
    We test against the text with spaces/hyphens removed for matching,
    since spacing varies by country and OCR often drops or adds spaces.
    Never rejects — only classifies confidence.
    """
    # Remove spaces and hyphens for pattern matching
    compact = re.sub(r'[\s\-]', '', text)

    for pattern, name in PLATE_PATTERNS:
        # Test both the spaced version and compact version
        if re.match(pattern, text) or re.match(pattern, compact):
            return True, name

    return False, 'Unknown'


def clean_plate(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9\s\-]', '', text)
    text = re.sub(r'\s+', ' ', text).strip()
    return text


def filter_detections(detections):
    filtered = []
    for (bbox, text, confidence) in detections:
        # Skip low-confidence detections
        if confidence < 0.3:
            continue

        cleaned = re.sub(r'[^A-Z0-9\-]', '', text.upper())

        # Skip single characters that are likely clutter symbols
        # Real plate groups are always 2+ characters
        if len(cleaned) < 2:
            continue

        bbox_width  = abs(bbox[1][0] - bbox[0][0])
        bbox_height = abs(bbox[2][1] - bbox[0][1])
        if bbox_height > 0 and bbox_width / bbox_height < 0.3:
            continue

        # Get the leftmost x coordinate of this detection's bounding box
        # bbox is [[x1,y1],[x2,y1],[x2,y2],[x1,y2]]
        left_x = bbox[0][0]
        filtered.append((left_x, cleaned))

    # Sort left to right — fixes reversed output ordering
    filtered.sort(key=lambda x: x[0])

    return [text for (_, text) in filtered]


files = sorted(os.listdir(PROCESSED_DIR))
results = {}
confidences = {}

for filename in files:
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue

    img_path = os.path.join(PROCESSED_DIR, filename)

    raw_detections = reader.readtext(
        img_path,
        detail=1,
        allowlist='ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789 -'
    )

    tokens     = filter_detections(raw_detections)
    raw_text   = ' '.join(tokens)
    plate_text = clean_plate(raw_text)

    is_valid, fmt = validate_plate(plate_text)
    results[filename]     = plate_text
    confidences[filename] = (is_valid, fmt)

    # Build the output line
    status = f"[{fmt}]" if is_valid else "[? unrecognised format]"
    output = plate_text if plate_text else "(nothing detected)"
    print(f"  {filename:40s}  →  {output:20s}  {status}")

	
with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
    for filename, plate in results.items():
        f.write(f"{filename} -> {plate}\n")
print(f"\nOCR results saved to {OUTPUT_FILE}")

# Summary
print(f"\n--- Summary ---")
total    = len(results)
detected = sum(1 for v in results.values() if v)
valid    = sum(1 for v in confidences.values() if v[0])
print(f"Images processed     : {total}")
print(f"Text detected        : {detected}/{total}")
print(f"Format recognised    : {valid}/{total}")
print(f"Uncertain (flagged)  : {detected - valid}/{total}")