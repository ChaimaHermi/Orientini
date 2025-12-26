from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.api.v1.routes import auth, chat
from app.api.v1.routes import users
from app.db.mongo import get_db
from app.services.auth_service import create_admin_if_not_exists


@asynccontextmanager
async def lifespan(app: FastAPI):
    db = get_db()
    create_admin_if_not_exists(db)
    yield




app = FastAPI(
    title="Orientini API",
    version="1.0.0",
    description="AI assistant for Tunisian students orientation",
    lifespan=lifespan
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:4200"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routes
app.include_router(auth.router, prefix="/api")
app.include_router(users.router, prefix="/api")
app.include_router(chat.router, prefix="/api")

# Root
@app.get("/")
def root():
    return {"message": "Orientini backend is running"}
