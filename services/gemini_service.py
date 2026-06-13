import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def fallback_response():

    return """
    {
        "severity":"Critical",
        "type":"Medical Emergency",
        "location":"Silk Board",
        "route":["Silk Board","Bannerghatta Road"],
        "corridor_required":true,
        "citizen_alert":"Emergency corridor active. Please use alternate routes."
    }
    """


def ask_gemini(prompt):

    try:

        response = model.generate_content(
            prompt
        )

        return response.text

    except Exception as e:

        print("Gemini Error:", e)

        return fallback_response()