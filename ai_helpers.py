import os 
import openai

def generate_outreach_message(application): 
    """
    Given a single application record (dict-like), return a suggested outreach message.

    Notes:
    - The current implementation uses a placeholder prompt (smoothie recipe) and does not yet
      incorporate fields from `application`; adapt `prompt` if you want a job-specific message.
    - This helper is kept separate from the Streamlit app so it can be reused and unit-tested.
    """

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key: 
        # Fail fast with a clear error if the key is missing so the UI can show a helpful message.
        raise RuntimeError("OPENAI_API_KEY is not set in env variables.")

    client = openai.OpenAI(api_key=api_key)  # create a lightweight client on each call; fine for low traffic

    # Prompt for the model describing what we want it to write.
    prompt = f"""
You are an expert career coach helping a job seeker write a short, professional outreach message
to a contact at a company about an open role.

Write a concise message (4–7 sentences) that:
- Mentions the role title "{application.get('Role', '').strip()}" and company "{application.get('Company', '').strip()}".
- Is friendly, confident, and polite (no begging, no apologies).
- Clearly expresses interest in the role and the company.
- Briefly highlights 1–2 strengths or relevant experiences (keep these generic if not provided in notes).
- Includes a soft call to action (e.g., quick chat, guidance, or advice).

If a contact name is provided ("{application.get('Contact Name', '').strip()}"), address them by first name;
otherwise, use a neutral greeting like "Hi there". If a LinkedIn URL is provided
("{application.get('Contact LinkedIn', '').strip()}"), you may mention that the sender found them on LinkedIn.
Do not invent specific companies, roles, or projects beyond what is given.
Avoid placeholders like [INSERT TEXT]; write a complete, ready‑to‑send message.
"""
    # Calling the chat completion model.
    # Consider passing only non-sensitive fields from `application` to avoid leaking PII to third parties.
    response = client.chat.completions.create(
        model = "gpt-4o-mini", # can alter model
        messages = [
            {
                "role": "system",
                "content": (
                    "You are a professional career coach who specializes in drafting clear, natural, "
                    "and effective outreach messages for job seekers. Always be concise, specific, "
                    "and human-sounding, and keep the tone warm, confident, and respectful."
                ),
            },
            {"role": "user", "content": prompt},
        ],
        temperature = 0.7 # range from 0.0 (deterministic) – 1.0 (very creative)
    )

    # Extract text from the AI response (first choice only; additional choices are discarded)
    message_text = response.choices[0].message.content.strip()
    return message_text