import os
from typing import Any

from dotenv import load_dotenv
from langchain_core.messages import AIMessage, HumanMessage, SystemMessage
from langchain_openai import ChatOpenAI

from app.config import DEFAULT_MODEL
from app.parsers import parse_json_response
from app.prompts import (
    CAREER_COACH_SYSTEM_PROMPT,
    COVER_LETTER_PROMPT,
    JOB_MATCH_PROMPT,
    RESUME_REVIEW_PROMPT,
)


load_dotenv()


def ensure_api_key() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise ValueError("OPENAI_API_KEY is missing. Add it to your environment or .env file.")


def build_llm(temperature: float = 0.2) -> ChatOpenAI:
    ensure_api_key()
    return ChatOpenAI(model=DEFAULT_MODEL, temperature=temperature)


def evaluate_resume(resume_text: str) -> dict[str, Any]:
    response = build_llm(temperature=0).invoke(
        RESUME_REVIEW_PROMPT.format(resume=resume_text)
    )
    return parse_json_response(response.content)


def evaluate_job_match(resume_text: str, job_description: str) -> dict[str, Any]:
    response = build_llm(temperature=0).invoke(
        JOB_MATCH_PROMPT.format(resume=resume_text, job_description=job_description)
    )
    return parse_json_response(response.content)


def generate_cover_letter(
    resume_text: str,
    job_description: str,
    candidate_name: str,
    email: str,
    phone: str,
    company_name: str,
    hiring_manager: str,
    tone: str,
) -> str:
    response = build_llm(temperature=0.5).invoke(
        COVER_LETTER_PROMPT.format(
            resume=resume_text,
            job_description=job_description,
            candidate_name=candidate_name or "The Candidate",
            email=email or "Not provided",
            phone=phone or "Not provided",
            company_name=company_name or "the company",
            hiring_manager=hiring_manager or "Hiring Manager",
            tone=tone,
        )
    )
    return response.content.strip()


def career_coach_reply(resume_text: str, chat_history: list[dict[str, str]], user_message: str) -> str:
    llm = build_llm(temperature=0.4)
    messages: list[Any] = [
        SystemMessage(content=CAREER_COACH_SYSTEM_PROMPT.format(resume=resume_text))
    ]

    for message in chat_history:
        role = message.get("role")
        content = message.get("content", "")
        if role == "user":
            messages.append(HumanMessage(content=content))
        elif role == "assistant":
            messages.append(AIMessage(content=content))

    messages.append(HumanMessage(content=user_message))
    response = llm.invoke(messages)
    return response.content.strip()
