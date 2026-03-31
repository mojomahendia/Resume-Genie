import json
import os
import tempfile
from pathlib import Path
from typing import Any

from langchain_community.document_loaders import PyMuPDFLoader


def extract_pdf_text(uploaded_file: Any) -> str:
    suffix = Path(uploaded_file.name).suffix or ".pdf"
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as temp_file:
        temp_file.write(uploaded_file.getbuffer())
        temp_path = temp_file.name

    try:
        documents = PyMuPDFLoader(temp_path).load()
        return "\n\n".join(doc.page_content for doc in documents).strip()
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)


def parse_json_response(raw_output: str) -> dict[str, Any]:
    try:
        return json.loads(raw_output)
    except json.JSONDecodeError:
        start = raw_output.find("{")
        end = raw_output.rfind("}")
        if start != -1 and end != -1 and end > start:
            return json.loads(raw_output[start : end + 1])
        raise ValueError("The model returned an invalid JSON response.")
