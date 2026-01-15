from sentence_transformers import SentenceTransformer, util
from typing import Dict, Tuple

# =====================================================
# Load model once
# =====================================================
model = SentenceTransformer(
    "paraphrase-multilingual-MiniLM-L12-v2"
)

# =====================================================
# Intent examples
# =====================================================
INTENT_EXAMPLES = {
    "TEXT_ONLY": [
        "اعطني معلومات عن المعهد",
        "اشرح لي هذه الجامعة",
        "ما هو المعهد العالي للفنون",
        "أريد معرفة تفاصيل عن الجامعة",
        "عرفني بالجامعة",
        "اشرح التخصصات"
    ],
    "IMAGE_ONLY": [
        "اعطني صور للمعهد",
        "اريد مشاهدة الحرم الجامعي",
        "صور الجامعة من الداخل",
        "أرني شكل المعهد",
        "صور الكلية",
        "اعطني صور"
    ],
    "TEXT_AND_IMAGE": [
        "اعطني معلومات مع صور",
        "اشرح المعهد وارني صور له",
        "معلومات مدعومة بصور عن الجامعة",
        "تفاصيل عن المعهد مع صور"
    ]
}

# =====================================================
# Pre-encode intent examples (performance)
# =====================================================
INTENT_EMBEDDINGS = {
    intent: model.encode(examples, convert_to_tensor=True)
    for intent, examples in INTENT_EXAMPLES.items()
}

# =====================================================
# Intent detection (FINAL LOGIC)
# =====================================================
def detect_intent(
    question: str,
    min_confidence: float = 0.45,
    min_gap: float = 0.08,
    image_prefer_gap: float = 0.03
) -> Tuple[str, Dict[str, float]]:
    """
    Détection d'intention robuste et orientée utilisateur.

    Règles :
    - score trop faible → TEXT_ONLY
    - IMAGE_ONLY prioritaire si proche du meilleur score
    - ambiguïté → TEXT_AND_IMAGE
    """

    if not question or not question.strip():
        return "TEXT_ONLY", {}

    question_emb = model.encode(question, convert_to_tensor=True)

    scores: Dict[str, float] = {}

    for intent, intent_embs in INTENT_EMBEDDINGS.items():
        similarity = util.cos_sim(question_emb, intent_embs)
        scores[intent] = similarity.max().item()

    # Trier les scores
    sorted_scores = sorted(
        scores.items(),
        key=lambda x: x[1],
        reverse=True
    )

    best_intent, best_score = sorted_scores[0]
    second_intent, second_score = sorted_scores[1]

    # -------------------------------------------------
    # 1️⃣ Confiance trop faible → texte seulement
    # -------------------------------------------------
    if best_score < min_confidence:
        return "TEXT_ONLY", scores

    # -------------------------------------------------
    # 2️⃣ PRIORITÉ IMAGES
    # Si IMAGE_ONLY est très proche du meilleur score,
    # on force IMAGE_ONLY (comportement humain)
    # -------------------------------------------------
    image_score = scores.get("IMAGE_ONLY", 0.0)

    if best_intent != "IMAGE_ONLY":
        if (best_score - image_score) <= image_prefer_gap:
            return "IMAGE_ONLY", scores

    # -------------------------------------------------
    # 3️⃣ Ambiguïté réelle → mixte
    # -------------------------------------------------
    if best_score - second_score < min_gap:
        return "TEXT_AND_IMAGE", scores

    # -------------------------------------------------
    # 4️⃣ Cas clair
    # -------------------------------------------------
    return best_intent, scores
