from pathlib import Path
import pdfplumber
import json
import warnings
import sys
from io import StringIO
import re

warnings.filterwarnings("ignore")

# Chemins
BASE_DIR = Path(__file__).resolve().parents[4]
RAW_DIR = BASE_DIR / "data" / "raw"
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"

PDF_FILE = "guide_scores_2025.pdf"
OUTPUT_FILE = "structured_scores_2025.json"

pdf_path = RAW_DIR / PDF_FILE
output_path = EXTRACTED_DIR / OUTPUT_FILE

structured_data = []

# Suppression des warnings pdfplumber
old_stderr = sys.stderr
sys.stderr = StringIO()

def clean_and_reverse(text):
    """Nettoie et reverse le texte arabe correctement"""
    if not text:
        return ""
    text = text.strip()
    if any('\u0600' <= c <= '\u06FF' for c in text):
        return text[::-1]
    return text

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}")
        
        for page_num in range(39, len(pdf.pages)):  # À partir de la page 40
            page = pdf.pages[page_num]
            tables = page.extract_tables()
            
            if not tables:
                continue
                
            for table in tables:
                if len(table) < 3:
                    continue
                
                previous = [""] * 7
                current_diploma = ""      # Nom classique de l'إجازة
                current_preparatory = ""  # Nom du cycle préparatoire (ex: مرحلة تحضيرية مندمجة...)
                
                for row in table:
                    if row is None:
                        continue
                    
                    # Normalisation à 7 colonnes
                    if len(row) > 7:
                        row = row[:7]
                    elif len(row) < 7:
                        row += [""] * (7 - len(row))
                    
                    # Nettoyage et reverse arabe
                    cleaned_row = []
                    for cell in row:
                        cell_text = "" if cell is None else str(cell).strip()
                        cleaned_row.append(clean_and_reverse(cell_text))
                    
                    # Fill down des cellules mergées
                    for j in range(7):
                        if cleaned_row[j]:
                            previous[j] = cleaned_row[j]
                        else:
                            cleaned_row[j] = previous[j]
                    
                    diploma_raw = cleaned_row[6]
                    
                    # Détection d'un nouveau cycle préparatoire intégré
                    if any(keyword in diploma_raw for keyword in ["مرحلة تحضيرية", "مندمجة", "فيزياء - كيمياء", "العلمية", "Préparatoire"]):
                        current_preparatory = diploma_raw.strip()
                        continue  # Ce n'est pas une ligne de données
                    
                    # Mise à jour du diploma normal
                    if (diploma_raw and 
                        not re.search(r'سن[تو]ان\s*\+\s*3', diploma_raw) and
                        "(امد)" not in diploma_raw and
                        not any(k in diploma_raw for k in ["إجبارية", "اختبار", "تطلب"])):
                        current_diploma = diploma_raw.strip()
                    
                    # Skip des en-têtes
                    if any(kw in " ".join(cleaned_row) for kw in ["مجموع نقاط", "صيغة احتساب", "الشعبة", "المؤسسة", "الرمز", "الجامعة", "الشهادة"]):
                        continue
                    
                    # Validation du code (5 chiffres)
                    code = cleaned_row[3].strip()
                    if not re.fullmatch(r'\d{5}', code):
                        continue
                    
                    # Validation du score
                    score_str = cleaned_row[0].replace(",", ".")
                    if score_str in ['', '-']:
                        continue
                    try:
                        score = float(score_str)
                    except ValueError:
                        continue
                    
                    # Gestion spéciale des cycles préparatoires
                    if current_preparatory and re.search(r'سن[تو]ان\s*\+\s*3', diploma_raw):
                        diploma = current_preparatory
                        periode = "سنتان +3 سنوات"
                    else:
                        diploma = current_diploma or None
                        periode = None
                    
                    # Extraction période et exigences (sécurisée contre None)
                    exigences = []
                    raw_diploma_cell = row[6]  # Cellule brute pour éviter None après nettoyage
                    if raw_diploma_cell:
                        diploma_lines = [l.strip() for l in str(raw_diploma_cell).split('\n') if l.strip()]
                        for line in diploma_lines:
                            rev_line = clean_and_reverse(line)
                            if re.search(r'\d+\s*سنوات?', rev_line) or '(امد)' in line:
                                periode = rev_line
                            elif any(word in rev_line for word in ['اختبار', 'إجبارية', 'تطلب', 'تربية بدنية']):
                                exigences.append(rev_line)
                    
                    # University
                    university_raw = cleaned_row[5].replace('\n', ' ').strip()
                    university = " ".join(university_raw.split())
                    
                    # Speciality
                    speciality_raw = cleaned_row[4].replace('\n', ' - ').strip()
                    speciality = " ".join(speciality_raw.split())
                    
                    entry = {
                        "diploma": diploma,
                        "university": university,
                        "speciality": speciality if speciality else None,
                        "code": code,
                        "bac": cleaned_row[2],
                        "formula": cleaned_row[1],
                        "score": score,
                        "page": page_num + 1,
                        "periode": periode,
                        "exigence": '، '.join(exigences) if exigences else None
                    }
                    structured_data.append(entry)

finally:
    sys.stderr = old_stderr

# Sauvegarde
with open(output_path, 'w', encoding='utf-8') as f:
    json.dump(structured_data, f, ensure_ascii=False, indent=4)

print(f"Extraction terminée : {len(structured_data)} entrées sauvegardées dans {output_path}")