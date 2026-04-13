from fastapi import FastAPI, Query
from pydantic import BaseModel
import os
from agents.expense_parser import parse_expense
from agents.travel_agent import answer_travel_query
from integrations.whatsapp import send_whatsapp_message
from db import save_expense, get_group_total

app = FastAPI()

BOT_NAME = "@TripBot"
VERIFY_TOKEN = os.getenv("VERIFY_TOKEN", "tripbot123")

@app.get("/webhook")
def verify_webhook(
    hub_mode: str = Query(None, alias="hub.mode"),
    hub_verify_token: str = Query(None, alias="hub.verify_token"),
    hub_challenge: str = Query(None, alias="hub.challenge")
):
    if hub_mode == "subscribe" and hub_verify_token == VERIFY_TOKEN:
        return int(hub_challenge)
    return {"error": "invalid token"}


@app.post("/webhook")
async def whatsapp_webhook(payload: dict):
    try:
        print("POST WEBHOOK HIT")
        print(payload)

        entry = payload["entry"][0]
        changes = entry["changes"][0]
        value = changes["value"]

        if "messages" not in value:
            return {"status": "no_message"}

        message_obj = value["messages"][0]
        sender = message_obj["from"]
        message = message_obj["text"]["body"]

        group_id = value.get("metadata", {}).get("phone_number_id", "default")

        if BOT_NAME.lower() not in message.lower():
            return {"status": "ignored"}

        clean = message.replace(BOT_NAME, "").strip()
        lower = clean.lower()

        if "split" in lower or "paid" in lower:
            expense = parse_expense(clean, sender)
            save_expense(group_id, expense)
            response = f"Added ₹{expense['amount']} for {expense['description']}"

        elif "total" in lower or "spent" in lower:
            total = get_group_total(group_id)
            response = f"Total trip spend so far: ₹{total}"

        else:
            response = answer_travel_query(clean)

        print("BOT RESPONSE:", response)
        return {"status": "ok"}

    except Exception as e:
        print("ERROR:", str(e))
        return {"error": str(e)}