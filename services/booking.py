import json
from datetime import date, time
from pydantic import BaseModel, EmailStr, ValidationError
from sqlalchemy.orm import Session

from db.models import Booking
from services import llm, memory


class BookingExtraction(BaseModel):
    is_booking_intent: bool = False
    name: str | None = None
    email: str | None = None
    date: str | None = None
    time: str | None = None


class BookingData(BaseModel):
    name: str
    email: EmailStr
    date: date
    time: time


EXTRACT_PROMPT = """
Today is {today}. Read the conversation and the latest user message.
Return JSON with keys: is_booking_intent (bool), name, email, date (YYYY-MM-DD), time (HH:MM 24h).
Use null for anything not provided. Set is_booking_intent true if the user wants to book an
interview OR is answering a question about booking details.
Latest message: {message}
Already collected: {state}
"""

def extract(message: str, state: dict[str, str]) -> BookingExtraction:
    raw = llm.chat(
        [{"role": "user", "content": EXTRACT_PROMPT.format(
            today=date.today().isoformat(), message = message, state = json.dumps(state))}],
        json_mode=True,
    )
    try:
        return BookingExtraction.model_validate_json(raw)
    except ValidationError:
        return BookingExtraction()
    

def handle_booking(session_id: str, message: str, db: Session) -> str | None:
    """Return a reply if this message belongs to a booking flow, else None."""
    state = memory.get_booking_state(session_id)
    extracted = extract(message, state)

    if not (state or extracted.is_booking_intent):
        return None

    for key in ("name", "email", "date", "time"):
        value = getattr(extracted, key)
        if value: 
            state[key] = value

    missing = [k for k in ("name", "email", "date", "time") if k not in state]
    if missing:
        memory.set_booking_state(session_id, state)
        return f"Happy to book that! Could you please share your {', '.join(missing)}?"

    try:
        data = BookingData.model_validate(state)
    except ValidationError:
        memory.clear_booking_state(session_id)
        return "Some details looked invalid. Let's start again = what's your name?"

    db.add(Booking(name = data.name, email = data.email, date = data.date, time = data.time))
    db.commit()
    memory.clear_booking_state(session_id)
    return f"Booked! {data.name}, your interview is on {data.date} at {data.time: %H:%M}. Confirmation will go to {data.email}."