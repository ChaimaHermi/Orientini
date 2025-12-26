from .pipelines.rag.pipeline_rag import rag_pipeline


class RagService:

    @staticmethod
    def ask(question: str) -> str:
        """
        Appelle le cœur RAG sans exposer sa complexité
        """
        return rag_pipeline(question)
