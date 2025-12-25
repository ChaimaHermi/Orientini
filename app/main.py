from pathlib import Path
from dotenv import load_dotenv

# Charger le .env depuis la racine du projet
BASE_DIR = Path(__file__).resolve().parents[2]  # Orientini/
load_dotenv(BASE_DIR / ".env")
