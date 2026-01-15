import os
from pathlib import Path
from dotenv import load_dotenv
import google.generativeai as genai

# ======================================================
# Configuration projet
# ======================================================
BASE_DIR = Path(__file__).resolve().parents[3]  # backend/
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)

# ======================================================
# Paramètres LLM (tu peux les déplacer dans config.py)
# ======================================================
GEMINI_MODEL = "gemini-1.5-flash"
LLM_TEMPERATURE = 0.0
LLM_MAX_OUTPUT_TOKENS = 20

# ======================================================
# Configuration Gemini
# ======================================================
API_KEY = os.getenv("GOOGLE_API_KEY")

if not API_KEY:
    raise RuntimeError(
        f"GOOGLE_API_KEY non trouvée. Vérifie le fichier {ENV_PATH}"
    )

genai.configure(api_key=API_KEY)

model = genai.GenerativeModel(
    model_name=GEMINI_MODEL,
    generation_config={
        "temperature": LLM_TEMPERATURE,
        "max_output_tokens": LLM_MAX_OUTPUT_TOKENS,
    }
)

# ======================================================
# Fonction publique utilisée par l’orchestrateur
# ======================================================
def llm_complete(question: str) -> str:
    """
    Analyse l’intention de la question utilisateur.

    Retourne STRICTEMENT une des valeurs :
    - IMAGE_ONLY
    - TEXT_ONLY
    - TEXT_AND_IMAGES
    """

    prompt = f"""
Tu es un classificateur d’intention.

Analyse la question suivante et retourne UNIQUEMENT
une des valeurs suivantes (sans explication) :

- IMAGE_ONLY : si l’utilisateur demande des images / photos
- TEXT_ONLY : si l’utilisateur demande une explication texte
- TEXT_AND_IMAGES : si les deux sont demandés

Question :
{question}

Réponse attendue (un seul mot) :
"""

    try:
        response = model.generate_content(prompt)
        intent = response.text.strip().upper()

        if intent not in ["IMAGE_ONLY", "TEXT_ONLY", "TEXT_AND_IMAGES"]:
            return "TEXT_ONLY"

        return intent

    except Exception as e:
        # Sécurité : ne jamais casser l’app à cause du LLM
        print("[LLM ERROR]", e)
        return "TEXT_ONLY"
