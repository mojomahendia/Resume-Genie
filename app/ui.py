import base64
from pathlib import Path

import streamlit as st


def _encoded_logo(logo_path: Path) -> str:
    return base64.b64encode(logo_path.read_bytes()).decode("utf-8")


def inject_styles(logo_path: Path) -> None:
    logo_css = ""
    if logo_path.exists():
        logo_css = f"""
        .brand-badge::before {{
            content: "";
            width: 50px;
            height: 50px;
            border-radius: 16px;
            background-image: url("data:image/png;base64,{_encoded_logo(logo_path)}");
            background-size: cover;
            background-position: center;
            box-shadow: 0 14px 28px rgba(15, 23, 42, 0.16);
            flex-shrink: 0;
        }}
        """

    st.markdown(
        f"""
        <style>
        @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

        :root {{
            --bg: #f4efe7;
            --bg-soft: #fbf8f3;
            --ink: #172033;
            --muted: #5e6779;
            --accent: #c2612d;
            --accent-strong: #a94717;
            --teal: #0e7490;
            --line: rgba(23, 32, 51, 0.08);
            --glass: rgba(255, 255, 255, 0.76);
            --shadow: 0 20px 45px rgba(23, 32, 51, 0.08);
        }}
        html, body, [class*="css"] {{
            font-family: 'Plus Jakarta Sans', sans-serif;
        }}
        .stApp {{
            background:
                radial-gradient(circle at 0% 0%, rgba(194, 97, 45, 0.18), transparent 26%),
                radial-gradient(circle at 100% 10%, rgba(14, 116, 144, 0.14), transparent 24%),
                linear-gradient(180deg, var(--bg) 0%, var(--bg-soft) 55%, #eef4f8 100%);
        }}
        .main .block-container {{
            padding-top: 1.6rem;
            padding-bottom: 3rem;
            max-width: 1200px;
        }}
        [data-testid="stSidebar"] {{
            background: linear-gradient(180deg, #192236 0%, #101726 100%);
            border-right: 1px solid rgba(255, 255, 255, 0.06);
        }}
        [data-testid="stSidebar"] * {{
            color: #f6f8fb;
        }}
        .brand-hero,
        .glass-card,
        .metric-card,
        .chat-shell {{
            background: var(--glass);
            border: 1px solid var(--line);
            border-radius: 26px;
            box-shadow: var(--shadow);
            backdrop-filter: blur(14px);
        }}
        .brand-hero {{
            padding: 1.6rem;
            margin-bottom: 1.2rem;
        }}
        .brand-layout {{
            display: flex;
            justify-content: space-between;
            gap: 1.5rem;
            align-items: center;
        }}
        .brand-copy {{
            flex: 1;
        }}
        .eyebrow {{
            display: inline-block;
            color: var(--accent);
            text-transform: uppercase;
            letter-spacing: 0.12em;
            font-weight: 800;
            font-size: 0.78rem;
            margin-bottom: 0.85rem;
        }}
        .hero-title {{
            color: var(--ink);
            font-size: 2.8rem;
            line-height: 1.02;
            font-weight: 800;
            margin: 0 0 0.75rem 0;
            max-width: 11ch;
        }}
        .hero-text {{
            color: var(--muted);
            line-height: 1.7;
            font-size: 1.02rem;
            max-width: 50rem;
            margin: 0;
        }}
        .brand-badge {{
            min-width: 220px;
            display: flex;
            align-items: center;
            gap: 0.9rem;
            padding: 1rem 1.1rem;
            border-radius: 22px;
            background: linear-gradient(180deg, rgba(255,255,255,0.82), rgba(250, 245, 236, 0.94));
            border: 1px solid rgba(194, 97, 45, 0.16);
        }}
        {logo_css}
        .brand-badge strong {{
            color: var(--ink);
            display: block;
            font-size: 1.05rem;
            margin-bottom: 0.15rem;
        }}
        .brand-badge span {{
            color: var(--muted);
            font-size: 0.92rem;
        }}
        .section-card {{
            padding: 1.25rem 1.3rem;
            margin-bottom: 1rem;
        }}
        .section-title {{
            color: var(--ink);
            font-weight: 800;
            font-size: 1.18rem;
            margin-bottom: 0.3rem;
        }}
        .section-copy {{
            color: var(--muted);
            margin-bottom: 0.8rem;
        }}
        .metric-card {{
            padding: 1.2rem 1.25rem;
            min-height: 148px;
        }}
        .metric-label {{
            text-transform: uppercase;
            letter-spacing: 0.1em;
            font-size: 0.76rem;
            color: rgba(23, 32, 51, 0.55);
            font-weight: 800;
            margin-bottom: 0.7rem;
        }}
        .metric-value {{
            color: var(--ink);
            font-size: 2.5rem;
            line-height: 1;
            font-weight: 800;
            margin-bottom: 0.55rem;
        }}
        .metric-note {{
            color: var(--muted);
            line-height: 1.6;
            font-size: 0.95rem;
        }}
        .pill {{
            display: inline-flex;
            align-items: center;
            padding: 0.4rem 0.7rem;
            border-radius: 999px;
            background: rgba(194, 97, 45, 0.12);
            color: var(--accent-strong);
            font-weight: 700;
            font-size: 0.86rem;
            margin: 0 0.4rem 0.45rem 0;
        }}
        .rich-card {{
            padding: 1.15rem 1.2rem;
            height: 100%;
        }}
        .rich-card h3 {{
            color: var(--ink);
            font-size: 1.02rem;
            margin: 0 0 0.75rem 0;
        }}
        .rich-card p, .rich-card li {{
            color: var(--muted);
            line-height: 1.65;
            font-size: 0.96rem;
        }}
        .rich-card ul {{
            margin: 0;
            padding-left: 1.1rem;
        }}
        .chat-shell {{
            padding: 0.8rem;
            margin-top: 0.7rem;
        }}
        [data-testid="stChatMessage"] {{
            border-radius: 22px;
            padding: 0.2rem 0.35rem;
            margin-bottom: 0.8rem;
        }}
        [data-testid="stChatMessageContent"] {{
            border: 1px solid var(--line);
            border-radius: 20px;
            padding: 0.7rem 0.9rem;
            box-shadow: 0 12px 28px rgba(23, 32, 51, 0.06);
        }}
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] p,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] li,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] span,
        [data-testid="stChatMessage"] [data-testid="stMarkdownContainer"] div,
        [data-testid="stChatMessageContent"] {{
            color: var(--ink) !important;
        }}
        [data-testid="stChatMessageContent"][aria-label="Chat message from user"] {{
            background: linear-gradient(180deg, rgba(255, 242, 232, 0.98), rgba(252, 232, 214, 0.94)) !important;
            border-color: rgba(194, 97, 45, 0.2);
        }}
        [data-testid="stChatMessageContent"][aria-label="Chat message from assistant"] {{
            background: linear-gradient(180deg, rgba(239, 248, 251, 0.98), rgba(247, 251, 255, 0.94)) !important;
            border-color: rgba(14, 116, 144, 0.16);
        }}
        [data-testid="stChatInput"] {{
            background: transparent !important;
            border: none !important;
            box-shadow: none !important;
        }}
        [data-testid="stChatInput"] > div {{
            background: rgba(255, 255, 255, 0.96) !important;
            border: 1px solid var(--line) !important;
            border-radius: 18px !important;
            box-shadow: 0 12px 28px rgba(23, 32, 51, 0.08);
        }}
        [data-testid="stChatInput"] textarea {{
            background: rgba(255, 255, 255, 0.96) !important;
            color: var(--ink) !important;
            caret-color: var(--accent-strong) !important;
            border-radius: 18px !important;
        }}
        [data-testid="stChatInput"] textarea::placeholder {{
            color: var(--ink) !important;
            opacity: 0.72;
        }}
        [data-testid="stChatInput"] button {{
            background: linear-gradient(135deg, var(--accent), #eb9048) !important;
            color: #ffffff !important;
            border-radius: 14px !important;
        }}
        [data-testid="stFileUploader"] {{
            border-radius: 18px;
            border: 1px dashed rgba(194, 97, 45, 0.42);
            background: rgba(255, 250, 244, 0.75);
        }}
        .stButton > button, .stDownloadButton > button {{
            border: none;
            border-radius: 14px;
            background: linear-gradient(135deg, var(--accent), #eb9048);
            color: white;
            font-weight: 800;
            padding: 0.8rem 1rem;
            box-shadow: 0 14px 28px rgba(194, 97, 45, 0.2);
        }}
        .stButton > button:hover, .stDownloadButton > button:hover {{
            background: linear-gradient(135deg, var(--accent-strong), #db7a2e);
        }}
        @media (max-width: 900px) {{
            .brand-layout {{
                flex-direction: column;
                align-items: flex-start;
            }}
            .hero-title {{
                font-size: 2.2rem;
                max-width: none;
            }}
            .brand-badge {{
                min-width: 0;
                width: 100%;
            }}
        }}
        </style>
        """,
        unsafe_allow_html=True,
    )


