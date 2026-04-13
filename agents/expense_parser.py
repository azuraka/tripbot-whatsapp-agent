from openai import OpenAI
import json

client = OpenAI()


def parse_expense(message: str, sender: str):
    prompt = f"""
    Convert this trip expense message into JSON.

    Message: {message}
    Sender: {sender}

    Return JSON with:
    amount, description, paid_by, split_type
    """

    res = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    text = res.output_text

    try:
        data = json.loads(text)
    except:
        data = {
            "amount": 0,
            "description": message,
            "paid_by": sender,
            "split_type": "equal"
        }

    return data
