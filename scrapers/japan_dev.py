import httpx
from .models import Job

MEILI_URL = "https://meili.japan-dev.com/multi-search"
MEILI_TOKEN = "3838486cea4344beaef2c4c5979be249fc5736ea4aab99fab193b5e7f540ffae"
JOB_BASE_URL = "https://japan-dev.com/jobs"
PAGE_SIZE = 100

# Filterable fields and their valid values:
#   visa_only:           true | false  (shorthand for sponsors_visas = sponsors_visas_yes)
#   japanese_level_enum: japanese_level_not_required | japanese_level_basic |
#                        japanese_level_conversational | japanese_level_business_level | japanese_level_fluent
#   remote_level:        remote_level_full | remote_level_partial | remote_level_no_remote
#   candidate_location:  candidate_location_anywhere | candidate_location_japan_only
#   seniority_level:     seniority_level_junior | seniority_level_mid_level |
#                        seniority_level_senior | seniority_level_lead
#   skill_names:         Backend | Frontend | Python | Go | DevOps | ... (free text, case-sensitive)


def _build_filter(filters: dict) -> str | None:
    clauses: list[str] = []

    if filters.get("visa_only", True):
        clauses.append("sponsors_visas = sponsors_visas_yes")

    # Multi-value fields → "field IN [v1, v2]"
    multi_fields = [
        "japanese_level_enum",
        "remote_level",
        "candidate_location",
        "seniority_level",
    ]
    for field in multi_fields:
        values = filters.get(field)
        if values:
            joined = ", ".join(values)
            clauses.append(f"{field} IN [{joined}]")

    # skill_names needs quotes around each value
    skills = filters.get("skill_names")
    if skills:
        joined = ", ".join(f'"{s}"' for s in skills)
        clauses.append(f"skill_names IN [{joined}]")

    return " AND ".join(clauses) if clauses else None


def _parse_hit(hit: dict) -> Job:
    return Job(
        id=f"japan_dev_{hit['id']}",
        source="japan_dev",
        title=hit["title"],
        company=hit["company_name"],
        url=f"{JOB_BASE_URL}/{hit['company']['slug']}/{hit['slug']}",
        location=hit.get("location"),
        salary_min=hit.get("salary_min"),
        salary_max=hit.get("salary_max"),
        japanese_level=hit.get("japanese_level"),
        remote_level=hit.get("remote_level"),
        candidate_location=hit.get("candidate_location"),
        sponsors_visas=hit.get("sponsors_visas") == "sponsors_visas_yes",
        skills=hit.get("skill_names", []),
        published_at=hit.get("published_at"),
    )


def fetch_jobs(filters: dict | None = None) -> list[Job]:
    if filters is None:
        filters = {"visa_only": True}

    meili_filter = _build_filter(filters)

    headers = {
        "Authorization": f"Bearer {MEILI_TOKEN}",
        "Content-Type": "application/json",
    }

    jobs: list[Job] = []
    offset = 0

    with httpx.Client() as client:
        while True:
            query: dict = {
                "indexUid": "Job_production",
                "q": "",
                "limit": PAGE_SIZE,
                "offset": offset,
            }
            if meili_filter:
                query["filter"] = meili_filter

            resp = client.post(MEILI_URL, headers=headers, json={"queries": [query]})
            resp.raise_for_status()

            result = resp.json()["results"][0]
            hits = result["hits"]
            if not hits:
                break

            jobs.extend(_parse_hit(h) for h in hits)

            offset += PAGE_SIZE
            if offset >= result["estimatedTotalHits"]:
                break

    return jobs
