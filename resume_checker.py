import json
import os
import tempfile
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
    st.subheader(title)
    if items:
        for item in items:
            st.write(f"- {item}")
    else:
        st.write("No items available.")


def main() -> None:
    st.set_page_config(page_title="Resume Checker", page_icon="📄", layout="centered")
    st.title("Resume Checker")
    st.write("Upload a resume PDF and click submit to see the evaluation.")

    uploaded_file = st.file_uploader("Upload your resume", type=["pdf"])
    submit_clicked = st.button("Submit", type="primary")

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
        st.metric("Resume Score", score)

        summary = result.get("summary")
        if summary:
            st.subheader("Summary")
            st.write(summary)

        render_list("Strengths", result.get("strengths", []))
        render_list("Weaknesses", result.get("weaknesses", []))
        render_list("Skills Present", result.get("skills_present", []))
        render_list("Skills To Add", result.get("skills_to_add", []))

        with st.expander("Raw JSON Output"):
            st.json(result)


if __name__ == "__main__":
    main()
