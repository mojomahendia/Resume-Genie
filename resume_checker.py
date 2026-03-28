import json
import os
import tempfile
from pathlib import Path
from typing import Any

import streamlit as st
from dotenv import load_dotenv
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from langchain_community.document_loaders import PyMuPDFLoader


load_dotenv()

PROMPT = PromptTemplate(
    input_variables=["context", "question"],
    template="""
You are an expert career counselor and resume evaluator.

Your task is to analyze the given resume carefully and provide a structured evaluation.

Resume:
{context}

User Query:
{question}

Instructions:
1. Evaluate the resume based on clarity, relevance, skills, experience, formatting, and impact.
2. Provide a score out of 100.
3. Identify key strengths and weaknesses.
4. Extract skills mentioned in the resume.
5. Suggest additional skills that could improve the resume.
6. Keep feedback practical, actionable, and concise.

Output Format (STRICT JSON):
{{
  "score": <number between 0-100>,
  "strengths": [
    "<strength 1>",
    "<strength 2>",
    "<strength 3>"
  ],
  "weaknesses": [
    "<weakness 1>",
    "<weakness 2>",
    "<weakness 3>"
  ],
  "skills_present": [
    "<skill 1>",
    "<skill 2>",
    "<skill 3>"
  ],
  "skills_to_add": [
    "<recommended skill 1>",
    "<recommended skill 2>",
    "<recommended skill 3>"
  ],
  "summary": "<brief overall evaluation in 2-3 lines>"
}}

Important:
- Do NOT include any explanation outside JSON.
- Ensure valid JSON output.
- Be honest but constructive.
""",
)


LOGO_PATH = Path(__file__).with_name("logo.png")


def extract_resume_text(uploaded_file: Any) -> str:
    with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    try:
        documents = PyMuPDFLoader(temp_path).load()
        return "\n\n".join(doc.page_content for doc in documents).strip()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def parse_llm_json(raw_output: str) -> dict[str, Any]:
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw_output[start : end + 1])
        raise ValueError("The model returned an invalid JSON response.")


def evaluate_resume(resume_text: str) -> dict[str, Any]:
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise ValueError("OPENAI_API_KEY is missing. Add it to your environment or .env file.")

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    formatted_prompt = PROMPT.format(
        context=resume_text,
        question="Please evaluate this resume.",
    )
    response = llm.invoke(formatted_prompt)
    return parse_llm_json(response.content)


