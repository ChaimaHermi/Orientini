from app.db.mongo import get_db


def database():
    return get_db()