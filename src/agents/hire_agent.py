import json
import re
from openai import OpenAI
from src.config.settings import GROQ_API_KEY
from src.memory.cv_store import get_cv
from src.tools.tool_registry import TOOL_DEFINITIONS, execute_tool

# ── OpenAI client ────────────────────────────────────────────────────────────

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
        
    system_prompt = """You are a job hunting assistant. You must always follow this exact sequence:
1. Look at the candidate's preferred roles and skills and pick ONE single concise job title that best represents them.
   This will be used as the search query.
   The query must be short and specific, exactly how a job title appears on a job board.
   Good examples: "AI Engineer", "Data Analyst", "Backend Developer"
   Bad examples: "AI Engineer, Software Engineer, Backend Developer" or "experienced python developer with ml skills"
   This is a hard rule. Never pass multiple roles or a long string as the search query.
2. Call search_jobs once using that single concise job title as the query and the location and count provided by the user.
3. Pick the top 3 jobs from the results.
4. Call scrape_job for each of those 3 jobs to fetch their details.
5. Write a tailored cover letter for each job after fetching details.

Cover letter rules:
- Address the specific company and job title by name
- Only use skills and experience actually present in the CV
- Write exactly 3 paragraphs: opening, value pitch, closing
- Use a professional but warm tone
- Never fabricate anything not in the CV
- Never use generic filler phrases like "I am writing to apply"

Return your final response as a raw JSON array only, with no markdown and no explanation, where each item contains:
{
  "job_title": "...",
  "company": "...",
  "location": "...",
  "salary": "...",
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
Begin by picking ONE concise search query (a single job title) and call search_jobs immediately.
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
        # We must include tool_calls if they exist
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
        
        # If there's neither content nor tool calls, it's an empty response (edge case)
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
            continue # Continue to the next iteration to send tool results
        else:
            # No tool calls, this must be the final response
            final_content = message.content or ""
            cleaned_content = _strip_markdown(final_content)
            try:
                results_list = json.loads(cleaned_content)
                print("[hire_agent] Successfully generated final response.")
                return results_list
            except json.JSONDecodeError as e:
                # If parsing fails, we could potentially raise or retry, 
                # but the instructions say to strip formatting, parse JSON, and return the list.
                # If it's not valid JSON, we will raise an error.
                raise ValueError(f"Failed to parse final response as JSON. Error: {e}\nRaw output: {cleaned_content}")

    # If the loop finishes without returning
    raise RuntimeError(f"Agent loop exceeded maximum iterations ({max_iterations}) without returning a final response.")
