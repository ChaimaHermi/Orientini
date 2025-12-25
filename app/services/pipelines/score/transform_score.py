import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[4]
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_JSON = EXTRACTED_DIR / "structured_scores_2025.json"
OUTPUT_JSON = PROCESSED_DIR / "processed_scores_2025.json"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# Liste des universités tunisiennes
TUNISIAN_UNIS = [
    "تونس", "تونس المنار", "قرطاج", "منوبة", "جندوبة",
    "نابل", "سوسة", "صفاقس", "قابس", "قفصة", "المنستير",
    "القيروان", "سيدي بوزيد", "زغوان"
]

# Institutions keywords
INSTITUTION_KEYWORDS = ["معهد", "المعهد", "كلية", "الكلية", "المدرسة", "المدرسة العليا"]


# ---------------------------------------------------------------------
# Normalisation du texte
# ---------------------------------------------------------------------
def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = re.sub(r"[()]", " ", text)
    return " ".join(text.split()).strip()


# ---------------------------------------------------------------------
# Correction des universités inversées
# ---------------------------------------------------------------------
def fix_reversed_university(text: str) -> str:
    """
    Corrige les cas où le gouvernorat apparaît avant l’institution :
    Exemple :
        'منوبة معهد الصحافة وعلوم الأخبار جامعة'
    devient :
        'معهد الصحافة وعلوم الأخبار جامعة منوبة'
    """
    tokens = text.split()
    if not tokens:
        return text

    first = tokens[0]
    if first in TUNISIAN_UNIS:
        # Remove governorate from the start
        tokens = tokens[1:]

        # Find institution beginning
        for i, t in enumerate(tokens):
            if any(t.startswith(k) for k in INSTITUTION_KEYWORDS):
                institution = " ".join(tokens[i:])
                parent = f"جامعة {first}"
                return f"{institution} {parent}"

    return text


# ---------------------------------------------------------------------
# Nettoyage Bac
# ---------------------------------------------------------------------
def clean_bac(bac: str) -> str:
    mapping = {
        "علوم تجريبية": "علوم تجريبية",
        "علوم الإعلامية": "علوم إعلامية",
        "علوم اإلعلامية": "علوم إعلامية",
        "إقتصاد وتصرف": "اقتصاد وتصرف",
        "اقتصاد و تصرف": "اقتصاد وتصرف",
        "رياضيات": "رياضيات",
        "آداب": "آداب",
        "بادآ": "آداب",
        "العلوم التقنية": "علوم تقنية",
    }
    return mapping.get(bac.strip(), bac.strip())


# ---------------------------------------------------------------------
# Extract Duration
# ---------------------------------------------------------------------
def extract_duration(text: str) -> Optional[str]:
    m = re.search(r"(\d+)\s*سنوات?", text)
    return f"{m.group(1)} سنوات" if m else None


# ---------------------------------------------------------------------
# Check if text is requirement
# ---------------------------------------------------------------------
def is_requirement(text: str) -> bool:
    keywords = ["اختبار", "إجبار", "سن", "العمر", "مقابلة", "شروط", "يجب"]
    t = text.lower().replace("،", " ")
    return any(k in t for k in keywords)


# ---------------------------------------------------------------------
# Extraction robuste parent_university + university
# ---------------------------------------------------------------------
def extract_parent_university(university_raw: str) -> Dict[str, str]:
    text = normalize_text(university_raw)

    # Fix reversed forms
    text = fix_reversed_university(text)

    if not text:
        return {"university": None, "parent_university": None}

    parent = None
    institution = None

    # 1️⃣ Detect explicit "جامعة X"
    m = re.search(r"جامعة\s+([^\s]+)", text)
    if m:
        parent = "جامعة " + m.group(1).strip()

    # 2️⃣ Detect institution
    for kw in INSTITUTION_KEYWORDS:
        if kw in text:
            # Keep only what comes after the keyword
            idx = text.index(kw)
            institution = text[idx:]
            break

    # 3️⃣ Infer parent from governorate if missing
    if not parent:
        for g in TUNISIAN_UNIS:
            if g in text:
                parent = "جامعة " + g
                break

    # 4️⃣ Final cleanup
    if institution:
        institution = institution.replace(parent or "", "").strip()

    return {
        "university": institution or None,
        "parent_university": parent
    }


# ---------------------------------------------------------------------
# Transform entry
# ---------------------------------------------------------------------
def transform_entry(entry: Dict[str, Any], diploma_override: Optional[str]) -> Dict[str, Any]:

    diploma_raw = normalize_text(entry.get("diploma"))
    university_raw = normalize_text(entry.get("university"))
    speciality_raw = normalize_text(entry.get("speciality"))
    bac = clean_bac(entry.get("bac"))
    code = entry.get("code")
    formula = entry.get("formula")
    score = entry.get("score")
    periode = normalize_text(entry.get("periode", ""))
    req_raw = normalize_text(entry.get("exigence", ""))

    # Duration
    duration = extract_duration(periode) or extract_duration(diploma_raw) or extract_duration(req_raw)
    duration = duration or "3 سنوات"

    # BASE diploma handling
    if diploma_override:
        diploma = diploma_override
    else:
        if diploma_raw and diploma_raw != "الإجازة / الشعبة" and not extract_duration(diploma_raw):
            diploma = diploma_raw
        else:
            diploma = None

    # SPECIAL RULE 1 : الموسيقى
    if diploma_raw == "الإجازة / الشعبة" and speciality_raw and "موسيقى" in speciality_raw:
        diploma = "الإجازة في الموسيقى والعلوم الموسيقية"

    # SPECIAL RULE 2 : الطب
    if (duration == "9 سنوات") or (speciality_raw and "طب" in speciality_raw):
        diploma = "الإجازة في الطب"

    # SPECIAL RULE 3 : القابلة
    if diploma_raw and "خاص باإلناث" in diploma_raw:
        diploma = "الإجازة في علوم التوليد - قابلة"
        speciality = "علوم التوليد - قابلة"
    else:
        # Normal speciality
        speciality = None
        if speciality_raw:
            speciality = " - ".join([s.strip() for s in speciality_raw.split("-") if s.strip()])

    # Requirements
    requirements = req_raw or None

    # University
    uni = extract_parent_university(university_raw)

    return {
        "code": code,
        "diploma": diploma,
        "university": uni["university"],
        "parent_university": uni["parent_university"],
        "speciality": speciality,
        "bac_section": bac,
        "formula": formula,
        "min_score": round(score, 3) if score is not None else None,
        "duration": duration,
        "requirements": requirements,
        "source_page": entry.get("page")
    }


# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    # Detect codes belonging to music specialities
    music_codes = {e["code"] for e in raw_data if "موسيقى" in normalize_text(e.get("speciality"))}

    processed = []
    seen = set()

    for e in raw_data:
        key = (e.get("code"), e.get("bac"))
        if key in seen:
            continue
        seen.add(key)

        # If code is music → override diploma
        diploma_override = "الإجازة في الموسيقى والعلوم الموسيقية" if e["code"] in music_codes else None

        t = transform_entry(e, diploma_override)
        if t["code"] and t["min_score"] is not None:
            processed.append(t)

    processed.sort(key=lambda x: x["code"])

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    print("✅ DONE. Total:", len(processed))


if __name__ == "__main__":
    main()
