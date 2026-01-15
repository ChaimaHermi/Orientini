import faiss
from pathlib import Path
import json
from .embed_entities import get_embedding_model
from .config import DATA_DIR, INDEX_PATH, METADATA_PATH


def build_murag_index():
    """
    Construit l'index FAISS MuRAG à partir de entities.json
    """
    entities_path = DATA_DIR / "entities.json"

    if not entities_path.exists():
        raise RuntimeError("❌ entities.json introuvable pour MuRAG")

    with open(entities_path, encoding="utf-8") as f:
        entities = json.load(f)

    texts = []
    metadata = []

    for entity in entities:
        text = (
            f"{entity.get('name_ar','')} "
            f"{entity.get('name_fr','')} "
            f"{entity.get('university_ar','')} "
            f"{entity.get('description_ar','')}"
        )

        texts.append(text)
        metadata.append({
            "id": entity["id"],
            "name_ar": entity.get("name_ar"),
            "university_ar": entity.get("university_ar"),
            "city": entity.get("city")
        })

    model = get_embedding_model()
    embeddings = model.encode(texts, convert_to_numpy=True)

    index = faiss.IndexFlatL2(embeddings.shape[1])
    index.add(embeddings)

    DATA_DIR.mkdir(parents=True, exist_ok=True)

    faiss.write_index(index, str(INDEX_PATH))

    with open(METADATA_PATH, "w", encoding="utf-8") as f:
        json.dump(metadata, f, ensure_ascii=False, indent=2)

    return index, metadata
