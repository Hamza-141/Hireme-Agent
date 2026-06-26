import json
from src.tools.job_search import search_jobs
from src.tools.job_scraper import scrape_job

TOOL_DEFINITIONS = [
    {
        "type": "function",
        "function": {
            "name": "search_jobs",
            "description": "Searches the Adzuna API for job listings based on query, location, and count. Returns a list of job dictionaries.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "The job title or keywords to search for."
                    },
                    "location": {
                        "type": "string",
                        "description": "The location to search in (e.g., city name or country)."
                    },
                    "count": {
                        "type": "integer",
                        "description": "The number of job results to request."
                    }
                },
                "required": ["query", "location", "count"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "scrape_job",
            "description": "Fetches the full details of a job listing from a URL and returns cleaned text.",
            "parameters": {
                "type": "object",
                "properties": {
                    "url": {
                        "type": "string",
                        "description": "The URL of the job listing to scrape."
                    }
                },
                "required": ["url"]
            }
        }
    }
]

def execute_tool(tool_name: str, args: dict, country_code: str = None) -> str:
    """Executes a registered tool by name with the given arguments."""
    print(f"[tool_registry] Executing tool: {tool_name}")
    try:
        if tool_name == "search_jobs":
            result = search_jobs(
                args["query"],
                args["location"],
                args["count"],
                country_code=country_code,
            )
            return json.dumps(result)
        elif tool_name == "scrape_job":
            result = scrape_job(args["url"])
            return result
        else:
            return f"Error: Tool '{tool_name}' is not recognized."
    except Exception as e:
        return f"Error executing tool '{tool_name}': {str(e)}"
