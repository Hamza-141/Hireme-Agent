import requests
import re

def scrape_job(url: str) -> str:
    """Fetch job listing URL and return cleaned text."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        print(f"[job_scraper] Scraping URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Strip HTML tags
        text = re.sub(r'<[^>]+>', ' ', response.text)
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:1500]
    except Exception as e:
        print(f"[job_scraper] Error scraping URL: {e}")
        return "The details could not be fetched."
