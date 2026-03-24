import httpx
from bs4 import BeautifulSoup
from .models import Job

BASE_URL = "https://www.tokyodev.com"
JOBS_URL = f"{BASE_URL}/jobs"

# Available filter values:
#   japanese_requirement: none, basic, conversational, business, fluent
#   remote_policy:        fully_remote, partially_remote, no_remote
#   applicant_location:   apply_from_abroad, japan_residents_only
#   seniority:            intern, junior, intermediate, senior
#   category:             backend, frontend, devops, aws, python, ... (see site for full list)

EMERALD_TAGS = {
    "no-japanese-required",
    "basic-japanese",
    "conversational-japanese",
    "business-japanese",
    "fluent-japanese",
    "apply-from-abroad",
    "japan-residents-only",
    "fully-remote",
    "partially-remote",
    "no-remote",
}


def _parse_page(html: str) -> list[Job]:
    soup = BeautifulSoup(html, "lxml")
    jobs: list[Job] = []

    # Each <li> is a company block
    for company_li in soup.select("li[id]"):
        company_tag = company_li.select_one("h3 a")
        if not company_tag:
            continue
        company_name = company_tag.get_text(strip=True)

        # Each job under this company
        for item in company_li.select("[data-collapsable-list-target='item']"):
            title_tag = item.select_one("h4 a")
            if not title_tag:
                continue

            title = title_tag.get_text(strip=True)
            path = title_tag.get("href", "")
            url = f"{BASE_URL}{path}"
            job_id = path.split("/jobs/")[-1] if "/jobs/" in path else path

            # Parse badges
            tag_links = item.select("div.flex a.tag")
            skills: list[str] = []
            japanese_level = None
            remote_level = None
            candidate_location = None

            for tag in tag_links:
                href = tag.get("href", "").lstrip("/jobs/")
                text = tag.get_text(strip=True)

                if href in EMERALD_TAGS:
                    if "japanese" in href:
                        japanese_level = text
                    elif href in ("apply-from-abroad", "japan-residents-only"):
                        candidate_location = text
                    elif "remote" in href:
                        remote_level = text
                else:
                    skills.append(text)

            # Salary — shown as badge text like "¥7M ~ ¥12M"
            salary_min = salary_max = None
            salary_tag = item.select_one("a[href='/jobs/salary-data']")
            if salary_tag:
                raw = salary_tag.get_text(strip=True)  # e.g. "¥7M ~ ¥12M"
                parts = raw.replace("¥", "").replace("M", "").split("~")
                try:
                    salary_min = int(float(parts[0].strip()) * 1_000_000)
                    salary_max = int(float(parts[1].strip()) * 1_000_000)
                except (ValueError, IndexError):
                    pass

            jobs.append(Job(
                id=f"tokyo_dev_{job_id}",
                source="tokyo_dev",
                title=title,
                company=company_name,
                url=url,
                japanese_level=japanese_level,
                remote_level=remote_level,
                candidate_location=candidate_location,
                sponsors_visas=True,  # TokyoDev only lists visa-sponsoring companies
                skills=skills,
                salary_min=salary_min,
                salary_max=salary_max,
            ))

    return jobs


def fetch_jobs(
    japanese_requirement: list[str] | None = None,
    remote_policy: list[str] | None = None,
    applicant_location: list[str] | None = None,
    seniority: list[str] | None = None,
    category: list[str] | None = None,
) -> list[Job]:
    """
    Fetch jobs from TokyoDev with optional filters.

    Example:
        fetch_jobs(
            japanese_requirement=["none"],
            applicant_location=["apply_from_abroad"],
            remote_policy=["fully_remote", "partially_remote"],
        )
    """
    params: list[tuple[str, str]] = []
    for val in japanese_requirement or []:
        params.append(("japanese_requirement[]", val))
    for val in remote_policy or []:
        params.append(("remote_policy[]", val))
    for val in applicant_location or []:
        params.append(("applicant_location[]", val))
    for val in seniority or []:
        params.append(("seniority[]", val))
    for val in category or []:
        params.append(("category[]", val))

    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept-Encoding": "gzip, deflate, br",
    }

    with httpx.Client(follow_redirects=True) as client:
        resp = client.get(JOBS_URL, params=params, headers=headers)
        resp.raise_for_status()

    return _parse_page(resp.text)
