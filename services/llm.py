from openai import OpenAI
from core.config import settings

client = OpenAI(api_key=settings.groq_api_key, base_url = settings.groq_base_url)

def chat(messages: list[dict[str, str]], json_mode: bool = False) -> str:
    resp = client.chat.completions.create(
        model = settings.chat_model,
        messages = messages,
        temperature = 0.2,
        response_format ={"type": "json_object"} if json_mode else None,   
    )
    return resp.choices[0].message.content or ""