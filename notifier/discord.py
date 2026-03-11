import os
import httpx
from scrapers.models import Job

BATCH_SIZE = 10  # Discord embeds per message


def _format_salary(job: Job) -> str:
    if job.salary_min and job.salary_max:
        return f"¥{job.salary_min // 10_000}万 ~ ¥{job.salary_max // 10_000}万"
    return "N/A"


def _job_to_embed(job: Job) -> dict:
    source_label = "🇯🇵 Japan Dev" if job.source == "japan_dev" else "🗼 Tokyo Dev"
    skills = ", ".join(job.skills[:6]) or "N/A"

    fields = [
        {"name": "Company", "value": job.company, "inline": True},
        {"name": "Salary", "value": _format_salary(job), "inline": True},
        {"name": "Japanese", "value": job.japanese_level or "N/A", "inline": True},
        {"name": "Remote", "value": job.remote_level or "N/A", "inline": True},
        {"name": "Location", "value": job.candidate_location or "N/A", "inline": True},
        {"name": "Skills", "value": skills, "inline": False},
    ]

    return {
        "title": job.title,
        "url": job.url,
        "color": 0x5865F2,  # Discord blurple
        "author": {"name": source_label},
        "fields": fields,
    }


def send(jobs: list[Job]) -> None:
    webhook_url = os.environ["DISCORD_WEBHOOK_URL"]
    if not jobs:
        return

    # Send in batches (Discord limit: 10 embeds per message)
    with httpx.Client() as client:
        for i in range(0, len(jobs), BATCH_SIZE):
            batch = jobs[i : i + BATCH_SIZE]
            payload = {
                "content": f"**{len(jobs)} new job(s) found!**" if i == 0 else None,
                "embeds": [_job_to_embed(j) for j in batch],
            }
            resp = client.post(webhook_url, json=payload)
            resp.raise_for_status()
