# PLAN.md — HireMe Agent

**Last Updated:** Current Session (July 2026)

**Source of Truth:** Active Project Plan & Agent Handoff Reference

---

## Project Purpose

**Core App:** AI-powered job matching tool. Upload CV → Parse → Agent loop searches live jobs (Adzuna) → Generates tailored cover letters via LLM.

**Target Audience:** Demo-ready portfolio project for LinkedIn/interviews.

**Owner Profile:** 2nd-year Software Engineering student (Pakistan). Intermediate Python, familiar with Streamlit, Flask, Django, Git.

**Core Goal:** Owner must deeply understand every component well enough to explain it thoroughly in technical interviews.

---

## Architecture & Key Decisions

- **UI Frontend:** Streamlit using `st.session_state["stage"]` (upload and results) for step-based navigation.
- **LLM Core:** Groq API running `llama-3.3-70b-versatile` via OpenAI Python SDK wrappers. Handles parsing and agent loops.
- **Job Data Fetching:** Adzuna API (`job_search.py`) covering 12 countries. `location_resolver.py` maps free text to codes; falls back to `gb` with a UI warning.
- **State & Memory:** `src/memory/cv_store.py` currently holds parsed CVs in a module-level global variable (Multi-user vulnerability).
- **Agent Logic:** `hire_agent.py` runs an OpenAI-style function calling loop (max 15 iterations).
- **File Handling:** PyMuPDF (`fitz`) for PDFs, `python-docx` for Word files. Processes via temporary files.
- **Hosting Deployment:** Streamlit Community Cloud with `st.secrets` falling back to local `.env`.

---

## Active Task: Upgrade `job_scraper.py` via BeautifulSoup

**Context:** Adzuna truncates job descriptions to exactly 500 characters in the search payload. Full data lives on the `redirect_url` inside `<section class="adp-body ...">`.

**Current State:** `scrape_job` is currently registered but disabled via system prompt instructions, making changes completely zero-risk to the main loop.

### 10-Phase Implementation Progress

- [x] **Phase 1:** Confirm baseline (500-char snippets active, tool unused)
- [x] **Phase 2:** Add `beautifulsoup4` to `requirements.txt` and install (pip restored via force-reinstall)
- [ ] **Phase 3 (CURRENT STEP):** Test extraction on 2–3 real Adzuna URLs using a scratch script to confirm target class reliability.
- [ ] **Phase 4:** Create Git safety net branch/commit for `job_scraper.py`
- [ ] **Phase 5:** Targeted file edit replacing regex tag stripping with explicit soup parsing logic:

  ```python
  from bs4 import BeautifulSoup
  soup = BeautifulSoup(response.text, "html.parser")
  description_box = soup.find("section", class_="adp-body")
  text = description_box.get_text(separator=" ", strip=True)
  ```

- [ ] **Phase 6:** Isolate test `scrape_job()` outside Streamlit environment
- [ ] **Phase 7:** Implement `NoneType` guard for external redirect edge cases to prevent `AttributeError` crashes
- [ ] **Phase 8:** Formally decide on re-enabling tool loop logic in `hire_agent.py` system prompts (weighing latency costs)
- [ ] **Phase 9:** Conduct end-to-end local integration testing in the Streamlit runtime
- [ ] **Phase 10:** Deploy to Streamlit Cloud and outline validation/rollback steps

---

## Other Backlog Tasks & Known Issues

### High Priority

- **Multi-user Data Bug:** Global storage in `cv_store.py` shares CV data across all active web instances simultaneously. Must migrate to `st.session_state` before public portfolio presentation.

### Documentation & Maintenance

- **Config/Docs Mismatch:** `README.md` and `.env.example` wrongly reference `OPENAI_API_KEY`. The code actually looks for `GROQ_API_KEY`. Fix on an independent branch.
- **Repository Clutter:** Delete or document standalone debugging files: `test_gemini.py`, `test_import.py` (contains hardcoded local paths), and empty `out.txt`.

### Unresolved Anomalies

- **Regional Search Bug:** Querying with `gb` (United Kingdom) parameters returned a Jersey City, NJ, USA job rendering an Adzuna "not available in your region" warning page. Requires future diagnosis.

---

## Technical Environment & Working Rules

### Workspace Blueprint

- **OS/Shell:** Windows, VS Code, Git Bash.
- **Package Management:** Run execution commands safely via `python -m pip` to protect system environment links.
- **Version Control:** Strictly one Git branch per isolated task. Clear, manual commit narratives. No auto-commit habits.

### Working with the AI Agent

- **Explain WHY before HOW.** Do not accept code changes without an accompanying explanation of the underlying logic.
- **Granular Edits Only.** Targeted adjustments are preferred over complete file rewrites.
- **Format for Scannability.** Information must remain accessible via lists, bold text, and brief technical checkpoints. Avoid massive walls of prose.

---

## Recommended Learning Sequence

To master the codebase for interviews, review components in this sequence:

1. Streamlit Session State Configuration
2. CV File Parsing Pipeline
3. Agent Execution Loop Architecture
4. Tool Selection & Function Calling Framework
5. Frontend UI Presentation Files