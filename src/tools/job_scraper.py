import requests
import re
from bs4 import BeautifulSoup

def scrape_job(url: str) -> str:
    """Fetch job listing URL and return cleaned text."""
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        }
        print(f"[job_scraper] Scraping URL: {url}")
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        # Extract only the job description section (adp-body), not the whole page

        soup = BeautifulSoup(response.text, "html.parser")
        box = soup.find("section", class_="adp-body")
        text = box.get_text(separator=" ", strip=True) if box else ""
        
        # Collapse whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text[:1500]
    except Exception as e:
        print(f"[job_scraper] Error scraping URL: {e}")
        return "The details could not be fetched."
