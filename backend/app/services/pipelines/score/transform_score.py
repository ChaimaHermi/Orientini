from pathlib import Path
import json
import re
from typing import List, Dict, Any, Optional

# ------------------------------------------------------------------
# Chemins
# ------------------------------------------------------------------
BASE_DIR = Path(__file__).resolve().parents[4]
EXTRACTED_DIR = BASE_DIR / "data" / "extracted"
PROCESSED_DIR = BASE_DIR / "data" / "processed"

INPUT_JSON = "structured_scores_2025.json"
OUTPUT_JSON = "processed_scores_2025.json"

input_path = EXTRACTED_DIR / INPUT_JSON
output_path = PROCESSED_DIR / OUTPUT_JSON

PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

def normalize_text(text: str) -> str:
    if not text:
        return ""
    text = text.strip()
    text = " ".join(text.split())
    text = text.replace("ةعماج(", "(جامعة ").replace(")(", ") (")
    return text

def clean_bac(bac: str) -> str:
    mapping = {
        "علوم تجريبية": "علوم تجريبية",
        "إقتصاد وتصرف": "اقتصاد وتصرف",
        "فرصتو داصتقإ": "اقتصاد وتصرف",
        "رياضيات": "رياضيات",
        "العلوم التقنية": "علوم تقنية",
        "علوم اإلعالمية": "علوم إعلامية",
        "علوم الإعلامية": "علوم إعلامية",
        "بادآ": "آداب",
        "ةيبيرجت مولع": "علوم تجريبية",
        "ةيملاعلإا مولع": "علوم إعلامية",
    }
    return mapping.get(bac.strip(), bac.strip())

def extract_duration(text: str) -> Optional[str]:
    """استخراج المدة مثل '9 سنوات' أو '6 سنوات' من نص"""
    match = re.search(r'(\d+)\s*سنوات?', text)
    if match:
        return f"{match.group(1)} سنوات"
    return None

def is_requirement(text: str) -> bool:
    """تحديد إذا كان النص متطلبًا (يتضمن كلمات مثل السن، اختبار، إجبارية...)"""
    if not text:
        return False
    text_lower = text.lower()
    requirement_keywords = [
        "سن القصوى", "أقل من", "أكثر من", "غرة سبتمبر",
        "اختبار", "إجبارية", "تطلب", "تربية بدنية", "مقابلة", "حد أقصى",
        "شروط", "السن", "العمر", "في غرة", "إجباري", "علوم الحياة"
    ]
    return any(keyword in text_lower for keyword in requirement_keywords)

def extract_parent_university(university_raw: str) -> Dict[str, str]:
    university = normalize_text(university_raw)
    
    match_open = re.search(r'\(جامعة\s*([^\(\)]+)', university)
    if match_open:
        parent = "جامعة " + match_open.group(1).strip()
        university_clean = re.sub(r'\(جامعة\s*[^\(\)]+', '', university).strip("() ")
        return {"university": university_clean or None, "parent_university": parent}
    
    match_closed = re.search(r'\(\s*جامعة\s*([^\(\)]+)\s*\)', university)
    if match_closed:
        parent = "جامعة " + match_closed.group(1).strip()
        university_clean = re.sub(r'\(\s*جامعة\s*[^\(\)]+\s*\)', '', university).strip()
        return {"university": university_clean or None, "parent_university": parent}
    
    if "(جامعة" in university and ")" in university:
        parts = university.split("(جامعة")
        if len(parts) >= 2:
            before = parts[0].strip()
            after = parts[1].strip()
            parent_part = after.split(")")[0].strip()
            parent = "جامعة " + parent_part
            university_clean = before.strip("() ")
            return {"university": university_clean or None, "parent_university": parent}
    
    return {"university": university or None, "parent_university": None}

