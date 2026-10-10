import json
import redis
from core.config import settings

_r =redis.Redis.from_url(settings.redis_url, decode_responses = True)

def get_history(session_id:str) -> list[dict[str, str]]:
    return [json.loads(m) for m in _r.lrange(f"chat:{session_id}", 0, -1)]


def append_message(session_id: str, role: str, content:str) ->None:
    key = f"chat: {session_id}"
    _r.rpush(key, json.dumps({"role": role, "content": content}))
    _r.ltrim(key, -settings.chat_history_limit, -1)
    _r.expire(key, settings.session_ttl_seconds)


#Partial booking stat lives in Redis also
def get_booking_state(session_id:str) -> dict[str,str]:
    return json.loads(_r.get(f"booking: {session_id}") or "{}")

def set_booking_state(session_id: str, state: dict[str, str]) -> None:
    _r.set(f"booking: {session_id}", json.dumps(state), ex=settings.session_ttl_seconds)

def clear_booking_state(session_id:str) -> None:
    _r.delete(f"booking: {session_id}")