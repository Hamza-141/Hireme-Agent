import json
import re
from openai import OpenAI
from src.config.settings import GROQ_API_KEY
from src.memory.cv_store import get_cv
from src.tools.tool_registry import TOOL_DEFINITIONS, execute_tool

# ── Groq / Llama client ───────────────────────────────────────────────────────

_client = OpenAI(api_key=GROQ_API_KEY, base_url="https://api.groq.com/openai/v1")


def _strip_markdown(text: str) -> str:
    """Remove markdown code fences that the LLM may wrap around JSON."""
    pattern = r"^```(?:json)?\s*\n?(.*?)\n?```$"
    match = re.match(pattern, text, re.DOTALL)
    if match:
        return match.group(1).strip()
    return text.strip()


def run_agent(location: str, count: int) -> list:
    """Run the job hunting agent loop."""

    cv_data = get_cv()
    if not cv_data:
        raise ValueError("No CV has been loaded yet.")

    system_prompt = """You are a job hunting assistant. Follow this exact sequence:

1. Look at the candidate's preferred roles and skills. Pick ONE single concise job title
   that best represents them. Use it as the search query.
   - Good: "AI Engineer", "Data Analyst", "Backend Developer"
   - Bad: "AI Engineer, Software Engineer" or "experienced python developer with ml skills"
   This is a hard rule. ONE job title only.

2. Call search_jobs ONCE using that single job title, the provided location, and count.

3. From the results, select the top jobs (up to the count requested).

4. For each job, write a tailored cover letter using:
   - The job's title, company, location, salary, and description fields from the search results.
   - You do NOT need to call scrape_job. The description from search_jobs is sufficient.

Cover letter rules:
- Address the specific company and job title by name.
- Only use skills and experience actually present in the CV.
- Write exactly 3 paragraphs: opening, value pitch, closing.
- Use a professional but warm tone.
- Never fabricate anything not in the CV.
- Never use generic filler phrases like "I am writing to apply".

Return your final response as a raw JSON array ONLY — no markdown, no explanation.
Each item in the array must contain:
{
  "job_title": "...",
  "company": "...",
  "location": "...",
  "salary": "...",
  "contract": "...",
  "posted": "...",
  "job_url": "...",
  "cover_letter": "..."
}
"""

    user_message_content = f"""
Candidate Details:
- Name: {cv_data.get('name')}
- Skills: {', '.join(cv_data.get('skills', []))}
- Preferred Roles: {', '.join(cv_data.get('preferred_roles', []))}
- Experience: {json.dumps(cv_data.get('experience', []), indent=2)}
- Education: {json.dumps(cv_data.get('education', []), indent=2)}
- Summary: {cv_data.get('summary')}

Search Requirements:
- Location: {location}
- Number of results to request: {count}

Instruction:
Pick ONE concise search query (a single job title) and call search_jobs immediately.
After getting results, write cover letters using the description field — do NOT call scrape_job.
"""

    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": user_message_content}
    ]

    max_iterations = 15

    for i in range(max_iterations):
        print(f"[hire_agent] Starting iteration {i+1}/{max_iterations}")

        response = _client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            tools=TOOL_DEFINITIONS,
            tool_choice="auto",
            temperature=0.3
        )

        message = response.choices[0].message

        # Append the assistant's message to the history
        assistant_message = {"role": "assistant"}
        if message.content is not None:
            assistant_message["content"] = message.content
        if message.tool_calls:
            assistant_message["tool_calls"] = []
            for tc in message.tool_calls:
                assistant_message["tool_calls"].append({
                    "id": tc.id,
                    "type": tc.type,
                    "function": {
                        "name": tc.function.name,
                        "arguments": tc.function.arguments
                    }
                })

        if "content" not in assistant_message and "tool_calls" not in assistant_message:
            assistant_message["content"] = ""

        messages.append(assistant_message)

        if message.tool_calls:
            for tool_call in message.tool_calls:
                tool_name = tool_call.function.name
                arguments = tool_call.function.arguments
                print(f"[hire_agent] Model called tool: {tool_name}")

                try:
                    args_dict = json.loads(arguments)
                except json.JSONDecodeError:
                    args_dict = {}

                result_str = execute_tool(tool_name, args_dict)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "name": tool_name,
                    "content": result_str
                })
            continue  # Continue to the next iteration to send tool results
        else:
            # No tool calls — this is the final response
            final_content = message.content or ""
            cleaned_content = _strip_markdown(final_content)
            try:
                results_list = json.loads(cleaned_content)
                print("[hire_agent] Successfully generated final response.")
                return results_list
            except json.JSONDecodeError as e:
                raise ValueError(
                    f"Failed to parse final response as JSON. Error: {e}\n"
                    f"Raw output: {cleaned_content}"
                )

    raise RuntimeError(
        f"Agent loop exceeded maximum iterations ({max_iterations}) without returning a final response."
    )


