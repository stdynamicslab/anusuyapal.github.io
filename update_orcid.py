import json
import re
from datetime import datetime, timezone
from pathlib import Path

import requests

ORCID = "0000-0002-8573-7938"
API_BASE = "https://pub.orcid.org/v3.0"
OUTPUT = Path("data/publications.json")

HEADERS = {
    "Accept": "application/vnd.orcid+json"
}

TIMEOUT = 30


def get_json(url):
    response = requests.get(url, headers=HEADERS, timeout=TIMEOUT)
    response.raise_for_status()
    return response.json()


def safe_text(value):
    if not value:
        return ""
    return str(value).strip()


def get_title(work):
    title = work.get("title") or {}
    return safe_text(title.get("title", {}).get("value"))


def get_date(work):
    date = work.get("publication-date") or work.get("publication-date")
    if not date:
        return ""

    year = safe_text((date.get("year") or {}).get("value"))
    month = safe_text((date.get("month") or {}).get("value"))
    day = safe_text((date.get("day") or {}).get("value"))

    if not year:
        return ""

    try:
        y = int(year)
        m = int(month) if month else 1
        d = int(day) if day else 1
        return f"{y:04d}-{m:02d}-{d:02d}"
    except ValueError:
        return year


def get_journal(work):
    journal = work.get("journal-title") or {}
    return safe_text(journal.get("value"))


def get_type(work):
    return safe_text(work.get("type")).replace("-", " ").title()


def get_url(work):
    url = (work.get("url") or {}).get("value")
    return safe_text(url)


def get_doi(work):
    ext_ids = (work.get("external-ids") or {}).get("external-id", [])

    # Prefer DOI.
    for item in ext_ids:
        if safe_text(item.get("external-id-type")).lower() == "doi":
            return safe_text(item.get("external-id-value"))

    # Sometimes the URL itself is a DOI.
    url = get_url(work)
    match = re.search(r"doi\.org/(10\.\d{4,9}/[-._;()/:A-Z0-9]+)", url, re.I)
    if match:
        return match.group(1).rstrip(".,;)")

    return ""


def choose_url(work, doi):
    if doi:
        return f"https://doi.org/{doi}"

    url = get_url(work)
    return url


def main():
    print(f"Fetching ORCID record for {ORCID}...")

    # /works provides the complete list of public work summaries.
    payload = get_json(f"{API_BASE}/{ORCID}/works")

    groups = (payload.get("group") or [])
    publications = []
    seen = set()

    for group in groups:
        summaries = group.get("work-summary") or []
        if not summaries:
            continue

        # ORCID groups equivalent records. Prefer the first public summary.
        work = summaries[0]

        title = get_title(work)
        if not title:
            continue

        doi = get_doi(work)
        date = get_date(work)
        journal = get_journal(work)
        work_type = get_type(work)
        url = choose_url(work, doi)

        # Deduplicate primarily by DOI, otherwise title.
        key = doi.lower() if doi else re.sub(r"\W+", "", title.lower())
        if key in seen:
            continue
        seen.add(key)

        publications.append({
            "title": title,
            "date": date,
            "year": date[:4] if date else "",
            "journal": journal,
            "type": work_type,
            "doi": doi,
            "url": url
        })

    publications.sort(
        key=lambda item: item.get("date") or "0000-00-00",
        reverse=True
    )

    output = {
        "orcid": ORCID,
        "last_updated": datetime.now(timezone.utc).isoformat(),
        "source": f"https://orcid.org/{ORCID}",
        "publications": publications
    }

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )

    print(f"Wrote {len(publications)} public ORCID works to {OUTPUT}")


if __name__ == "__main__":
    main()
