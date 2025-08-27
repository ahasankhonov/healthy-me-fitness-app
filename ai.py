# ai.py
import os
import json
import openai
from dotenv import load_dotenv
from typing import List, Dict

load_dotenv()

openai.api_key = os.getenv("OPENAI_API_KEY")


def dict_to_string(obj, level=0) -> str:
    """Convert nested dicts/lists to a readable string for AI input."""
    strings = []
    indent = "  " * level
    if isinstance(obj, dict):
        for key, value in obj.items():
            if isinstance(value, (dict, list)):
                nested = dict_to_string(value, level + 1)
                strings.append(f"{indent}{key}: {nested}")
            else:
                strings.append(f"{indent}{key}: {value}")
    elif isinstance(obj, list):
        for idx, item in enumerate(obj):
            nested = dict_to_string(item, level + 1)
            strings.append(f"{indent}Item {idx + 1}: {nested}")
    else:
        strings.append(f"{indent}{obj}")
    return "\n".join(strings)


def ask_ai(profile: Dict, question: str, notes: List[Dict] = []) -> str:
    """Ask the AI a question with profile and notes."""
    notes_text = "\n".join([note.get("text", "") for note in notes])
    prompt = f"""
Profile:
{dict_to_string(profile)}

Notes:
{notes_text}

Question:
{question}
"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    return response.choices[0].message.content.strip()


def get_macros(profile: Dict, goals: List[str], notes: List[Dict] = []) -> Dict:
    """Generate daily macros considering profile, goals, and notes."""
    notes_text = "\n".join([note.get("text", "") for note in notes])
    prompt = f"""
Profile:
{dict_to_string(profile)}

Goals:
{', '.join(goals)}

Notes:
{notes_text}

Please calculate the user's daily macros (calories, protein, fat, carbs) in JSON format like:
{{"calories": 2500, "protein": 150, "fat": 70, "carbs": 300}}
"""
    response = openai.chat.completions.create(
        model="gpt-4",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.7
    )
    try:
        return json.loads(response.choices[0].message.content.strip())
    except json.JSONDecodeError:
        # Fallback: return zeros if AI doesn't output proper JSON
        return {"calories": 0, "protein": 0, "fat": 0, "carbs": 0}
