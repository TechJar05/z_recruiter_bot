# core/gender_utils.py
import requests

from openai import OpenAI
from decouple import config
client = OpenAI(api_key=config("OPENAI_API_KEY"))

def predict_gender_from_name(name: str) -> str | None:
    """
    Predicts gender from first name using Genderize.io API.
    Returns 'male', 'female' or None.
    """
    try:
        response = requests.get(f"https://api.genderize.io/?name={name}")
        if response.status_code == 200:
            data = response.json()
            if data.get("gender") and float(data.get("probability", 0)) > 0.7:
                return data["gender"]
        return None
    except:
        return None


def predict_gender_from_resume(resume_text: str) -> str:
    """
    Uses OpenAI to analyze the full resume text and infer gender (male/female).
    """
    prompt = f"""
You are an HR expert. Based on the resume text below, predict the candidate's gender.
Use cues like pronouns or descriptions. Return only one word: male or female.

Resume:
{resume_text}
    """
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.1,
        )
        return response.choices[0].message.content.strip().lower()
    except:
        return "male"  # fallback


def get_final_gender(name: str, resume_text: str) -> str:
    """
    Final function to return gender:
    1. Try name-based.
    2. Fallback to resume text.
    """
    gender = predict_gender_from_name(name)
    if gender:
        return gender
    return predict_gender_from_resume(resume_text)
