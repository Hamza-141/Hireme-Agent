"""CV structured parsing using GPT-4o and main ingest pipeline."""

import json
import re

from openai import OpenAI

from src.config.settings import GROQ_API_KEY
from src.memory.cv_store import save_cv
from src.parsers.cv_extractor import extract_text

# ── OpenAI client ────────────────────────────────────────────────────────────

_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")

_SYSTEM_PROMPT = """\
You are an expert CV / résumé parser.
Given the raw text of a CV, extract the information into a single JSON object.
Return ONLY the raw JSON — no markdown, no explanation, no code fences.

The JSON must contain exactly these keys:
{
  "name": "string",
  "email": "string or null",
  "phone": "string or null",
  "location": "string or null",
  "summary": "brief professional summary string",
  "skills": ["list", "of", "skills"],
  "experience": [
    {
      "title": "job title",
      "company": "company name",
      "duration": "e.g. Jan 2020 – Mar 2023",
      "description": "brief description of responsibilities"
    }
  ],
  "education": [
    {
      "degree": "degree name",
      "institution": "school or university",
      "year": "graduation year or range"
    }
  ],
  "preferred_roles": ["inferred list of roles the candidate would suit"],
  "preferred_industries": ["inferred list of industries the candidate fits"]
}

If a field cannot be determined, use null for strings or an empty list for arrays.
Infer preferred_roles and preferred_industries from the candidate's background.\
"""


# ── Public API ───────────────────────────────────────────────────────────────


def parse_cv(raw_text: str) -> dict:
    """Send raw CV text to GPT-4o and return a structured dict.

    Args:
        raw_text: The full plain-text content of a CV.

    Returns:
        A dict with the parsed CV fields.

    Raises:
        ValueError: If the LLM response cannot be parsed as valid JSON.
    """
    response = _client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": _SYSTEM_PROMPT},
            {"role": "user", "content": raw_text},
        ],
        temperature=0.0,
    )

    content = response.choices[0].message.content.strip()

    # Strip accidental markdown code fences the model might add.
    content = _strip_markdown(content)

    try:
        parsed = json.loads(content)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Failed to parse LLM response as JSON.\n"
            f"JSONDecodeError: {exc}\n"
            f"Raw response:\n{content}"
        ) from exc

    print(f"[cv_parser] Successfully parsed CV for: {parsed.get('name', 'unknown')}")
    return parsed


def ingest(uploaded_file) -> dict:
    """End-to-end pipeline: extract → parse → store.

    This is the single entry-point the UI should call.

    Args:
        uploaded_file: A Streamlit ``UploadedFile`` object.

    Returns:
        The parsed CV dict (also saved to cv_store).
    """
    raw_text = extract_text(uploaded_file)
    cv_data = parse_cv(raw_text)
    save_cv(cv_data)
    return cv_data


# ── Private helpers ──────────────────────────────────────────────────────────


def _strip_markdown(text: str) -> str:
    """Remove markdown code fences that the LLM may wrap around JSON."""
    # Matches ```json ... ``` or ``` ... ```
    pattern = r"^```(?:json)?\s*\n?(.*?)\n?```$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text
