from fastapi import FastAPI
from api.routes import router
from dotenv import load_dotenv

load_dotenv()

app = FastAPI(title="YouTube RAG API")
app.include_router(router)