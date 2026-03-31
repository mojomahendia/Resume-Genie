from __future__ import annotations

import os

import streamlit as st

from app.config import LOGO_PATH
from app.parsers import extract_pdf_text
from app.services import (
    career_coach_reply,
    evaluate_job_match,
    evaluate_resume,
    generate_cover_letter,
)
from app.ui import (
    inject_styles,
    render_hero,
    render_list_card,
    render_metric,
    render_pills,
    render_section_intro,
    render_text_card,
)


def init_state() -> None:
    st.session_state.setdefault("resume_text", "")
    st.session_state.setdefault("resume_filename", "")
    st.session_state.setdefault("coach_messages", [])
    st.session_state.setdefault("coach_status", "Ready")
    st.session_state.setdefault("coach_error", "")


def handle_resume_upload() -> None:
    uploaded_file = st.file_uploader("Upload resume PDF", type=["pdf"], key="resume_uploader")
    if uploaded_file is not None:
        is_new_file = uploaded_file.name != st.session_state.get("resume_filename")
        if is_new_file:
            try:
                text = extract_pdf_text(uploaded_file)
            except Exception as exc:
                st.error(f"Could not read the uploaded PDF: {exc}")
                return

            st.session_state["resume_text"] = text
            st.session_state["resume_filename"] = uploaded_file.name
            st.session_state["resume_review_result"] = None
            st.session_state["job_match_result"] = None
            st.session_state["cover_letter_output"] = None
            st.session_state["coach_messages"] = []
            st.success(f"Loaded `{uploaded_file.name}` successfully.")


def require_resume() -> bool:
    if st.session_state.get("resume_text"):
        return True
    st.info("Upload a resume PDF from the sidebar to unlock all features.")
    return False


def resume_review_page() -> None:
    render_section_intro(
        "Resume Review",
        "Analyze clarity, positioning, skills, and impact. This section gives you a structured report with strengths, weaknesses, and next-step improvements.",
    )

    if not require_resume():
        return

    if st.button("Run Resume Review", use_container_width=True):
        try:
            with st.spinner("Reviewing your resume..."):
                result = evaluate_resume(st.session_state["resume_text"])
            st.session_state["resume_review_result"] = result
        except Exception as exc:
            st.error(f"Resume review failed: {exc}")
            return

    result = st.session_state.get("resume_review_result")
    if not result:
        return

    metric_cols = st.columns(2, gap="large")
    with metric_cols[0]:
        render_metric("Resume Score", str(result.get("score", "N/A")), "A quick measure of overall effectiveness and readiness.")
    with metric_cols[1]:
        render_metric("Best-Fit Role", str(result.get("target_role", "N/A")), "Suggested target role based on your current resume profile.")

    render_text_card("Overall Summary", result.get("summary", "No summary available."))

    first_row = st.columns(2, gap="large")
    with first_row[0]:
        render_list_card("Strengths", result.get("strengths", []))
    with first_row[1]:
        render_list_card("Weaknesses", result.get("weaknesses", []))

    second_row = st.columns(2, gap="large")
    with second_row[0]:
        render_list_card("Skills Present", result.get("skills_present", []))
    with second_row[1]:
        render_list_card("Skills To Add", result.get("skills_to_add", []))

    with st.expander("View structured output"):
        st.json(result)


def job_match_page() -> None:
    render_section_intro(
        "Job Fit Analyzer",
        "Check ATS and recruiter fit before you apply. Paste the job description and get match quality, missing skills, and improvement suggestions.",
    )

    if not require_resume():
        return

    job_description = st.text_area(
        "Paste the job description",
        height=220,
        placeholder="Paste the role description, responsibilities, requirements, and preferred skills here...",
    )

    if st.button("Analyze Job Match", use_container_width=True):
        if not job_description.strip():
            st.warning("Paste a job description first.")
        else:
            try:
                with st.spinner("Comparing your resume with the job description..."):
                    result = evaluate_job_match(st.session_state["resume_text"], job_description)
                st.session_state["job_match_result"] = result
            except Exception as exc:
                st.error(f"Job match analysis failed: {exc}")
                return

    result = st.session_state.get("job_match_result")
    if not result:
        return

    metric_cols = st.columns(3, gap="large")
    with metric_cols[0]:
        render_metric("Match Score", str(result.get("overall_score", "N/A")), "Estimated recruiter and ATS alignment for this role.")
    with metric_cols[1]:
        render_metric("Decision", str(result.get("decision", "N/A")), "How a recruiter may triage the application at first pass.")
    with metric_cols[2]:
        render_metric("Risk Level", str(result.get("risk_level", "N/A")), "Higher risk usually means more missing skills or weak alignment.")

    render_text_card("Recruiter Summary", result.get("final_summary", "No summary available."))

    st.markdown("**Matched Skills**")
    render_pills(result.get("matched_skills", []))
    st.markdown("**Missing Skills**")
    render_pills(result.get("missing_skills", []))
    st.markdown("**ATS Keywords to Include**")
    render_pills(result.get("ats_keywords", []))

    first_row = st.columns(2, gap="large")
    with first_row[0]:
        render_list_card("Key Insights", result.get("key_insights", []))
    with first_row[1]:
        render_text_card("Experience Fit", result.get("experience_fit", "No details available."))

    second_row = st.columns(2, gap="large")
    with second_row[0]:
        render_list_card("Strengths", result.get("strengths", []))
    with second_row[1]:
        render_list_card("Gaps", result.get("gaps", []))

    render_list_card("Recommendations", result.get("recommendations", []))


