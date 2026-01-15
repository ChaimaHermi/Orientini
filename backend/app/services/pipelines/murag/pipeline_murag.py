from app.services.pipelines.murag.murag_search import search_entity
from app.services.pipelines.murag.image_map import IMAGE_MAP


def murag_pipeline(question: str) -> dict:
    """
    Pipeline MuRAG FINAL – sans hallucinations
    """

    if not question or not question.strip():
        return {"entities": [], "images": {}}

    # 1️⃣ Recherche FAISS (large)
    entities = search_entity(question, top_k=5)

    print("DEBUG ENTITIES FOUND:", entities)

    if not entities:
        return {"entities": [], "images": {}}

    # 2️⃣ 🎯 RÈGLE ABSOLUE : nom explicite → 1 seule entité
    selected_entity = None

    for e in entities:
        name_ar = e.get("name_ar", "").strip()
        if name_ar and name_ar in question:
            selected_entity = e
            break

    # 3️⃣ Fallback : meilleure entité seulement
    if selected_entity is None:
        selected_entity = entities[0]

    entities = [selected_entity]

    # 4️⃣ Mapping images (APRÈS filtrage)
    images = {}

    entity_id = selected_entity.get("id")
    if entity_id in IMAGE_MAP:
        images[entity_id] = IMAGE_MAP[entity_id]

    return {
        "entities": entities,
        "images": images
    }
