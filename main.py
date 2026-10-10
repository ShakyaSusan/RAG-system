from contextlib import asynccontextmanager
from fastapi import FastAPI
from api import chat, ingestion
from db.models import Base
from db.session import engine
from services.vector_store import ensure_collection


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(engine)
    ensure_collection()
    yield


app = FastAPI(title="Conversational RAG", lifespan = lifespan)
app.include_router(ingestion.router)
app.include_router(chat.router)