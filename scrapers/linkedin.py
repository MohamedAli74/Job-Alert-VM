import logging
import requests
from .base import JobResult

logger = logging.getLogger(__name__)

_HEADERS = {
    "User-Agent":      "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 "
                       "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Accept":          "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Referer":         "https://www.linkedin.com/",
}

_URL = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"


def scrape(source: dict) -> list[JobResult]:
    """
    Uses LinkedIn's unauthenticated guest job search API.

    Config example:
      - name: LinkedIn
        type: linkedin
        url: "https://www.linkedin.com/jobs"
        keywords: "software intern"
        location: "Israel"
        remote_only: false   # optional
    """
    from bs4 import BeautifulSoup

    keywords = source.get("keywords", "software intern")
    location = source.get("location", "")

    params: dict = {"keywords": keywords, "location": location, "start": "0"}
    if source.get("remote_only"):
        params["f_WT"] = "2"

    try:
        resp = requests.get(_URL, params=params, headers=_HEADERS, timeout=15)
        resp.raise_for_status()
    except Exception:
        logger.exception("LinkedIn request failed")
        return []

    soup    = BeautifulSoup(resp.text, "html.parser")
    results = []
    for card in soup.select("li"):
        title_el   = card.select_one(".base-search-card__title")
        company_el = card.select_one(".base-search-card__subtitle")
        loc_el     = card.select_one(".job-search-card__location")
        link_el    = card.select_one("a.base-card__full-link")
        if not title_el or not link_el:
            continue
        results.append(JobResult(
            source_name=source["name"],
            title=title_el.get_text(strip=True),
            url=link_el["href"].split("?")[0],
            company=company_el.get_text(strip=True) if company_el else None,
            location=loc_el.get_text(strip=True) if loc_el else None,
        ))
    return results
