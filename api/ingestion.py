from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.models import Document
from db.session import get_db
from services import vector_store
from services.chunking import ChunkStrategy, chunk_text
from services.embeddings import embed_texts
from services.parsing import extract_text

router = APIRouter(prefix = "/ingest", tags = ["ingestion"])

class IngestResponse(BaseModel):
    document_id: str
    filename: str
    chunk_strategy: ChunkStrategy
    chunk_count: int


@router.post("", response_model = IngestResponse)
async def ingest(
    file: UploadFile = File(...),
    strategy: ChunkStrategy = Form(ChunkStrategy.FIXED),
    db: Session = Depends(get_db),
) -> IngestResponse:
    content = await file.read()
    try:
        text = extract_text(file.filename or "", content)
    except ValueError as e:
        raise HTTPException(status_code = 400, detail=str(e))
    if not text.strip():
        raise HTTPException(status_code=422, detail="No extractable text")

    chunks = chunk_text(text, strategy)
    vectors = embed_texts(chunks)

    doc = Document(
        filename= file.filename,
        file_type = (file.filename or "").rsplit(".",1)[-1].lower(),
        chunk_strategy = strategy.value,
        chunk_count = len(chunks),
    )
    db.add(doc)
    db.commit()

    vector_store.upsert_chunks(doc.id, chunks, vectors)
    return IngestResponse(
        document_id=doc.id, filename=doc.filename, chunk_strategy=strategy, chunk_count=len(chunks)
    )
