import requests
from src.config.settings import ADZUNA_APP_ID, ADZUNA_APP_KEY, ADZUNA_COUNTRY
from src.tools.location_resolver import resolve_location


def search_jobs(query: str, location: str, count: int, country_code: str = None) -> list:
    """Search Adzuna API for jobs.

    Args:
        query: Job title / keywords to search.
        location: City or region (passed as `where` to Adzuna).
        count: Number of results to request.
        country_code: Two-letter Adzuna country code (auto-resolved from location if not given).
    """
    try:
        # Resolve country from location if not explicitly provided
        if not country_code:
            country_code, _ = resolve_location(location)

        url = f"https://api.adzuna.com/v1/api/jobs/{country_code}/search/1"
        params = {
            "app_id": ADZUNA_APP_ID,
            "app_key": ADZUNA_APP_KEY,
            "results_per_page": count,
            "what": query,
            "where": location,
            "content-type": "application/json",
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
                salary = f"{int(min_sal):,} - {int(max_sal):,}"
            elif min_sal is not None:
                salary = f"From {int(min_sal):,}"
            elif max_sal is not None:
                salary = f"Up to {int(max_sal):,}"
            else:
                salary = "Not specified"

            # Description — give the agent a full 1000 chars so it can write
            # a proper cover letter without needing to scrape the employer site.
            description = item.get("description", "")
            if len(description) > 1000:
                description = description[:997] + "..."

            # Contract details
            contract_type = item.get("contract_type", "")
            contract_time = item.get("contract_time", "")
            if contract_type and contract_time:
                contract = f"{contract_type.title()} / {contract_time.title()}"
            elif contract_type:
                contract = contract_type.title()
            elif contract_time:
                contract = contract_time.title()
            else:
                contract = "Not specified"

            # Posting date (ISO string from Adzuna, e.g. "2025-06-20T12:00:00Z")
            created_raw = item.get("created", "")
            created = created_raw[:10] if created_raw else "Unknown"

            redirect_url = item.get("redirect_url", "").strip()

            # Skip jobs with no redirect URL — they lead to dead pages
            if not redirect_url:
                continue

            job_listings.append({
                "id": str(item.get("id", "")),
                "title": item.get("title", ""),
                "company": item.get("company", {}).get("display_name", ""),
                "location": item.get("location", {}).get("display_name", ""),
                "salary": salary,
                "contract": contract,
                "posted": created,
                "description": description,
                "url": redirect_url,
            })

        print(f"[job_search] Found {len(job_listings)} jobs.")
        return job_listings

    except Exception as e:
        print(f"[job_search] Warning: API call failed - {e}")
        return []
