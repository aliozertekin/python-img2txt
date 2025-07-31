import os
from pdf2image import convert_from_path
from PIL import Image
import easyocr
import numpy as np

# Set up
POPPLER_PATH = r"C:/poppler/bin"  # ← change this to your Poppler /bin path
INPUT_FOLDER = "input"
OUTPUT_FOLDER = "output"

reader = easyocr.Reader(['tr'], gpu=False)

# Define your ROIs (relative to A4 @ 300dpi ~ 2480x3508)
# Format: (label, (x1, y1, x2, y2)) -- coordinates in pixels
REGIONS = [
    ("Header",     (100,  100, 2380, 300)),     # top section
    ("Main Info",  (100,  500, 2380, 1200)),    # middle block
    ("Footer",     (100, 3200, 2380, 3400))     # bottom block
]

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

for filename in os.listdir(INPUT_FOLDER):
    if filename.lower().endswith(".pdf"):
        filepath = os.path.join(INPUT_FOLDER, filename)
        base_name = os.path.splitext(filename)[0]

        print(f"[INFO] Processing {filename}...")

        # Convert PDF to images (one per page)
        pages = convert_from_path(filepath, dpi=300, poppler_path=POPPLER_PATH)

        for i, page in enumerate(pages):
            img_np = np.array(page)

            ocr_result = []

            for label, (x1, y1, x2, y2) in REGIONS:
                region = img_np[y1:y2, x1:x2]
                text_lines = reader.readtext(region, detail=0, paragraph=True)
                section_text = f"--- {label} ---\n" + "\n".join(text_lines) + "\n"
                ocr_result.append(section_text)

            # Save text output per page
            output_path = os.path.join(OUTPUT_FOLDER, f"{base_name}_page{i+1}.txt")
            with open(output_path, "w", encoding="utf-8") as f:
                f.write("\n".join(ocr_result))

        print(f"[DONE] Output saved in: {OUTPUT_FOLDER}/{base_name}_pageX.txt")
