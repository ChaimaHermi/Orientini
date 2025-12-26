from pymongo import MongoClient
from app.core.config import settings

client = MongoClient(settings.MONGO_URI)
db = client[settings.MONGO_DB]

users = db.users
conversations = db.conversations
messages = db.messages
orientation_sessions = db.orientation_sessions
programs = db.programs

def get_db():
    return db