def transform_entry(entry: Dict[str, Any]) -> Dict[str, Any]:
    diploma_raw = normalize_text(entry.get("diploma", ""))
    university_raw = normalize_text(entry.get("university", ""))
    speciality_raw = normalize_text(entry.get("speciality", ""))
    code = entry.get("code", "").strip()
    bac = clean_bac(entry.get("bac", ""))
    formula = entry.get("formula", "").strip()
    score = entry.get("score")
    periode_raw = normalize_text(entry.get("periode", ""))
    requirements_raw = normalize_text(entry.get("exigence", "")) if entry.get("exigence") else ""

    # ------------------ استخراج المدة (duration) ------------------
    duration = None
    
    # 1. من عمود periode أولاً
    if periode_raw:
        duration = extract_duration(periode_raw)
    
    # 2. إذا لم توجد، من diploma
    if not duration and diploma_raw:
        duration = extract_duration(diploma_raw)
    
    # 3. إذا لم توجد، من requirements
    if not duration and requirements_raw:
        duration = extract_duration(requirements_raw)
    
    # إذا لم نجد مدة → افتراضي 3 سنوات (للإجازة العادية)
    if not duration:
        duration = "3 سنوات"

    # ------------------ معالجة diploma ------------------
    if diploma_raw:
        # إذا كان diploma هو فقط المدة أو متطلب → diploma = None
        if extract_duration(diploma_raw) or is_requirement(diploma_raw):
            diploma = None
            # نقل المحتوى إلى requirements
            if requirements_raw:
                requirements = requirements_raw + "، " + diploma_raw
            else:
                requirements = diploma_raw
        else:
            diploma = diploma_raw if not ("الشعبة" in diploma_raw or "/" in diploma_raw) else None
            requirements = requirements_raw
    else:
        diploma = None
        requirements = requirements_raw

    # ------------------ تنظيف requirements من المدة ------------------
    if duration != "3 سنوات" and requirements:
        # إزالة المدة من requirements إذا كانت موجودة
        requirements = re.sub(r'\d+\s*سنوات?', '', requirements)
        requirements = re.sub(r'،\s*,', '،', requirements)  # تنظيف فواصل زائدة
        requirements = requirements.strip("، ").strip()
        if not requirements:
            requirements = None

    # ------------------ باقي الحقول ------------------
    uni_dict = extract_parent_university(university_raw)
    university = uni_dict["university"]
    parent_university = uni_dict["parent_university"]

    if speciality_raw:
        speciality_raw = speciality_raw.replace(";", " - ").replace(" ; ", " - ")
        speciality = " - ".join([s.strip() for s in speciality_raw.split("-") if s.strip()])
    else:
        speciality = None

    return {
        "code": code,
        "diploma": diploma,
        "university": university,
        "parent_university": parent_university,
        "speciality": speciality,
        "bac_section": bac,
        "formula": formula,
        "min_score": round(score, 3) if score is not None else None,
        "duration": duration,
        "requirements": requirements,
        "source_page": entry.get("page")
    }

def main():
    if not input_path.exists():
        print(f"الملف غير موجود: {input_path}")
        return

    print(f"قراءة {input_path}")
    with open(input_path, 'r', encoding='utf-8') as f:
        raw_data: List[Dict] = json.load(f)

    print(f"{len(raw_data)} مدخلة محملة.")

    seen = set()
    processed_data = []

    for entry in raw_data:
        key = (entry.get("code"), entry.get("bac"))
        if key in seen:
            continue
        seen.add(key)

        transformed = transform_entry(entry)
        if transformed["code"] and transformed["min_score"] is not None:
            processed_data.append(transformed)

    processed_data.sort(key=lambda x: x["code"])

    print(f"{len(processed_data)} مدخلة نهائية.")

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(processed_data, f, ensure_ascii=False, indent=2)

    print(f"تم الحفظ في: {output_path}")

    # تحقق من الأمثلة المشكلة
    print("\n--- تصحيح الطب والصيدلة (مدة 9 و6 سنوات) ---")
    for ex in processed_data:
        if ex["code"] in ["10700", "34701"]:
            print(f"Code: {ex['code']} | Bac: {ex['bac_section']}")
            print(f"   duration: {ex['duration']}")
            print(f"   requirements: {ex['requirements'] or 'لا يوجد'}")
            print()

if __name__ == "__main__":
    main()