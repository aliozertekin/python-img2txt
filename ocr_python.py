import os
from pdf2image import convert_from_path
from PIL import Image
import easyocr
import numpy as np

# --- Configuration ---
POPPLER_PATH = r"C:/poppler/bin"  # ⚠️ Change this to your Poppler bin path
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

# Initialize OCR reader with Turkish language (you can change to 'en' or ['tr', 'en'] for both)
reader = easyocr.Reader(['tr'], gpu=False)

# Define named regions (x1, y1, x2, y2) based on 300 DPI A4 size (2480x3508 px)
REGIONS = [
    ("Header",     (100,  100, 2380, 300)),     # Top of the page
    ("Main Info",  (100,  500, 2380, 1200)),    # Center of the page
    ("Footer",     (100, 3200, 2380, 3400))     # Bottom of the page
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Process all PDF files in the input folder
for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".pdf"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        base_name = os.path.splitext(filename)[0]

        print(f"[INFO] Processing '{filename}'...")

        # Convert PDF pages to images
        pages = convert_from_path(filepath, dpi=300, poppler_path=POPPLER_PATH)
        all_text = []

        for i, page in enumerate(pages):
            img_np = np.array(page)
            all_text.append(f"\n--- Page {i + 1} ---\n")

            # Extract each defined region
            for label, (x1, y1, x2, y2) in REGIONS:
                region = img_np[y1:y2, x1:x2]
                text_lines = reader.readtext(region, detail=0, paragraph=True)
                region_text = "\n".join(text_lines).strip()
                all_text.append(f"[{label}]\n{region_text}\n")

        # Write all text to a single output file
        output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}.txt")
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(all_text))

        print(f"[✓] Output saved: {output_path}")
