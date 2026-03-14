import os
import google.generativeai as genai

genai.configure(api_key=os.getenv("GOOGLE_API_KEY"))

PROMPT = """
Extract the following JSON from the user journal text.
Return:
{
  "emotion": "<single emotion label>",
  "keywords": ["...","..."],
  "summary": "<one sentence summarizing mental state>"
}
Journal text:
\"\"\"{text}\"\"\"
"""

def analyze_text(text: str) -> dict:
    response = genai.responses.create(
        model="gemini-1.5-mini",
        input=PROMPT.format(text=text),
        max_output_tokens=250,
        temperature=0.3,
    )
    raw = response.output[0].content[0].text.strip()
    import json
    return json.loads(raw)