import numpy as np
from sentence_transformers import SentenceTransformer
from .config import EMBEDDING_MODEL

model = SentenceTransformer(EMBEDDING_MODEL)


def embed_corpus(chunks: list[str]) -> np.ndarray:
    embeddings = model.encode(
        chunks,
        normalize_embeddings=True,
        show_progress_bar=True
    )
    return embeddings.astype("float32")
