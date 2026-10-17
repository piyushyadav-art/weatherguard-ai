import os

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage

load_dotenv()


def explain_report(report: dict) -> str:
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY is not set. Add your Gemini API key to the project's .env file."
        )

    llm = ChatGoogleGenerativeAI(
        model="gemini-3.8-flash",
        api_key=api_key,
        temperature=0
    )

    prompt = f"""
You are a weather-information assistant.

Use only the verified report below.

REPORT:
{report}

Write a concise explanation in plain text, using at most 5 short bullet points.
Include the current conditions, overall risk, any important alert, and practical
safety suggestions. Avoid repeating values and do not include a long introduction.
End with this disclaimer exactly once:
   "Follow official guidance from local disaster-management authorities."

Do not invent values, locations, warnings, or emergency claims.
"""

    response = llm.invoke([
        HumanMessage(content=prompt)
    ])

    content = response.content

    # Some Gemini/LangChain versions return content blocks with metadata such
    # as signatures. Keep only the human-readable text for the app.
    if isinstance(content, str):
        return content

    if isinstance(content, list):
        text_parts = []
        for block in content:
            if isinstance(block, str):
                text_parts.append(block)
            elif isinstance(block, dict) and isinstance(block.get("text"), str):
                text_parts.append(block["text"])
        return "\n".join(text_parts).strip()

    return str(content)
