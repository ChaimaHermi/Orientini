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
# CONSTANTES
# ---------------------------------------------------------------------
TUNISIAN_UNIS = [
    "تونس", "تونس المنار", "قرطاج", "منوبة", "جندوبة",
    "نابل", "سوسة", "صفاقس", "قابس", "قفصة", "المنستير",
    "القيروان", "سيدي بوزيد", "زغوان"
]

INSTITUTION_KEYWORDS = [
    "المعهد", "معهد",
    "الكلية", "كلية",
    "المدرسة العليا", "المدرسة"
]

# ---------------------------------------------------------------------
# NORMALISATION TEXTE SIMPLE
# ---------------------------------------------------------------------
def normalize_text(text: Optional[str]) -> str:
    if not text:
        return ""
    return re.sub(r"\s+", " ", text).strip()

# ---------------------------------------------------------------------
# NETTOYAGE DE L’INSTITUTION (SANS UNIVERSITÉ)
# ---------------------------------------------------------------------
def clean_institution(raw: str) -> str:
    if not raw:
        return "غير محدد"

    # Supprimer tout ce qui suit "جامعة"
    raw = re.split(r"جامعة", raw)[0]

    # Supprimer parenthèses cassées
    raw = raw.replace("(", "").replace(")", "")

    # Nettoyage espaces
    raw = re.sub(r"\s+", " ", raw).strip()

    return raw or "غير محدد"

# ---------------------------------------------------------------------
# DÉTECTION ROBUSTE DE L’UNIVERSITÉ MÈRE
# ---------------------------------------------------------------------
def clean_parent_university(raw: str) -> str:
    if not raw:
        return "غير محدد"

    # Normalisation des préfixes OCR
    raw = raw.replace("بـ", " ").replace("بال", " ").replace("ب", " ")

    # Déduction par la ville
    for city in TUNISIAN_UNIS:
        if city in raw:
            return f"جامعة {city}"

    # Fallback si "جامعة" existe
    if "جامعة" in raw:
        return "جامعة " + raw.split("جامعة")[-1].strip()

    return "غير محدد"

# ---------------------------------------------------------------------
# EXTRACTION UNIVERSITÉ + UNIVERSITÉ MÈRE
# ---------------------------------------------------------------------
def extract_parent_university(university_raw: str) -> Dict[str, str]:

    institution = clean_institution(university_raw)
    parent = clean_parent_university(university_raw)

    return {
        "university": institution,
        "parent_university": parent
    }

# ---------------------------------------------------------------------
# NETTOYAGE BAC
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

    return mapping.get(bac.strip(), bac.strip())

# ---------------------------------------------------------------------
# EXTRACTION DURÉE
# ---------------------------------------------------------------------
def extract_duration(text: str) -> Optional[str]:
    if not text:
        return None
    m = re.search(r"(\d+)\s*سنوات?", text)
    return f"{m.group(1)} سنوات" if m else None

# ---------------------------------------------------------------------
# RAG BLOCK
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
# TRANSFORMATION D’UNE ENTRÉE
# ---------------------------------------------------------------------
def transform_entry(entry: Dict[str, Any]) -> Dict[str, Any]:

    diploma_raw = normalize_text(entry.get("diploma"))
    speciality_raw = normalize_text(entry.get("speciality"))
    bac = clean_bac(entry.get("bac"))

    duration = (
        extract_duration(entry.get("periode", ""))
        or extract_duration(diploma_raw)
        or extract_duration(entry.get("exigence", ""))
        or "3 سنوات"
    )

    diploma = diploma_raw or "غير محدد"

    if duration == "9 سنوات" or "طب" in speciality_raw:
        diploma = "الطب"

    speciality = speciality_raw.replace("-", " - ") if speciality_raw else "غير محدد"

    uni = extract_parent_university(entry.get("university", ""))

    return {
        "code": entry.get("code"),
        "diploma": diploma,
        "university": uni["university"],
        "parent_university": uni["parent_university"],
        "speciality": speciality,
        "bac_section": bac,
        "formula": entry.get("formula") or "غير محدد",
        "min_score": round(entry["score"], 3) if entry.get("score") is not None else None,
        "duration": duration,
        "requirements": normalize_text(entry.get("exigence")) or None,
        "source_page": entry.get("page")
    }

# ---------------------------------------------------------------------
# MAIN
# ---------------------------------------------------------------------
def main():

    with open(INPUT_JSON, "r", encoding="utf-8") as f:
        raw_data = json.load(f)

    processed, rag_blocks, seen = [], [], set()

    for e in raw_data:
        key = (e.get("code"), e.get("bac"))
        if key in seen:
            continue
        seen.add(key)

        t = transform_entry(e)

        if t["code"] and t["min_score"] is not None:
            processed.append(t)
            rag_blocks.append(build_rag_block(t))

    processed.sort(key=lambda x: x["code"])

    with open(OUTPUT_JSON, "w", encoding="utf-8") as f:
        json.dump(processed, f, ensure_ascii=False, indent=2)

    with open(RAG_TEXT_FILE, "w", encoding="utf-8") as f:
        f.write("\n".join(rag_blocks))

    print(f"✅ DONE — {len(processed)} entrées traitées correctement")

# ---------------------------------------------------------------------
if __name__ == "__main__":
    main()
