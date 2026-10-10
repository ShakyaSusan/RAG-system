from fastapi import APIRouter, Depends
from pydantic import BaseModel
from sqlalchemy.orm import Session

from db.session import get_db
from services import booking, memory, rag

router = APIRouter(prefix="/chat", tags = ["chat"])


class ChatRequest(BaseModel):
    session_id: str
    message: str

class ChatResponse(BaseModel):
    session_id: str
    reply: str


@router.post("", response_model=ChatResponse)
def chat(req: ChatRequest, db: Session = Depends(get_db)) -> ChatResponse:
    history = memory.get_history(req.session_id)

    reply = booking.handle_booking(req.session_id, req.message, db)
    if reply is None:
        reply = rag.answer(history, req.message)

    memory.append_message(req.session_id, "user", req.message)
    memory.append_message(req.session_id, "assistant", reply)
    return ChatResponse(session_id=req.session_id, reply=reply)