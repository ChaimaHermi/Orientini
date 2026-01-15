from bson import ObjectId
from datetime import datetime

from app.services.rag_service import RagService
from app.models.message import Message
from app.models.conversation import Conversation
from app.utils.conversation_utils import generate_conversation_title


class ConversationService:

    def __init__(self, db):
        self.conversations = db.conversations
        self.messages = db.messages

    # ==================================================
    # ASK (RAG + MuRAG)
    # ==================================================
    def ask(
        self,
        user_id: str,
        question: str,
        conversation_id: str | None = None
    ):
        # 🆕 Nouvelle conversation
        if not conversation_id or conversation_id == "default":
            conversation_title = generate_conversation_title(question)

            conversation = Conversation(
                user_id=user_id,
                title=conversation_title,
                created_at=datetime.utcnow()
            )

            result = self.conversations.insert_one(
                conversation.dict(exclude={"id"}, exclude_none=True)
            )
            conversation_id = str(result.inserted_id)

        # ♻️ Conversation existante
        else:
            if not ObjectId.is_valid(conversation_id):
                raise ValueError("Invalid conversation id")

            conv = self.conversations.find_one(
                {"_id": ObjectId(conversation_id)}
            )

            if not conv:
                raise ValueError("Conversation not found")

            conversation_title = conv.get("title", "")

        # ================================
        # 💬 MESSAGE UTILISATEUR
        # ================================
        self.messages.insert_one(
            Message(
                conversation_id=conversation_id,
                role="user",
                content=question,
                created_at=datetime.utcnow()
            ).dict(exclude={"id"}, exclude_none=True)
        )

        # ================================
        # 🤖 IA (RAG + MuRAG)
        # ================================
        result = RagService.ask(question)

        answer_text = result.get("answer", "")
        images = result.get("images")   # dict ou None

        # ================================
        # 💬 MESSAGE ASSISTANT (TEXTE + IMAGES)
        # ================================
        self.messages.insert_one(
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer_text,
                images=images,              # ✅ STOCKAGE DES IMAGES
                created_at=datetime.utcnow()
            ).dict(exclude={"id"}, exclude_none=True)
        )

        # ================================
        # 🔁 RÉPONSE API
        # ================================
        return {
            "conversation_id": conversation_id,
            "conversation_title": conversation_title,
            "answer": answer_text,
            "images": images
        }

    # ==================================================
    # LISTE DES CONVERSATIONS
    # ==================================================
    def get_user_conversations(self, user_id: str):
        conversations = self.conversations.find(
            {"user_id": user_id},
            {"_id": 1, "title": 1, "created_at": 1}
        ).sort("created_at", -1)

        return [
            {
                "id": str(c["_id"]),
                "title": c.get("title", ""),
                "created_at": c.get("created_at")
            }
            for c in conversations
        ]

    # ==================================================
    # MESSAGES D’UNE CONVERSATION
    # ==================================================
    def get_conversation_messages(self, conversation_id: str):
        if not ObjectId.is_valid(conversation_id):
            raise ValueError("Invalid conversation id")

        return list(
            self.messages
            .find({"conversation_id": conversation_id}, {"_id": 0})
            .sort("created_at", 1)
        )

    # ==================================================
    # SUPPRESSION
    # ==================================================
    def delete_conversation(self, conversation_id: str, user_id: str):
        if not ObjectId.is_valid(conversation_id):
            raise ValueError("Invalid conversation id")

        conv = self.conversations.find_one({
            "_id": ObjectId(conversation_id),
            "user_id": user_id
        })

        if not conv:
            raise ValueError("Conversation not found")

        self.conversations.delete_one({"_id": ObjectId(conversation_id)})
        self.messages.delete_many({"conversation_id": conversation_id})

        return True
