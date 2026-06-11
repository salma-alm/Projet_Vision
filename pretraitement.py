import cv2
import os
import numpy as np

CROPPED_DIR   = "images/cropped"
PROCESSED_DIR = "images/processed"

os.makedirs(PROCESSED_DIR, exist_ok=True)

files = os.listdir(CROPPED_DIR)
print(f"Processing {len(files)} cropped images...")

for filename in files:
    if not filename.lower().endswith((".jpg", ".jpeg", ".png", ".webp")):
        continue

    in_path  = os.path.join(CROPPED_DIR, filename)
    out_path = os.path.join(PROCESSED_DIR, filename)

    image = cv2.imread(in_path)
    if image is None:
        print(f"  SKIP {filename} — could not read")
        continue

    # Step 1: Resize to standard height
    target_h = 100
    h, w = image.shape[:2]
    scale   = target_h / h
    resized = cv2.resize(image, (int(w * scale), target_h),
                         interpolation=cv2.INTER_CUBIC)
    # INTER_CUBIC is smoother than default when upscaling small plates

    # Step 2: Crop the bottom 15% of the image.
    # German and some European plates have a registration/city strip
    # along the bottom edge. This is not part of the plate number
    # and confuses OCR heavily. We remove it preemptively.
    h2, w2 = resized.shape[:2]
    resized = resized[0:int(h2 * 0.85), 0:w2]

    # Step 2b: Crop the left edge — removes the EU country rectangle
    # (blue strip with country code and stars) which OCR reads as H or E.
    # European plates consistently have this strip occupying roughly
    # the leftmost 10-12% of the plate width.
    h2, w2 = resized.shape[:2]
    left_crop = int(w2 * 0.12)
    resized = resized[0:h2, left_crop:w2]

    # Step 3: Grayscale
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Step 4: Denoise BEFORE thresholding.
    # Previously we denoised after — but noise fools the threshold
    # calculation. Doing it first gives a cleaner threshold result.
    # h=10 is the filter strength — higher = more smoothing but
    # risks blurring thin characters.
    denoised = cv2.fastNlMeansDenoising(gray, h=10)

    # Step 5: Contrast enhancement via CLAHE.
    # Better than plain equalizeHist — CLAHE (Contrast Limited Adaptive
    # Histogram Equalisation) enhances contrast locally without
    # over-brightening already bright regions (like glare spots).
    # clipLimit controls how aggressively it enhances — 2.0 is balanced.
    clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
    enhanced = clahe.apply(denoised)

    # Step 6: Adaptive threshold
    thresh = cv2.adaptiveThreshold(
        enhanced, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        15, 8
        # blockSize 15 (was 11) — looks at a larger neighbourhood,
        # better for larger characters
        # C=8 (was 2) — subtracts more from the mean, reduces noise
        # being misread as text strokes
    )

    # Step 7: Morphological opening — removes small isolated noise spots
    # that survived thresholding. The kernel size (2,2) is deliberately
    # small so it doesn't erode actual character strokes.
    kernel  = np.ones((2, 2), np.uint8)
    cleaned = cv2.morphologyEx(thresh, cv2.MORPH_OPEN, kernel)

    cv2.imwrite(out_path, cleaned)
    print(f"  OK {filename}")

print(f"\nDone. Processed images saved to {PROCESSED_DIR}/")