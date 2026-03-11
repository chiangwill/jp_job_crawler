import os
from supabase import create_client, Client
from scrapers.models import Job


def get_client() -> Client:
    url = os.environ["SUPABASE_URL"]
    key = os.environ["SUPABASE_KEY"]
    return create_client(url, key)


def get_existing_ids(client: Client) -> set[str]:
    res = client.table("jobs").select("id").execute()
    return {row["id"] for row in res.data}


def save_new_jobs(client: Client, jobs: list[Job]) -> list[Job]:
    """Insert jobs that don't exist yet. Returns only the newly inserted ones."""
    if not jobs:
        return []

    existing_ids = get_existing_ids(client)
    seen: set[str] = set()
    new_jobs = []
    for j in jobs:
        if j.id not in existing_ids and j.id not in seen:
            seen.add(j.id)
            new_jobs.append(j)

    if not new_jobs:
        return []

    rows = [
        {
            "id": j.id,
            "source": j.source,
            "title": j.title,
            "company": j.company,
            "url": j.url,
            "location": j.location,
            "salary_min": j.salary_min,
            "salary_max": j.salary_max,
            "japanese_level": j.japanese_level,
            "remote_level": j.remote_level,
            "candidate_location": j.candidate_location,
            "sponsors_visas": j.sponsors_visas,
            "skills": j.skills,
            "published_at": j.published_at,
            "notified": False,
        }
        for j in new_jobs
    ]

    client.table("jobs").insert(rows).execute()
    return new_jobs


def mark_notified(client: Client, job_ids: list[str]) -> None:
    if not job_ids:
        return
    client.table("jobs").update({"notified": True}).in_("id", job_ids).execute()