def render_hero() -> None:
    st.markdown(
        """
        <div class="brand-hero">
            <div class="brand-layout">
                <div class="brand-copy">
                    <div class="eyebrow">AI Career Suite</div>
                    <h1 class="hero-title">Build sharper resumes and job applications.</h1>
                    <p class="hero-text">
                        Resume Genie turns your resume into a full AI workspace: review your profile,
                        compare it against job descriptions, generate tailored cover letters, and get
                        real-time career coaching from a single beautiful dashboard.
                    </p>
                </div>
                <div class="brand-badge">
                    <div>
                        <strong>Resume Genie</strong>
                        <span>Smart resume analysis, matching, writing, and coaching.</span>
                    </div>
                </div>
            </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_section_intro(title: str, copy: str) -> None:
    st.markdown(
        f"""
        <div class="glass-card section-card">
            <div class="section-title">{title}</div>
            <div class="section-copy">{copy}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_metric(label: str, value: str, note: str) -> None:
    st.markdown(
        f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-note">{note}</div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_list_card(title: str, items: list[str]) -> None:
    bullet_items = "".join(f"<li>{item}</li>" for item in items) or "<li>No items available.</li>"
    st.markdown(
        f"""
        <div class="glass-card rich-card">
            <h3>{title}</h3>
            <ul>{bullet_items}</ul>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_text_card(title: str, body: str) -> None:
    st.markdown(
        f"""
        <div class="glass-card rich-card">
            <h3>{title}</h3>
            <p>{body}</p>
        </div>
        """,
        unsafe_allow_html=True,
    )


def render_pills(items: list[str]) -> None:
    pills = "".join(f'<span class="pill">{item}</span>' for item in items) or '<span class="pill">None</span>'
    st.markdown(pills, unsafe_allow_html=True)
