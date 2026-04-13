from openai import OpenAI

client = OpenAI()


def answer_travel_query(query: str):
    prompt = f"""
    You are a helpful WhatsApp group travel assistant.
    Keep answers short and useful.

    Query: {query}
    """

    res = client.responses.create(
        model="gpt-5-mini",
        input=prompt
    )

    return res.output_text