def render_list(title: str, items: list[str]) -> None:
    bullet_items = "".join(f"<li>{item}</li>" for item in items) or "<li>No items available.</li>"
    st.markdown(
        f"""
        <div class="result-card">
            <h3>{title}</h3>
            <ul>{bullet_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def inject_styles() -> None:
    st.markdown(
        """
        <style>
        .stApp {
            background:
                radial-gradient(circle at top left, rgba(230, 120, 40, 0.16), transparent 28%),
                radial-gradient(circle at top right, rgba(13, 110, 253, 0.10), transparent 25%),
                linear-gradient(180deg, #f8f5ef 0%, #fffdf9 45%, #f5f8fc 100%);
        }
        .main .block-container {
            max-width: 1120px;
            padding-top: 2rem;
            padding-bottom: 3rem;
        }
        .hero-card,
        .panel-card,
        .score-card,
        .summary-card,
        .result-card {
            background: rgba(255, 255, 255, 0.88);
            border: 1px solid rgba(31, 41, 55, 0.08);
            border-radius: 24px;
            box-shadow: 0 18px 45px rgba(31, 41, 55, 0.08);
            backdrop-filter: blur(10px);
        }
        .hero-card {
            padding: 1.5rem;
            margin-bottom: 1.25rem;
        }
        .hero-flex {
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 1.25rem;
        }
        .hero-text {
            flex: 1;
            min-width: 0;
        }
        .hero-eyebrow {
            color: #c45a1a;
            font-size: 0.82rem;
            font-weight: 700;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            margin-bottom: 0.6rem;
        }
        .hero-title {
            color: #162033;
            font-size: 2.6rem;
            line-height: 1.05;
            font-weight: 800;
            margin: 0 0 0.75rem 0;
        }
        .hero-copy {
            color: #465066;
            font-size: 1.04rem;
            line-height: 1.7;
            margin: 0;
            max-width: 42rem;
        }
        .panel-card {
            padding: 1.25rem;
            margin-bottom: 1.25rem;
        }
        .panel-title {
            color: #162033;
            font-size: 1.2rem;
            font-weight: 700;
            margin-bottom: 0.3rem;
        }
        .panel-copy {
            color: #5a6579;
            margin-bottom: 1rem;
        }
        .score-card {
            padding: 1.4rem;
            margin-bottom: 1rem;
            background: linear-gradient(135deg, rgba(14, 116, 144, 0.95), rgba(22, 32, 51, 0.96));
            color: #ffffff;
        }
        .score-label {
            font-size: 0.85rem;
            letter-spacing: 0.08em;
            text-transform: uppercase;
            opacity: 0.78;
            margin-bottom: 0.45rem;
        }
        .score-value {
            font-size: 3rem;
            line-height: 1;
            font-weight: 800;
            margin-bottom: 0.4rem;
        }
        .score-note {
            font-size: 0.98rem;
            opacity: 0.88;
        }
        .summary-card,
        .result-card {
            padding: 1.25rem 1.35rem;
            height: 100%;
        }
        .summary-card h3,
        .result-card h3 {
            color: #162033;
            font-size: 1.08rem;
            margin: 0 0 0.8rem 0;
        }
        .summary-card p,
        .result-card li {
            color: #4f5a6e;
            font-size: 0.98rem;
            line-height: 1.7;
        }
        .result-card ul {
            margin: 0;
            padding-left: 1.2rem;
        }
        .logo-wrap {
            display: flex;
            justify-content: center;
            align-items: center;
            flex: 0 0 auto;
            width: 160px;
            max-width: 30%;
            padding: 0.65rem 0.85rem;
            border-radius: 18px;
            background: linear-gradient(180deg, rgba(255, 248, 240, 0.95), rgba(248, 250, 255, 0.9));
            border: 1px solid rgba(196, 90, 26, 0.16);
        }
        .logo-wrap img {
            max-height: 92px;
            object-fit: contain;
        }
        @media (max-width: 900px) {
            .hero-flex {
                flex-direction: column;
                align-items: flex-start;
            }
            .logo-wrap {
                width: 120px;
                max-width: none;
            }
        }
        [data-testid="stFileUploader"] {
            background: rgba(250, 247, 241, 0.9);
            border: 1px dashed rgba(196, 90, 26, 0.45);
            border-radius: 18px;
            padding: 0.35rem;
        }
        .stButton > button {
            width: 100%;
            border: none;
            border-radius: 14px;
            background: linear-gradient(135deg, #c45a1a, #ea8d42);
            color: white;
            font-weight: 700;
            padding: 0.8rem 1rem;
            box-shadow: 0 12px 24px rgba(196, 90, 26, 0.22);
        }
        .stButton > button:hover {
            background: linear-gradient(135deg, #ae4e14, #db7d31);
        }
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_header() -> None:
    st.markdown('<div class="hero-card"><div class="hero-flex"><div class="hero-text">', unsafe_allow_html=True)
    st.markdown(
        """
        <div class="hero-eyebrow">AI Resume Review</div>
        <div class="hero-title">Upload your resume and get actionable feedback.</div>
        <p class="hero-copy">
            Review clarity, skills, positioning, and overall impact in one place.
            The app reads your resume, scores it, and turns the output into a structured report.
        </p>
        """,
        unsafe_allow_html=True,
    )
    st.markdown("</div>", unsafe_allow_html=True)
    if LOGO_PATH.exists():
        st.markdown('<div class="logo-wrap">', unsafe_allow_html=True)
        st.image(str(LOGO_PATH), width=110)
        st.markdown("</div>", unsafe_allow_html=True)
    st.markdown("</div></div>", unsafe_allow_html=True)


def render_summary(summary: str) -> None:
    st.markdown(
        f"""
        <div class="summary-card">
            <h3>Overall Summary</h3>
            <p>{summary}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_score(score: Any) -> None:
    st.markdown(
        f"""
        <div class="score-card">
            <div class="score-label">Resume Score</div>
            <div class="score-value">{score}</div>
            <div class="score-note">A quick indicator of how well the resume communicates impact and fit.</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def main() -> None:
    st.set_page_config(page_title="Resume Checker", page_icon="📄", layout="wide")
    inject_styles()
    render_header()

    st.markdown(
        """
        <div class="panel-card">
            <div class="panel-title">Start Your Resume Review</div>
            <div class="panel-copy">
                Upload a PDF version of your resume, then click submit to generate your analysis.
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )

    upload_col, action_col = st.columns([2.4, 1], gap="large")
    with upload_col:
        uploaded_file = st.file_uploader("Upload your resume", type=["pdf"], label_visibility="collapsed")
    with action_col:
        st.markdown("<div style='height: 0.4rem;'></div>", unsafe_allow_html=True)
        submit_clicked = st.button("Analyze Resume", type="primary")

    if submit_clicked:
        if uploaded_file is None:
            st.warning("Please upload a PDF resume before submitting.")
            return

        with st.spinner("Analyzing your resume..."):
            try:
                resume_text = extract_resume_text(uploaded_file)
                if not resume_text:
                    st.error("Could not extract text from the uploaded resume.")
                    return

                result = evaluate_resume(resume_text)
            except Exception as exc:
                st.error(f"Resume analysis failed: {exc}")
                return

        score = result.get("score", "N/A")
        st.success("Resume analysis completed.")
        render_score(score)

        summary = result.get("summary")
        if summary:
            render_summary(summary)

        first_row = st.columns(2, gap="large")
        with first_row[0]:
            render_list("Strengths", result.get("strengths", []))
        with first_row[1]:
            render_list("Weaknesses", result.get("weaknesses", []))

        second_row = st.columns(2, gap="large")
        with second_row[0]:
            render_list("Skills Present", result.get("skills_present", []))
        with second_row[1]:
            render_list("Skills To Add", result.get("skills_to_add", []))

        with st.expander("Raw JSON Output"):
            st.json(result)


if __name__ == "__main__":
    main()
