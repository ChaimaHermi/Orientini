import os
import google.generativeai as genai
from dotenv import load_dotenv
from pathlib import Path

# Charger explicitement le .env
PROJECT_ROOT = Path(__file__).resolve().parent
load_dotenv(PROJECT_ROOT / ".env")

print("GOOGLE_API_KEY chargée ?", bool(os.getenv("GOOGLE_API_KEY")))

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

# CORRECTION DU NOM DU MODÈLE ICI
model = genai.GenerativeModel("gemini-2.5-flash")
try:
    r = model.generate_content("أجب بكلمة واحدة: مرحبا")
    print(r.text.strip())
except Exception as e:
    print(f"Une erreur est survenue lors de l'appel API: {e}")