def cover_letter_page() -> None:
    render_section_intro(
        "Cover Letter Generator",
        "Generate a tailored cover letter that reflects your resume, the role, and the company you are targeting.",
    )

    if not require_resume():
        return

    col1, col2 = st.columns(2, gap="large")
    with col1:
        candidate_name = st.text_input("Full name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")
    with col2:
        company_name = st.text_input("Company name")
        hiring_manager = st.text_input("Hiring manager")
        tone = st.selectbox("Tone", ["Professional", "Confident", "Warm", "Bold"])

    job_description = st.text_area(
        "Job description",
        height=220,
        placeholder="Paste the target job description here...",
        key="cover_letter_job_description",
    )

    if st.button("Generate Cover Letter", use_container_width=True):
        if not job_description.strip():
            st.warning("Paste a job description first.")
        else:
            try:
                with st.spinner("Writing your cover letter..."):
                    letter = generate_cover_letter(
                        resume_text=st.session_state["resume_text"],
                        job_description=job_description,
                        candidate_name=candidate_name,
                        email=email,
                        phone=phone,
                        company_name=company_name,
                        hiring_manager=hiring_manager,
                        tone=tone,
                    )
                st.session_state["cover_letter_output"] = letter
            except Exception as exc:
                st.error(f"Cover letter generation failed: {exc}")
                return

    letter = st.session_state.get("cover_letter_output")
    if not letter:
        return

    st.text_area("Generated cover letter", value=letter, height=360)
    st.download_button(
        "Download Cover Letter",
        data=letter,
        file_name="resume_genie_cover_letter.txt",
        mime="text/plain",
        use_container_width=True,
    )


def career_coach_page() -> None:
    render_section_intro(
        "AI Career Coach",
        "Ask for interview prep, role targeting, skill gaps, or resume improvement advice. The assistant answers using your uploaded resume as context.",
    )

    if not require_resume():
        return

    status_col, info_col = st.columns([1, 2], gap="large")
    with status_col:
        render_metric(
            "Coach Status",
            st.session_state.get("coach_status", "Ready"),
            "The coach updates this while generating a response.",
        )
    with info_col:
        render_text_card(
            "How This Works",
            "Upload your resume, type a question, and Resume Genie answers using your resume as context. If something fails, the error will appear below so you can see exactly what happened.",
        )

    if not os.getenv("OPENAI_API_KEY"):
        st.warning("`OPENAI_API_KEY` is not set, so the coach cannot generate a response yet.")

    if not st.session_state["coach_messages"]:
        st.info(
            "Try asking: 'What roles am I best suited for?', 'Give me interview questions for this resume', or 'What skills should I learn next?'"
        )
        st.session_state["coach_messages"].append(
            {
                "role": "assistant",
                "content": "I’m ready to help with resume improvements, interview prep, job targeting, and skill-gap analysis. Ask me anything about your next career step.",
            }
        )

    for message in st.session_state["coach_messages"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    if st.session_state.get("coach_error"):
        st.error(st.session_state["coach_error"])

    prompt = st.chat_input("Ask Resume Genie about your resume, interviews, job search, or next skills to learn.")
    if not prompt:
        return

    st.session_state["coach_error"] = ""
    st.session_state["coach_status"] = "Thinking"
    st.session_state["coach_messages"].append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        try:
            with st.spinner("Thinking like your career coach..."):
                reply = career_coach_reply(
                    resume_text=st.session_state["resume_text"],
                    chat_history=st.session_state["coach_messages"][:-1],
                    user_message=prompt,
                )
            st.session_state["coach_status"] = "Responded"
            st.markdown(reply)
        except Exception as exc:
            reply = f"I hit an error while generating career advice: {exc}"
            st.session_state["coach_status"] = "Error"
            st.session_state["coach_error"] = reply
            st.error(reply)

    st.session_state["coach_messages"].append({"role": "assistant", "content": reply})

    with st.expander("Coach diagnostics"):
        st.write(
            {
                "resume_loaded": bool(st.session_state.get("resume_text")),
                "resume_filename": st.session_state.get("resume_filename"),
                "api_key_present": bool(os.getenv("OPENAI_API_KEY")),
                "message_count": len(st.session_state.get("coach_messages", [])),
                "status": st.session_state.get("coach_status"),
            }
        )


def render_sidebar() -> str:
    with st.sidebar:
        if LOGO_PATH.exists():
            st.image(str(LOGO_PATH), width=110)
        st.markdown("## Resume Genie")
        st.caption("A complete AI toolkit for resumes, job targeting, and career guidance.")
        handle_resume_upload()

        if st.session_state.get("resume_filename"):
            st.markdown(f"**Loaded resume:** `{st.session_state['resume_filename']}`")

        page = st.radio(
            "Choose a workspace",
            [
                "Resume Review",
                "Job Fit Analyzer",
                "Cover Letter",
                "AI Career Coach",
            ],
        )

        st.markdown("---")
        st.markdown("**Tips**")
        st.markdown("- Use PDF resumes with selectable text.")
        st.markdown("- Paste complete job descriptions for better results.")
        st.markdown("- Add your API key in `.env` as `OPENAI_API_KEY`.")

    return page


def run() -> None:
    st.set_page_config(
        page_title="Resume Genie",
        page_icon="📄",
        layout="wide",
        initial_sidebar_state="expanded",
    )
    init_state()
    inject_styles(LOGO_PATH)
    render_hero()

    page = render_sidebar()
    if page == "Resume Review":
        resume_review_page()
    elif page == "Job Fit Analyzer":
        job_match_page()
    elif page == "Cover Letter":
        cover_letter_page()
    else:
        career_coach_page()
