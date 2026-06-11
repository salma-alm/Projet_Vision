import json
import cv2
import os

# --- Paths ---
JSON_PATH    = "annotations/instances_Train.json"
RAW_DIR      = "images/raw"
CROPPED_DIR  = "images/cropped"

# Create output folder if it doesn't exist yet
os.makedirs(CROPPED_DIR, exist_ok=True)

# --- Load the full annotation file ---
with open(JSON_PATH, "r") as f:
    data = json.load(f)

# --- Build a lookup: filename -> image_id ---
# The JSON stores images and annotations separately.
# We need to link them: image filename -> image_id -> bounding box.
filename_to_id = {}
for img in data["images"]:
    filename_to_id[img["file_name"]] = img["id"]

# --- Build a lookup: image_id -> list of bounding boxes ---
# One image can have multiple plates (e.g. two cars visible).
# We take the largest bbox per image — most likely the main plate.
id_to_bboxes = {}
for ann in data["annotations"]:
    iid = ann["image_id"]
    if iid not in id_to_bboxes:
        id_to_bboxes[iid] = []
    id_to_bboxes[iid].append(ann["bbox"])

# --- Process each image in images/raw/ ---
raw_files = os.listdir(RAW_DIR)
print(f"Found {len(raw_files)} images in {RAW_DIR}")

for filename in raw_files:
    # Only process image files
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue

    # Check this image exists in the JSON
    if filename not in filename_to_id:
        print(f"  SKIP {filename} — not found in annotations")
        continue

    image_id = filename_to_id[filename]

    # Check this image has bounding boxes
    if image_id not in id_to_bboxes:
        print(f"  SKIP {filename} — no bounding box in annotations")
        continue

    # Load the image
    img_path = os.path.join(RAW_DIR, filename)
    image = cv2.imread(img_path)
    if image is None:
        print(f"  SKIP {filename} — could not read image file")
        continue

    # Pick the largest bounding box (by area) as the main plate
    bboxes = id_to_bboxes[image_id]
    bbox = max(bboxes, key=lambda b: b[2] * b[3])  # width * height

    # bbox format from COCO is [x, y, width, height] — all floats
    x, y, w, h = bbox
    x, y, w, h = int(x), int(y), int(w), int(h)

    # Add a small padding around the crop so we don't cut off edges
    pad = 5
    img_h, img_w = image.shape[:2]
    x1 = max(0, x - pad)
    y1 = max(0, y - pad)
    x2 = min(img_w, x + w + pad)
    y2 = min(img_h, y + h + pad)

    # Crop the plate region
    crop = image[y1:y2, x1:x2]

    # Save to images/cropped/ with same filename
    out_path = os.path.join(CROPPED_DIR, filename)
    cv2.imwrite(out_path, crop)
    print(f"  OK {filename} — plate cropped {w}x{h}px")

print(f"\nDone. Cropped plates saved to {CROPPED_DIR}/")