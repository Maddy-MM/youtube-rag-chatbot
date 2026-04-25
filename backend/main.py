import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from api.routes import router
from dotenv import load_dotenv
from src.database import init_db, SessionLocal
from src.auth import get_user, create_user

load_dotenv()


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    init_db()

    default_username = os.environ.get("DEFAULT_USER", "admin")
    default_password = os.environ.get("DEFAULT_PASS", "admin123")

    db = SessionLocal()
    try:
        if not get_user(db, default_username):
            create_user(db, default_username, default_password)
            print(f"Default user '{default_username}' created.")
        else:
            print(f"Default user '{default_username}' already exists.")
    finally:
        db.close()

    yield  # Application runs here


app = FastAPI(title="YouTube RAG API", lifespan=lifespan)
app.include_router(router)