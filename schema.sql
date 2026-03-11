CREATE TABLE IF NOT EXISTS jobs (
    id               TEXT PRIMARY KEY,
    source           TEXT NOT NULL,
    title            TEXT NOT NULL,
    company          TEXT NOT NULL,
    url              TEXT NOT NULL UNIQUE,
    location         TEXT,
    salary_min       INTEGER,
    salary_max       INTEGER,
    japanese_level   TEXT,
    remote_level     TEXT,
    candidate_location TEXT,
    sponsors_visas   BOOLEAN DEFAULT TRUE,
    skills           TEXT[] DEFAULT '{}',
    published_at     TEXT,
    first_seen       TIMESTAMPTZ DEFAULT NOW(),
    notified         BOOLEAN DEFAULT FALSE
);
