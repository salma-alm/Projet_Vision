import re

GROUND_FILE = "annotations/ground.txt"
OCR_FILE = "ocr_results.txt"


def normalize(text):
    text = text.upper()
    text = re.sub(r'[^A-Z0-9]', '', text)
    return text


ground_truth = {}

with open(GROUND_FILE, "r", encoding="utf-8") as f:
    for line in f:

        line = line.strip()

        if not line:
            continue

        filename, plate = line.split(",", 1)

        ground_truth[filename.strip()] = normalize(
            plate.strip()
        )


ocr_results = {}

with open(OCR_FILE, "r", encoding="utf-8") as f:
    for line in f:

        line = line.strip()

        if "->" not in line:
            continue

        filename, plate = line.split("->", 1)

        ocr_results[filename.strip()] = normalize(
            plate.strip()
        )


total = len(ground_truth)
detected = 0
exact_matches = 0

print("\n--- Evaluation ---\n")

for filename, expected in ground_truth.items():

    predicted = ocr_results.get(filename, "")

    if predicted:
        detected += 1

    correct = expected == predicted

    if correct:
        exact_matches += 1

    status = "OK" if correct else "FAIL"

    print(
        f"{status:5s} | "
        f"{filename:30s} | "
        f"Expected: {expected:12s} | "
        f"Got: {predicted}"
    )

print("\n--- Summary ---")

print(f"Images total      : {total}")
print(f"Text detected     : {detected}")
print(f"Exact matches     : {exact_matches}")

if total > 0:
    print(
        f"Detection rate    : "
        f"{100 * detected / total:.2f}%"
    )

    print(
        f"Exact accuracy    : "
        f"{100 * exact_matches / total:.2f}%"
    )