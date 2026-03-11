from pydantic import BaseModel
from typing import Optional


class Job(BaseModel):
    id: str                        # unique: source + job id
    source: str                    # "japan_dev" | "tokyo_dev"
    title: str
    company: str
    url: str
    location: Optional[str] = None
    salary_min: Optional[int] = None
    salary_max: Optional[int] = None
    japanese_level: Optional[str] = None
    remote_level: Optional[str] = None
    candidate_location: Optional[str] = None
    sponsors_visas: bool = False
    skills: list[str] = []
    published_at: Optional[str] = None
