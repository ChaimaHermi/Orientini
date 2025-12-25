import fitz
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
RAW_DIR = BASE_DIR / "data" / "raw"
PDF_FILE = "guide_scores_2025.pdf"

def debug_page(page_number=40):
    pdf_path = RAW_DIR / PDF_FILE
    doc = fitz.open(pdf_path)
    page = doc[page_number - 1]

    blocks = page.get_text("blocks")

    print(f"=== DEBUG PAGE {page_number} ===")
    for x0, y0, x1, y1, text, *_ in blocks:
        text = text.strip()
        if text:
            print(f"x0={x0:.1f}  y0={y0:.1f}  →  {text}")

if __name__ == "__main__":
    debug_page(40)
