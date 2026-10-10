import re
from enum import StrEnum

class ChunkStrategy(StrEnum):
    FIXED = "fixed"
    SENTENCE = "sentence"

def fixed_size_chunks(text: str, size: int = 800, overlap: int = 100) -> list[str]:
    step = size-overlap
    return [text[i : i + size] for i in range(0, len(text), step) if text[i : i + size].strip()]

def sentence_chunks(text: str, max_chars: int = 800) -> list[str]:
    sentences = re.split(r"(?<=[.!?])\s+", text)
    chunks : list[str] = []
    current = ""
    for s in sentences:
        if current and len(current) + len(s) > max_chars:
            chunks.append(current.strip())
            current = ""
        current += s + " "
    if current.strip():
        chunks.append(current.strip())

    return chunks

def chunk_text(text: str, strategy: ChunkStrategy) -> list[str]:
    if strategy is ChunkStrategy.FIXED:
        return fixed_size_chunks(text)
    return sentence_chunks(text)

