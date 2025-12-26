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

    def ask(
        self,
        user_id: str,
        question: str,
        conversation_id: str | None = None
    ):
        """
        Crée une conversation si nécessaire,
        ajoute les messages user + assistant,
        retourne l'id + le titre + la réponse IA
        """

        # 🆕 nouvelle conversation
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

        # ♻️ conversation existante
        else:
            if not ObjectId.is_valid(conversation_id):
                raise ValueError("Invalid conversation id")

            conv = self.conversations.find_one(
                {"_id": ObjectId(conversation_id)}
            )

            if not conv:
                raise ValueError("Conversation not found")

            conversation_title = conv["title"]

        # 💬 message utilisateur
        self.messages.insert_one(
            Message(
                conversation_id=conversation_id,
                role="user",
                content=question,
                created_at=datetime.utcnow()
            ).dict(exclude={"id"}, exclude_none=True)
        )

        # 🤖 réponse IA
        answer = RagService.ask(question)

        # 💬 message assistant
        self.messages.insert_one(
            Message(
                conversation_id=conversation_id,
                role="assistant",
                content=answer,
                created_at=datetime.utcnow()
            ).dict(exclude={"id"}, exclude_none=True)
        )

        return {
            "conversation_id": conversation_id,
            "conversation_title": conversation_title,
            "answer": answer
        }

    def get_user_conversations(self, user_id: str):
        conversations = self.conversations.find(
            {"user_id": user_id},
            {"_id": 1, "title": 1, "created_at": 1}
        ).sort("created_at", -1)

        return [
            {
                "id": str(c["_id"]),
                "title": c["title"],
                "created_at": c["created_at"]
            }
            for c in conversations
        ]

    def get_conversation_messages(self, conversation_id: str):
        if not ObjectId.is_valid(conversation_id):
            raise ValueError("Invalid conversation id")

        return list(
            self.messages
            .find({"conversation_id": conversation_id}, {"_id": 0})
            .sort("created_at", 1)
        )

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
