import uuid
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, PointStruct, VectorParams
from core.config import settings

client = QdrantClient(url=settings.qdrant_url)

def ensure_collection() -> None:
    existing = {c.name for c in client.get_collections().collections}
    if settings.qdrant_collection not in existing:
        client.create_collection(
            settings.qdrant_collection,
            vectors_config = VectorParams(size = settings.embedding_dim, distance=Distance.COSINE),
        )


def upsert_chunks(document_id: str, chunks: list[str], vectors: list[list[float]]):
    points = [
        PointStruct(
            id = str(uuid.uuid4()),
            vector=vec,
            payload={"document_id": document_id, "chunk_index": i, "text": chunk},
        )
        for i, (chunk, vec) in enumerate(zip(chunks, vectors))
    ]
    client.upsert(settings.qdrant_collection, points=points)


def search(query_vector: list[float], top_k: int = 4) -> list[str]:
    result = client.query_points(settings.qdrant_collection, query=query_vector, limit = top_k)
    return [p.payload["text"] for p in result.points if p.payload]