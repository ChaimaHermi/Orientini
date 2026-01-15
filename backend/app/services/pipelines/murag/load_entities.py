import json
from .config import DATA_DIR

def load_entities():
    with open(DATA_DIR / "entities.json", encoding="utf-8") as f:
        return json.load(f)
