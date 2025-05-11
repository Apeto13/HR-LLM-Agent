from groq import Groq
from backend.prompts import format_prompt
import json
import re
from backend.api_key import API_KEY

client = Groq(api_key=API_KEY)

def llm_call(text: str, model: str = "deepseek-r1-distill-llama-70b") -> str:
    prompt = format_prompt.format(input=text)
    response = client.chat.completions.create(
        messages=[{'role':'user', 'content': prompt}],
        model = model,
        temperature = 0.0
    )
    return response.choices[0].message.content

def parse_llm_to_json(llm_output: str) -> dict:
    cleaned = re.sub(r'^```(?:json)?\s*', '', llm_output.strip(), flags=re.IGNORECASE)
    cleaned = re.sub(r'\s*```$', '', cleaned, flags=re.IGNORECASE)

    match = re.search(r'\{.*\}', cleaned, flags=re.DOTALL)
    json_text = match.group(0) if match else cleaned

    try:
        return json.loads(json_text)
    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        return {}