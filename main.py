import yaml
from dotenv import load_dotenv
from scrapers.japan_dev import fetch_jobs as fetch_japan_dev
from scrapers.tokyo_dev import fetch_jobs as fetch_tokyo_dev
from storage.database import get_client, save_new_jobs, mark_notified
from notifier.discord import send as discord_send

load_dotenv()


def load_config(path: str = "config.yaml") -> dict:
    with open(path) as f:
        return yaml.safe_load(f)


def main():
    config = load_config()
    db = get_client()

    print("Fetching Japan Dev...")
    japan_dev_jobs = fetch_japan_dev(filters=config["japan_dev"]["filters"])
    print(f"  → {len(japan_dev_jobs)} jobs fetched")

    print("Fetching Tokyo Dev...")
    try:
        td_filters = config["tokyo_dev"]["filters"]
        tokyo_dev_jobs = fetch_tokyo_dev(**td_filters)
        print(f"  → {len(tokyo_dev_jobs)} jobs fetched")
    except Exception as e:
        print(f"  → Failed: {e}")
        tokyo_dev_jobs = []

    all_jobs = japan_dev_jobs + tokyo_dev_jobs

    print("Saving new jobs to Supabase...")
    new_jobs = save_new_jobs(db, all_jobs)
    print(f"  → {len(new_jobs)} new jobs found")

    if new_jobs:
        print("Sending Discord notification...")
        discord_send(new_jobs)
        mark_notified(db, [j.id for j in new_jobs])
        print("  → Done")
    else:
        print("  → No new jobs, skipping notification")


if __name__ == "__main__":
    main()
