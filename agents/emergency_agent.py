from services.gemini_service import ask_gemini
from utils.prompts import EMERGENCY_PROMPT


def analyze_emergency(text):

    prompt = f"""
    {EMERGENCY_PROMPT}

    Emergency Report:

    {text}
    """

    return ask_gemini(prompt)