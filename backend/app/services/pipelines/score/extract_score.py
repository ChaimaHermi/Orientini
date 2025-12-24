from pathlib import Path
import pdfplumber
import json
import warnings
import sys
from io import StringIO
import re

warnings.filterwarnings("ignore")

BASE_DIR = Path(__file__).resolve().parents[4]
RAW_DIR = BASE_DIR / "data" / "raw"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"

PDF_FILE = "guide_scores_2025.pdf"
OUTPUT_FILE = "structured_scores_2025.json"

pdf_path = RAW_DIR / PDF_FILE
output_path = EXTRACTED_DIR / OUTPUT_FILE

structured_data = []

old_stderr = sys.stderr
sys.stderr = StringIO()

def clean_and_reverse(text):
    """Clean and properly reverse Arabic text from RTL PDF"""
    if not text:
        return ""
    text = text.strip()
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return text[::-1]
    return text

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for page_num in range(39, len(pdf.pages)):  # Start from page 40
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if not tables:
                continue
                
            for table in tables:
                if len(table) < 5:
                    continue
                
                previous = [""] * 7
                current_diploma = ""
                
                for row in table:
                    if row is None:
                        continue
                    
                    # Ensure exactly 7 columns
                    if len(row) > 7:
                        row = row[:7]
                    elif len(row) < 7:
                        row += [""] * (7 - len(row))
                    
                    # Clean each cell and reverse Arabic properly
                    cleaned_row = []
                    for cell in row:
                        cell_text = "" if cell is None else cell.strip()
                        cleaned_row.append(clean_and_reverse(cell_text))
                    
                    # Fill down merged cells
                    for j in range(7):
                        if cleaned_row[j]:
                            previous[j] = cleaned_row[j]
                        else:
                            cleaned_row[j] = previous[j]
                    
                    # Update current diploma when a new full diploma appears
                    diploma_col = cleaned_row[6]
                    if diploma_col and not diploma_col.startswith("3 سنوات") and "(امد)" not in diploma_col and not any(k in diploma_col for k in ["إجبارية", "اختبار", "تطلب"]):
                        current_diploma = diploma_col
                    
                    # Skip header rows
                    if any(kw in " ".join(cleaned_row) for kw in ["مجموع نقاط", "صيغة احتساب", "الشعبة", "المؤسسة", "الرمز", "الجامعة", "الشهادة"]):
                        continue
                    
                    # Validate code: must be exactly 5 digits
                    code = cleaned_row[3].strip()
                    if not re.fullmatch(r'\d{5}', code):
                        continue
                    
                    # Validate score
                    score_str = cleaned_row[0].replace(",", ".")
                    if score_str in ['', '-']:
                        continue
                    try:
                        score = float(score_str)
                    except ValueError:
                        continue
                    
                    # Clean university
                    university = " ".join(cleaned_row[5].split())
                    
                    # Clean speciality - multiple lines
                    raw_speciality = row[4]  # Use raw row[4] before cleaning
                    speciality_cell = "" if raw_speciality is None else raw_speciality
                    speciality_lines = [clean_and_reverse(l.strip()) for l in speciality_cell.split('\n') if l.strip()]
                    speciality = " - ".join(speciality_lines)
                    
                    # Extract periode and exigences safely from raw diploma column
                    periode = None
                    exigences = []
                    raw_diploma_cell = row[6]  # Use raw cell to avoid None
                    if raw_diploma_cell:
                        diploma_lines = [l.strip() for l in raw_diploma_cell.split('\n') if l.strip()]
                        for raw_line in diploma_lines:
                            rev_line = clean_and_reverse(raw_line)
                            if re.search(r'سنوات?\b', rev_line) or '(امد)' in raw_line:
                                periode = rev_line
                            elif any(word in rev_line for word in ['اختبار', 'إجبارية', 'تطلب', 'تربية بدنية']):
                                exigences.append(rev_line)
                    
                    entry = {
                        "diploma": current_diploma.strip(),
                        "university": university.strip(),
                        "speciality": speciality.strip(),
                        "code": code,
                        "bac": cleaned_row[2].strip(),
                        "formula": cleaned_row[1].strip(),
                        "score": score,
                        "page": page_num + 1,
                        "periode": periode,
                        "exigence": '، '.join(exigences) if exigences else None
                    }
                    
                    structured_data.append(entry)

finally:
    sys.stderr = old_stderr

# Save to JSON
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=4)

print(f"\nExtraction completed: {len(structured_data)} records saved to {output_path}")

if structured_data:
    print("\n--- First 10 examples ---")
    for i, ex in enumerate(structured_data[:10], 1):
        print(f"{i}. Diploma: {ex['diploma']}")
        print(f"   University: {ex['university']}")
        print(f"   Speciality: {ex['speciality']}")
        print(f"   Code: {ex['code']} | Score: {ex['score']} | Periode: {ex['periode']}")
        print(f"   Exigence: {ex['exigence']}\n")