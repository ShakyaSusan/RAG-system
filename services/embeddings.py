from sentence_transformers import SentenceTransformer

model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")

def embed_texts(texts: list[str]) -> list[list[float]]:
    vectors = model.encode(
        texts,
        normalize_embeddings = True,
        convert_to_numpy = True
    )

    return vectors.tolist() 