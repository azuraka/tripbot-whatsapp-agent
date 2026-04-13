from fastapi import FastAPI
from pydantic import BaseModel
from agents.expense_parser import parse_expense
from agents.travel_agent import answer_travel_query
from integrations.whatsapp import send_whatsapp_message
from db import save_expense, get_group_total

app = FastAPI()

BOT_NAME = "@TripBot"


class WebhookPayload(BaseModel):
    message: str
    group_id: str
    sender: str


@app.post("/webhook")
async def whatsapp_webhook(payload: WebhookPayload):
    message = payload.message
    group_id = payload.group_id
    sender = payload.sender

    if BOT_NAME.lower() not in message.lower():
        return {"status": "ignored"}

    clean = message.replace(BOT_NAME, "").strip()
    lower = clean.lower()

    if "split" in lower or "paid" in lower:
        expense = parse_expense(clean, sender)
        save_expense(group_id, expense)
        response = f"Added expense: ₹{expense['amount']} for {expense['description']}"

    elif "total" in lower or "spent" in lower:
        total = get_group_total(group_id)
        response = f"Total trip spend so far: ₹{total}"

    else:
        response = answer_travel_query(clean)

    send_whatsapp_message(group_id, response)
    return {"status": "ok"}