import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

from .config import (
    GEMINI_MODEL,
    LLM_TEMPERATURE,
    LLM_MAX_OUTPUT_TOKENS
)

# ======================================================
# Charger le fichier .env depuis la racine du projet
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[5]  # Orientini/
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# ======================================================
# Configuration Gemini
# ======================================================
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        f"GOOGLE_API_KEY non trouvée. Vérifiez le fichier {ENV_PATH}"
    )

genai.configure(api_key=API_KEY)


def llm_answer(question: str, context: str) -> str:
    """
    Génère une réponse en arabe naturel, de type assistant d’orientation,
    sans format technique (JSON, listes, champs).
    """
    prompt = f"""
    أنت مستشار توجيه جامعي في تونس.

    السؤال:
    {question}

    المهمة:
    - فهم السؤال بدقة.
    - استخراج فقط التكوينات المطابقة تمامًا للسؤال.
    - إعادة صياغة الجواب بلغة عربية واضحة وبأسلوب إرشادي إنساني.
    - تخيّل أنك تشرح لطالب حائر بعد الباكالوريا.

    قواعد صارمة:
    - لا تذكر أي تكوين غير مطابق لشعبة السؤال.
    - لا تستنتج ولا تضف معلومات غير موجودة في السياق.
    - يمكنك الربط بين المعلومات وشرح العلاقة بينها فقط إذا كانت العلاقة مذكورة صراحة في السياق.
    - إذا كان السؤال يتطلب استنتاجًا غير مذكور صراحة في السياق، يجب الامتناع عن الإجابة.
    - لا تستعمل أي تنسيق تقني (لا JSON، لا نقط، لا تعداد).
    - لا تذكر أسماء الحقول مثل "التكوين" أو "المؤسسة".
    - أجب باللغة العربية فقط.

    أسلوب الإجابة المطلوب:
    - لغة طبيعية وسلسة.
    - صياغة تفسيرية مثل: "توجد"، "يمكنك"، "من بين الإمكانيات".
    - ذكر عدد الإمكانيات إن أمكن.
    - ذكر المؤسسات والجامعات بشكل سردي.
    - لا تبدأ بمقدمة طويلة أو عبارات عاطفية زائدة.
    - التفسير يجب أن يكون مبنيًا فقط على إعادة صياغة المعطيات الموجودة دون تعميم أو افتراض.
    - إذا كان السؤال يتعلق بصيغة الاحتساب أو معدل القبول، اكتفِ بشرح الصيغة المذكورة في السياق دون مقارنة أو استنتاج.

    في حالة عدم وجود أي تكوين مطابق:
    أجب حرفيًا:
    "لا تتوفر معطيات كافية للإجابة عن هذا السؤال."

    السياق المتوفر:
    {context}

    الإجابة النهائية:
    """

    model = genai.GenerativeModel(GEMINI_MODEL)

    response = model.generate_content(
        prompt,
        generation_config={
            "temperature": LLM_TEMPERATURE,
            "max_output_tokens": LLM_MAX_OUTPUT_TOKENS
        }
    )

    if hasattr(response, "text") and response.text:
        return response.text.strip()

    return "لا تتوفر معطيات كافية للإجابة عن هذا السؤال."
