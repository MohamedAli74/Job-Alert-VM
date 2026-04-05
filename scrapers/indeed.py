import logging
from .base import JobResult

logger = logging.getLogger(__name__)

# Country name → jobspy country_indeed value
_COUNTRY_MAP = {
    "uk": "UK", "united kingdom": "UK", "england": "UK", "london": "UK",
    "usa": "USA", "us": "USA", "united states": "USA",
    "canada": "CANADA", "australia": "AUSTRALIA",
    "germany": "GERMANY", "france": "FRANCE",
    "india": "INDIA",
}


def scrape(source: dict) -> list[JobResult]:
    """
    Uses python-jobspy to scrape Indeed.
    jobspy handles anti-bot measures internally.

    Config example:
      - name: Indeed UK
        type: indeed
        url: "https://www.indeed.com"
        keywords: "software intern"
        location: "United Kingdom"
        country: "UK"           # jobspy country code (default: UK)
        hours_old: 72           # optional, default 72
        results_wanted: 20      # optional, default 20
    """
    try:
        from jobspy import scrape_jobs
    except ImportError:
        logger.error("python-jobspy not installed. Run: pip install python-jobspy")
        return []

    keywords      = source.get("keywords", "software intern")
    location      = source.get("location", "United Kingdom")
    country_raw   = source.get("country", location)
    country       = _COUNTRY_MAP.get(country_raw.lower(), country_raw.upper())
    hours_old     = int(source.get("hours_old", 72))
    results_wanted = int(source.get("results_wanted", 20))

    try:
        df = scrape_jobs(
            site_name=["indeed"],
            search_term=keywords,
            location=location,
            results_wanted=results_wanted,
            hours_old=hours_old,
            country_indeed=country,
            verbose=0,
        )
    except Exception:
        logger.exception("Indeed (jobspy) scrape failed")
        return []

    if df is None or df.empty:
        return []

    results = []
    for _, row in df.iterrows():
        title = row.get("title")
        url   = row.get("job_url")
        if not title or not url:
            continue

        # jobspy puts skills/tags in description — extract first few words as hint
        desc = str(row.get("description") or "")
        skills = _extract_skills(desc)

        results.append(JobResult(
            source_name=source["name"],
            title=str(title).strip(),
            url=str(url).strip(),
            company=str(row.get("company") or "").strip() or None,
            location=str(row.get("location") or "").strip() or None,
            skills=skills,
        ))
    return results


_SKILL_KEYWORDS = [
    "python", "javascript", "typescript", "java", "c++", "c#", "go", "rust",
    "react", "node", "angular", "vue", "django", "flask", "spring",
    "aws", "azure", "gcp", "docker", "kubernetes", "sql", "postgresql",
    "machine learning", "deep learning", "pytorch", "tensorflow",
    "linux", "git", "rest", "graphql",
]


def _extract_skills(description: str) -> str | None:
    """Scan the job description for known tech keywords and return them comma-joined."""
    desc_lower = description.lower()
    found = [kw for kw in _SKILL_KEYWORDS if kw in desc_lower]
    return ", ".join(found) if found else None
