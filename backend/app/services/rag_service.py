from app.services.orchestrator.intent_classifier import detect_intent
from app.services.pipelines.rag.pipeline_rag import rag_pipeline
from app.services.pipelines.murag.pipeline_murag import murag_pipeline


class RagService:

    @staticmethod
    def ask(question: str) -> dict:
        print("\n==============================")
        print("🟣 RagService.ask")
        print("QUESTION:", question)

        # ✅ CORRECT : unpack intent + scores
        intent, scores = detect_intent(question)

        print("🎯 DETECTED INTENT:", intent)
        print("📊 SCORES:", scores)

        # -----------------------------
        # 🖼️ IMAGES SEULEMENT
        # -----------------------------
        if intent == "IMAGE_ONLY":
            print("➡️ MODE IMAGE_ONLY ACTIVÉ")

            murag_result = murag_pipeline(question)

            return {
                "answer": "🖼️ إليك صور المؤسسة المطلوبة:",
                "images": murag_result.get("images", {})
            }

        # -----------------------------
        # 📝 TEXTE SEULEMENT
        # -----------------------------
        if intent == "TEXT_ONLY":
            print("➡️ MODE TEXT_ONLY ACTIVÉ")

            answer = rag_pipeline(question)

            return {
                "answer": answer,
                "images": {}
            }

        # -----------------------------
        # 🔀 TEXTE + IMAGES
        # -----------------------------
        print("➡️ MODE TEXT_AND_IMAGES ACTIVÉ")

        murag_result = murag_pipeline(question)
        answer = rag_pipeline(question)

        return {
            "answer": answer,
            "images": murag_result.get("images", {})
        }
