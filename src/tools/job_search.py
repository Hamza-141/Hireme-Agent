import requests
import urllib.parse
from src.config.settings import ADZUNA_APP_ID, ADZUNA_APP_KEY, ADZUNA_COUNTRY

def search_jobs(query: str, location: str, count: int) -> list:
    """Search Adzuna API for jobs."""
    try:
        url = f"https://api.adzuna.com/v1/api/jobs/{ADZUNA_COUNTRY}/search/1"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": count,
            "what": query,
            "where": location,
        }
        
        headers = {"Accept": "application/json"}
        response = requests.get(url, params=params, headers=headers)
        response.raise_for_status()
        
        data = response.json()
        results = data.get("results", [])
        
        if not results:
            print("[job_search] Warning: No results found or empty response.")
            return []
            
        job_listings = []
        for item in results:
            # Format salary
            min_sal = item.get("salary_min")
            max_sal = item.get("salary_max")
            if min_sal is not None and max_sal is not None:
                salary = f"{min_sal} - {max_sal}"
            elif min_sal is not None:
                salary = f"From {min_sal}"
            elif max_sal is not None:
                salary = f"Up to {max_sal}"
            else:
                salary = "Not specified"
                
            description = item.get("description", "")
            if len(description) > 600:
                description = description[:597] + "..."
                
            job_listings.append({
                "id": str(item.get("id", "")),
                "title": item.get("title", ""),
                "company": item.get("company", {}).get("display_name", ""),
                "location": item.get("location", {}).get("display_name", ""),
                "salary": salary,
                "description": description,
                "url": item.get("redirect_url", "")
            })
            
        print(f"[job_search] Found {len(job_listings)} jobs.")
        return job_listings
        
    except Exception as e:
        print(f"[job_search] Warning: API call failed - {e}")
        return []
