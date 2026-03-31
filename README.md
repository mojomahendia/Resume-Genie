# Resume Genie

Resume Genie is a complete Streamlit application for:

- Resume review and scoring
- Resume vs job description matching
- Tailored cover letter generation
- AI-powered career coaching

## Run locally

1. Add your API key to a `.env` file:

```bash
OPENAI_API_KEY=your_key_here
```

2. Install dependencies:

```bash
pip install -r requirement.txt
```

3. Start the app:

```bash
streamlit run streamlit_app.py
```

## Project structure

- `streamlit_app.py`: Streamlit entry point
- `app/app.py`: Main application flow
- `app/services.py`: LLM integration and feature logic
- `app/parsers.py`: PDF extraction and JSON parsing helpers
- `app/prompts.py`: Prompt templates for all AI features
- `app/ui.py`: Shared visual components and theme

## Notes

- Upload PDF resumes with selectable text for the best results.
- The included `logo.png` is used throughout the UI.
