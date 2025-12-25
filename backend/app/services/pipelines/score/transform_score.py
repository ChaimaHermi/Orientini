import json
import re
from pathlib import Path
from typing import Dict, Any, Optional

# ---------------------------------------------------------------------
# PATHS
# ---------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[4]
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_JSON = EXTRACTED_DIR / "structured_scores_2025.json"
OUTPUT_JSON = PROCESSED_DIR / "processed_scores_2025.json"
RAG_TEXT_FILE = PROCESSED_DIR / "rag_corpus.txt"

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------
# CONSTANTS
# ---------------------------------------------------------------------
TUNISIAN_UNIS = [
    "تونس", "تونس المنار", "قرطاج", "منوبة", "جندوبة",
    "نابل", "سوسة", "صفاقس", "قابس", "قفصة", "المنستير",
    "القيروان", "سيدي بوزيد", "زغوان"
]

INSTITUTION_KEYWORDS = [
    "معهد", "المعهد", "كلية", "الكلية", "المدرسة", "المدرسة العليا"
]

# ---------------------------------------------------------------------
# NORMALIZATION
# ---------------------------------------------------------------------
def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    text = re.sub(r"[()]", " ", text)
    text = re.sub(r"\s+", " ", text)
    return text.strip()

# ---------------------------------------------------------------------
# FIX REVERSED UNIVERSITY
# ---------------------------------------------------------------------
def fix_reversed_university(text: str) -> str:
    tokens = text.split()
    if not tokens:
        return text

    first = tokens[0]
    if first in TUNISIAN_UNIS:
        tokens = tokens[1:]
        for i, t in enumerate(tokens):
            if any(t.startswith(k) for k in INSTITUTION_KEYWORDS):
                institution = " ".join(tokens[i:])
                return f"{institution} جامعة {first}"
    return text

# ---------------------------------------------------------------------
# CLEAN BAC
# ---------------------------------------------------------------------
def clean_bac(bac: Optional[str]) -> str:
    if not bac:
        return "غير محدد"

    mapping = {
        "علوم تجريبية": "علوم تجريبية",
        "علوم الإعلامية": "علوم إعلامية",
        "علوم اإلعالمية": "علوم إعلامية",
        "اقتصاد و تصرف": "اقتصاد وتصرف",
        "إقتصاد وتصرف": "اقتصاد وتصرف",
        "رياضيات": "رياضيات",
        "آداب": "آداب",
        "بادآ": "آداب",
        "علوم تقنية": "علوم تقنية",
        "العلوم التقنية": "علوم تقنية",
    }
    bac = bac.strip()
    return mapping.get(bac, bac)

# ---------------------------------------------------------------------
# EXTRACT DURATION
# ---------------------------------------------------------------------
def extract_duration(text: str) -> Optional[str]:
    m = re.search(r"(\d+)\s*سنوات?", text)
    return f"{m.group(1)} سنوات" if m else None

# ---------------------------------------------------------------------
# UNIVERSITY EXTRACTION
# ---------------------------------------------------------------------
def extract_parent_university(university_raw: str) -> Dict[str, str]:
    text = normalize_text(university_raw)
    text = fix_reversed_university(text)

    if not text:
        return {
            "university": "غير محدد",
            "parent_university": "غير محدد"
        }

    parent = None
    institution = None

    m = re.search(r"جامعة\s+([^\s]+)", text)
    if m:
        parent = "جامعة " + m.group(1)

    for kw in INSTITUTION_KEYWORDS:
        if kw in text:
            institution = text[text.index(kw):]
            break

    if not parent:
        for g in TUNISIAN_UNIS:
            if g in text:
                parent = "جامعة " + g
                break

    if institution and parent:
        institution = institution.replace(parent, "").strip()

    return {
        "university": institution or "غير محدد",
        "parent_university": parent or "غير محدد"
    }

# ---------------------------------------------------------------------
# BUILD RAG TEXT BLOCK
# ---------------------------------------------------------------------
def build_rag_block(entry: Dict[str, Any]) -> str:
    return (
        "###\n"
        f"التكوين: {entry['diploma']}\n"
        f"الاختصاص: {entry['speciality']}\n"
        f"المؤسسة: {entry['university']}\n"
        f"الجامعة: {entry['parent_university']}\n"
        f"شعبة الباكالوريا: {entry['bac_section']}\n"
        f"المدة: {entry['duration']}\n"
        f"معدل القبول الأدنى: {entry['min_score']}\n"
        f"صيغة الاحتساب: {entry['formula']}\n"
        f"شروط إضافية: {entry['requirements'] or 'لا يوجد'}\n"
    )

# ---------------------------------------------------------------------
# TRANSFORM ENTRY
# ---------------------------------------------------------------------
def transform_entry(entry: Dict[str, Any], diploma_override: Optional[str]) -> Dict[str, Any]:

    diploma_raw = normalize_text(entry.get("diploma"))
    university_raw = normalize_text(entry.get("university"))
    speciality_raw = normalize_text(entry.get("speciality"))
    bac = clean_bac(entry.get("bac"))
    code = entry.get("code")
    formula = entry.get("formula") or "غير محدد"
    score = entry.get("score")
    periode = normalize_text(entry.get("periode", ""))
    req_raw = normalize_text(entry.get("exigence", ""))

    duration = (
        extract_duration(periode)
        or extract_duration(diploma_raw)
        or extract_duration(req_raw)
        or "3 سنوات"
    )

    if diploma_override:
        diploma = diploma_override
    elif diploma_raw and not extract_duration(diploma_raw):
        diploma = diploma_raw
    else:
        diploma = "غير محدد"

    if duration == "9 سنوات" or "طب" in speciality_raw:
        diploma = "الطب"

    if "خاص باإلناث" in diploma_raw:
        diploma = "الإجازة في علوم التوليد - قابلة"
        speciality = "علوم التوليد - قابلة"
    else:
        speciality = speciality_raw.replace("-", " - ").strip() if speciality_raw else "غير محدد"

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
        "requirements": req_raw or None,
        "source_page": entry.get("page")
    }

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    music_codes = {
        e["code"]
        for e in raw_data
        if "موسيقى" in normalize_text(e.get("speciality"))
    }

    processed = []
    seen = set()
    rag_blocks = []

    for e in raw_data:
        key = (e.get("code"), e.get("bac"))
        if key in seen:
            continue
        seen.add(key)

        diploma_override = (
            "الإجازة في الموسيقى والعلوم الموسيقية"
            if e["code"] in music_codes else None
        )

        t = transform_entry(e, diploma_override)

        if t["code"] and t["min_score"] is not None:
            processed.append(t)
            rag_blocks.append(build_rag_block(t))

    processed.sort(key=lambda x: x["code"])

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    with open(RAG_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(rag_blocks))

    print(f"✅ DONE — JSON: {len(processed)} entries | RAG corpus generated")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
