
import os
import json
import time
from pathlib import Path
from dotenv import load_dotenv
from google import genai
from google.genai import errors

BASE_DIR = Path(__file__).parent.parent

load_dotenv(BASE_DIR / ".env")

api_key = os.getenv("GEMINI_API_KEY")

if not api_key:
    raise ValueError("GEMINI_API_KEY not found in .env file.")

client = genai.Client(api_key=api_key)


def generate_answer(question, retrieved_chunks):
    if not retrieved_chunks:
        return "I could not find relevant policy information. Please contact HR."

    policy_context = []

    for chunk in retrieved_chunks:
        policy_context.append({
            "policy_title": chunk.get("policy_title"),
            "policy_code": chunk.get("policy_code"),
            "version": chunk.get("version_number"),
            "effective_start": chunk.get("effective_start"),
            "effective_end": chunk.get("effective_end"),
            "content": chunk.get("content")
        })

    prompt = f"""
You are an HR Policy Assistant.

Answer using only the supplied policy information.

Rules:
1. Never invent policy details.
2. If information is insufficient, say so.
3. Do not make unsupported guarantees.
4. Keep the answer clear and concise.
5. Cite the policy title and version.
6. Recommend contacting HR when the policy does not cover the question.

POLICY INFORMATION:
{json.dumps(policy_context, indent=2)}

EMPLOYEE QUESTION:
{question}
"""

    models = ["gemini-flash-latest", "gemini-2.5-flash"]

    for model in models:
        for attempt in range(3):
            try:
                response = client.models.generate_content(
                    model=model,
                    contents=prompt
                )

                return response.text

            except errors.APIError as error:
                if error.code not in (429, 500, 503):
                    raise

                if attempt < 2:
                    time.sleep(2 ** (attempt + 1))

        print(f"{model} unavailable. Trying fallback model.")

    return "The AI service is temporarily unavailable. Please try again later."

