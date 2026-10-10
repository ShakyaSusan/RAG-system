from services import llm, vector_store
from services.embeddings import embed_texts

SYSTEM = (
    "You are a helpful assistant. Answer using ONLY the content below."
    "If the answer is not in the context, say you don't know. \n\nContext:\n{context}"
)

def condense_question(history: list[dict[str, str]], question: str) -> str:
    if not history:
        return question
    convo = "\n".join(f"{m['role']}: {m['content']}" for m in history)
    prompt = (
        "Rewrite the final user question as a standalone question using the conversation. "
        "Return only the question. \n\n" f"{convo}\nuser: {question}"
    )
    return llm.chat([{"role": "user", "content": prompt}]).strip()

def answer(history: list[dict[str, str]], question: str) -> str:
    standalone =condense_question(history, question)
    [vector] = embed_texts([standalone])
    context = "\n---\n".join(vector_store.search(vector, top_k=4))
    messages = [{"role": "system", "content": SYSTEM.format(context=context)}]
    messages += history + [{"role": "user", "content": question}]
    return llm.chat(messages)