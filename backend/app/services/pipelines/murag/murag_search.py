import faiss
import json
from .config import INDEX_PATH, METADATA_PATH
from .embed_entities import get_embedding_model
from .murag_index import build_murag_index

_index = None
_metadata = None


def load_index():
    global _index, _metadata

    if _index is not None and _metadata is not None:
        return

    # 🔁 Auto-build si index absent
    if not INDEX_PATH.exists() or not METADATA_PATH.exists():
        _index, _metadata = build_murag_index()
        return

    _index = faiss.read_index(str(INDEX_PATH))

    with open(METADATA_PATH, encoding="utf-8") as f:
        _metadata = json.load(f)


def search_entity(question: str, top_k: int = 5) -> list[dict]:
    """
    Recherche sémantique FAISS (search only, no business logic)
    """

    load_index()

    if not question or not question.strip():
        return []

    model = get_embedding_model()

    # ⚠️ même normalisation que le build
    query_vec = model.encode(
        [question],
        normalize_embeddings=True
    )

    k = min(top_k, len(_metadata))

    distances, indices = _index.search(query_vec, k)

    results = []

    for dist, idx in zip(distances[0], indices[0]):
        if idx < 0 or idx >= len(_metadata):
            continue

        entity = _metadata[idx].copy()
        entity["distance"] = float(dist)

        results.append(entity)

    # ✅ TRI EXPLICITE (distance croissante = meilleur)
    results.sort(key=lambda x: x["distance"])

    return results
