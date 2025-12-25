from pathlib import Path
import pickle
import faiss
from sentence_transformers import SentenceTransformer

from .load_corpus import load_corpus
from .embed_corpus import embed_corpus
from .config import TOP_K, EMBEDDING_MODEL

BASE_DIR = Path(__file__).resolve().parents[4]
DATA_DIR = BASE_DIR / "data" / "processed"

INDEX_PATH = DATA_DIR / "faiss.index"
META_PATH = DATA_DIR / "faiss_meta.pkl"
CORPUS_PATH = DATA_DIR / "rag_corpus.txt"

model = SentenceTransformer(EMBEDDING_MODEL)


def get_faiss_index():
    if INDEX_PATH.exists() and META_PATH.exists():
        index = faiss.read_index(str(INDEX_PATH))
        with open(META_PATH, "rb") as f:
            corpus = pickle.load(f)
        return index, corpus

    corpus = load_corpus(CORPUS_PATH)
    embeddings = embed_corpus(corpus)

    dim = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)
    index.add(embeddings)

    faiss.write_index(index, str(INDEX_PATH))
    with open(META_PATH, "wb") as f:
        pickle.dump(corpus, f)

    return index, corpus


def search(query: str, top_k: int = TOP_K) -> list[str]:
    index, corpus = get_faiss_index()

    query_embedding = model.encode(
        [query],
        normalize_embeddings=True
    )

    _, indices = index.search(query_embedding, top_k)
    return [corpus[i] for i in indices[0]]
