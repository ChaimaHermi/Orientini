# =========================
# Recherche vectorielle
# =========================
TOP_K = 6  
# ⬆️ On réduit légèrement le contexte pour laisser PLUS de tokens
# à Gemini pour terminer sa réponse (ce n’est PAS un filtre métier)

# =========================
# Embeddings
# =========================
EMBEDDING_MODEL = "paraphrase-multilingual-MiniLM-L12-v2"

# =========================
# LLM Gemini
# =========================
USE_LLM = True
LLM_PROVIDER = "gemini"
GEMINI_MODEL = "gemini-2.5-flash"

LLM_TEMPERATURE = 0.2

# ⬇️ CLÉ DU PROBLÈME : marge large pour réponses narratives
LLM_MAX_OUTPUT_TOKENS = 4096
