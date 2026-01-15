from pathlib import Path

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / "data" / "murag"

INDEX_PATH = DATA_DIR / "faiss.index"
METADATA_PATH = DATA_DIR / "metadata.json"
