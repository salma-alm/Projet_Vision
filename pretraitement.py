import cv2
import os

# --- Paths ---
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

    # Load the cropped plate
    image = cv2.imread(in_path)
    if image is None:
        print(f"  SKIP {filename} — could not read")
        continue

    # Step 1: Resize to a standard height while keeping proportions.
    # EasyOCR performs better when text is a reasonable size.
    # We standardise to 100px tall — most plates are wider than tall.
    target_h = 100
    h, w = image.shape[:2]
    scale   = target_h / h
    resized = cv2.resize(image, (int(w * scale), target_h))

    # Step 2: Convert to grayscale.
    # Colour information is irrelevant for reading text.
    # This reduces the image from 3 channels (BGR) to 1 channel.
    gray = cv2.cvtColor(resized, cv2.COLOR_BGR2GRAY)

    # Step 3: Increase contrast using histogram equalisation.
    # This spreads out pixel intensity values so dark images become
    # more readable and overexposed images lose their glare.
    equalized = cv2.equalizeHist(gray)

    # Step 4: Adaptive thresholding — convert to pure black and white.
    # Unlike simple thresholding (one global cutoff), adaptive thresholding
    # calculates the cutoff locally for each region of the image.
    # This handles uneven lighting across the plate much better.
    thresh = cv2.adaptiveThreshold(
        equalized, 255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY,
        11, 2
    )

    # Step 5: Median blur to remove small noise specks.
    # A 3x3 kernel is small enough to not blur the actual text.
    cleaned = cv2.medianBlur(thresh, 3)

    # Save the processed image
    cv2.imwrite(out_path, cleaned)
    print(f"  OK {filename}")

print(f"\nDone. Processed images saved to {PROCESSED_DIR}/")