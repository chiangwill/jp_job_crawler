# jp-job-crawler

Aggregates visa-sponsored Python job listings from [Japan Dev](https://japan-dev.com) and [Tokyo Dev](https://www.tokyodev.com), stores them in Supabase, and sends Discord notifications when new jobs are found.

Runs automatically every day at 10:00 JST via GitHub Actions.

## How it works

1. Fetch jobs from Japan Dev (Meilisearch API) and Tokyo Dev (HTML scraping)
2. Compare against jobs already stored in Supabase
3. Insert new jobs and send a Discord notification

## Setup

### 1. Clone and install dependencies

```bash
git clone https://github.com/chiangwill/jp_job_crawler.git
cd jp_job_crawler
uv sync
```

### 2. Configure environment variables

```bash
cp .env.example .env
```

Fill in `.env`:

```
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
DISCORD_WEBHOOK_URL=https://discord.com/api/webhooks/...
```

### 3. Create the Supabase table

Run `schema.sql` in the [Supabase SQL Editor](https://supabase.com/dashboard).

### 4. Configure filters

Edit `config.yaml` to adjust job filters:

```yaml
japan_dev:
  filters:
    visa_only: true
    skill_names: [Python]

tokyo_dev:
  filters:
    japanese_requirement: [none]
    applicant_location: [apply_from_abroad]
    category: [python]
```

**Japan Dev filter options**

| Field | Values |
|---|---|
| `visa_only` | `true` / `false` |
| `japanese_level_enum` | `japanese_level_not_required`, `japanese_level_basic`, `japanese_level_conversational`, `japanese_level_business_level`, `japanese_level_fluent` |
| `remote_level` | `remote_level_full`, `remote_level_partial`, `remote_level_no_remote` |
| `candidate_location` | `candidate_location_anywhere`, `candidate_location_japan_only` |
| `seniority_level` | `seniority_level_junior`, `seniority_level_mid_level`, `seniority_level_senior`, `seniority_level_lead` |
| `skill_names` | `Python`, `Backend`, `Frontend`, `DevOps`, `Go`, ... |

**Tokyo Dev filter options**

| Field | Values |
|---|---|
| `japanese_requirement` | `none`, `basic`, `conversational`, `business`, `fluent` |
| `remote_policy` | `fully_remote`, `partially_remote`, `no_remote` |
| `applicant_location` | `apply_from_abroad`, `japan_residents_only` |
| `seniority` | `intern`, `junior`, `intermediate`, `senior` |
| `category` | `backend`, `frontend`, `devops`, `python`, `go`, ... |

### 5. Run manually

```bash
uv run main.py
```

## GitHub Actions

Add these secrets to your repository (**Settings → Secrets and variables → Actions**):

- `SUPABASE_URL`
- `SUPABASE_KEY`
- `DISCORD_WEBHOOK_URL`

The workflow runs daily at 10:00 JST. You can also trigger it manually from the Actions tab.
