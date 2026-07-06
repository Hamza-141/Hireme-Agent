# PLAN.md — HireMe Agent

Last updated: July 07, 2026

## Current Goal
HireMe Agent is an AI-powered job matching tool: a user uploads their CV, the app parses it, searches live job listings via Adzuna, and generates tailored cover letters using an LLM. It works end-to-end from a hackathon build. Current stage: cleaning up and hardening the existing code before using it as a portfolio/interview project — no new features have been agreed on yet.

## Architecture / Key Decisions
- **UI**: Streamlit, two "pages" controlled by `st.session_state["stage"]` (`upload` and `results`), no real routing library.
- **LLM**: Groq API running `llama-3.3-70b-versatile`, accessed through the OpenAI Python SDK pointed at Groq's base URL. Used for both CV parsing (`cv_parser.py`) and the job-hunting agent loop (`hire_agent.py`).
- **Job data**: Adzuna API (`job_search.py`), limited to 12 supported countries. `location_resolver.py` maps free-text locations to Adzuna country codes and falls back to `gb` with a UI warning if the location isn't supported.
- **CV storage**: `src/memory/cv_store.py` holds the parsed CV in a plain Python module-level global variable (not `st.session_state`, not a database).
- **Agent tool loop**: `hire_agent.py` uses OpenAI-style function calling (`tool_choice="auto"`, max 15 iterations). Two tools are registered (`search_jobs`, `scrape_job`), but the system prompt explicitly tells the model to skip `scrape_job` and use the description field from `search_jobs` results instead.
- **File parsing**: Only PDF (via PyMuPDF/`fitz`) and DOCX (via `python-docx`) are supported; files are extracted through a temp file that's deleted afterward.
- **Hosting**: Streamlit Community Cloud, secrets read via `st.secrets` first, falling back to `.env` locally.

## Active Tasks
- [ ] Decide whether to keep `scrape_job` (dead code — registered as a tool but never called) or remove it, since it adds confusion without being used
- [ ] Move CV storage from a module-level global to `st.session_state`, since a global variable is shared across *all* users on a deployed app, not per-user
- [ ] Fix `README.md`: it documents `OPENAI_API_KEY` as required, but the app actually reads `GROQ_API_KEY` — anyone following the README setup will fail
- [ ] Remove or explain leftover dev files not part of the actual app: `test_gemini.py`, `test_import.py` (hardcoded Windows path), `out.txt` (empty)
- [ ] Review Adzuna's 12-country limitation and decide if the silent fallback-to-UK behavior is the right UX or needs rethinking

## Known Issues / Blockers
- **Multi-user data bug**: `cv_store.py`'s global variable means if two people use the deployed app at the same time, one user's CV can overwrite another's. This is the most important correctness issue to fix before treating this as demo-ready for multiple simultaneous users.
- **Dead code**: `scrape_job` / `job_scraper.py` is fully implemented and registered in `TOOL_DEFINITIONS`, but the agent is instructed never to use it. Either it should be wired in for real, or removed to avoid confusing anyone reading the code.
- **Docs mismatch**: `README.md` and `.env` example reference `OPENAI_API_KEY`; actual code (`settings.py`) requires `GROQ_API_KEY`. This will break onboarding for anyone else trying to run the project.
- **Repo clutter**: `test_gemini.py`, `test_import.py`, and `out.txt` look like debugging leftovers rather than part of the real app, and would look unpolished in a portfolio/interview context.

## Recent Changes
- This is the first PLAN.md for the project. It was generated from a full review of the existing codebase (no prior planning conversation existed yet). Nothing has been changed in the code yet — this file just captures the current state and the issues found so we have a shared reference to work from.
