#!/usr/bin/env python3
"""Nittany Connect automated event research. Candidates ALWAYS require manual review."""
import argparse
from datetime import date, datetime, timedelta
import json
import os
from pathlib import Path
import re
import sys
from urllib.parse import urlparse
from zoneinfo import ZoneInfo

import requests
from bs4 import BeautifulSoup
from openai import OpenAI

ROOT = Path(__file__).resolve().parents[1]
PENDING = ROOT / "data" / "pending-events.json"
APPROVED = ROOT / "data" / "approved-events.json"
TZ = ZoneInfo("America/New_York")
SOURCES = [
    "https://studentaffairs.psu.edu/events",
    "https://bjc.psu.edu/events",
    "https://cpa.psu.edu/events",
    "https://arboretum.psu.edu/events/",
    "https://downtownstatecollege.com/events/",
    "https://www.statecollege.com/events/",
]
HOSTS = ("psu.edu", "statecollege.com", "downtownstatecollege.com")
TAGS = {
    "Sports & Fitness", "Gaming & Technology", "Music & Arts",
    "Outdoor Activities", "Volunteering", "Business & Career",
    "Food & Culture", "Academic Clubs", "Sporting Events",
    "Social Events", "Club Meetings", "Concerts & Performances",
    "Career Events", "Community Service", "Workshops",
}
HEADERS = {"User-Agent": "NittanyConnectStudentPrototype/0.1 (event-research; attribution)"}


def read_json(path):
    try:
        obj = json.loads(path.read_text(encoding="utf-8"))
        return obj if isinstance(obj, dict) else {"events": []}
    except (OSError, ValueError):
        return {"events": []}


def host_allowed(url):
    try:
        parsed = urlparse(url)
        host = (parsed.hostname or "").lower()
        return (parsed.scheme == "https" and not parsed.username and not parsed.password
                and any(host == d or host.endswith("." + d) for d in HOSTS))
    except ValueError:
        return False


def normalize(raw, today, end):
    if not isinstance(raw, dict):
        return None
    title = str(raw.get("title") or "").strip()[:170]
    url = str(raw.get("officialUrl") or raw.get("sourceUrl") or "").strip()
    raw_day = str(raw.get("date") or "")[:10]
    try:
        day = date.fromisoformat(raw_day)
    except ValueError:
        return None
    if not title or not host_allowed(url) or not today <= day <= end:
        return None
    end_date = str(raw.get("endDate") or raw_day)[:10]
    try:
        if date.fromisoformat(end_date) < day:
            end_date = raw_day
    except ValueError:
        end_date = raw_day
    def short(name, fallback, limit):
        return str(raw.get(name) or fallback).strip()[:limit]
    def clock(name):
        value = raw.get(name)
        return value if isinstance(value, str) and re.fullmatch(r"(?:[01]\d|2[0-3]):[0-5]\d", value) else None
    tags = [t for t in raw.get("tags", []) if isinstance(t, str) and t in TAGS]
    return {
        "title": title, "date": raw_day, "endDate": end_date,
        "startTime": clock("startTime"), "endTime": clock("endTime"),
        "location": short("location", "Location not confirmed", 180),
        "description": short("description", "See official event page for details.", 400),
        "organizer": short("organizer", "Organizer not confirmed", 120),
        "category": short("category", "Campus event", 70),
        "cost": short("cost", "Ticket details not confirmed", 100),
        "tags": list(dict.fromkeys(tags))[:8],
        "officialUrl": url,
        "verified": False,
        "researchNote": "LLM suggestion; source and all details require manual review.",
    }


def event_key(obj):
    return (re.sub(r"[^a-z0-9]", "", str(obj.get("title", "")).casefold())
            + "|" + str(obj.get("date", ""))[:10])


def source_check(event):
    """Corroborate visible title/date on a publisher page. Never certify automatically."""
    try:
        r = requests.get(event["officialUrl"], timeout=12, headers=HEADERS, allow_redirects=True)
        if not r.ok or not host_allowed(r.url) or len(r.content) > 1500000:
            return event
        if "html" not in r.headers.get("content-type", ""):
            return event
        page = BeautifulSoup(r.text, "html.parser").get_text(" ", strip=True).casefold()
        words = [w for w in re.findall(r"[a-z0-9]{4,}", event["title"].casefold())
                 if w not in {"penn", "state", "event", "concert", "2026", "2027"}]
        d = date.fromisoformat(event["date"])
        dates = [d.isoformat(), d.strftime("%B %d, %Y"), d.strftime("%B %d"),
                 d.strftime("%b %d, %Y"), d.strftime("%m/%d/%Y")]
        title_found = len(words) >= 2 and sum(w in page for w in words) >= max(2, len(words)//2)
        date_found = any(s.casefold() in page for s in dates)
        if title_found and date_found:
            event["researchNote"] = ("Title/date appear on publisher page. "
                                     "Confirm time, venue, cost, cancellation before approval.")
        else:
            event["researchNote"] = "Could not corroborate title/date; manual review required."
    except (requests.RequestException, ValueError):
        event["researchNote"] = "Source inaccessible; manual review required."
    return event


def research(today, horizon):
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("OPENAI_API_KEY GitHub Actions secret is not configured.")
    model = os.getenv("NC_RESEARCH_MODEL", "gpt-5-mini")
    prompt = (
        "Find real upcoming public events at Penn State University Park or State College PA "
        f"between {today.isoformat()} and {horizon.isoformat()} inclusive. "
        "Use web search and the event pages of these publishers: "
        + ", ".join(SOURCES) + ". "
        "Return up to 25 events. Each requires an actual specific HTTPS publisher event URL "
        "and a clearly stated date. No generic homepages or guessed annual recurrences. "
        "Never guess times, ticket prices, locations or URLs; use null for uncertain times. "
        "If nothing credible is found return an empty array. "
        "Return ONLY a JSON object with an events array. Event fields: "
        "title, date YYYY-MM-DD, endDate YYYY-MM-DD, startTime HH:MM or null, "
        "endTime HH:MM or null, location, description, organizer, category, cost, "
        "tags array, officialUrl. Allowed tags: " + ", ".join(sorted(TAGS))
    )
    result = OpenAI(api_key=api_key).responses.create(
        model=model, input=prompt,
        tools=[{"type": "web_search", "search_context_size": "medium"}],
        max_output_tokens=9000, store=False)
    output = result.output_text.strip()
    fence = chr(96) * 3
    if output.startswith(fence):
        output = re.sub(r"^" + fence + r"(?:json)?\s*|\s*" + fence + r"$", "", output).strip()
    try:
        data = json.loads(output)
    except ValueError:
        first, last = output.find("{"), output.rfind("}")
        data = json.loads(output[first:last + 1]) if first >= 0 and last > first else {"events": []}
    return data.get("events", []) if isinstance(data, dict) and isinstance(data.get("events"), list) else []


def run(days=45):
    today = datetime.now(TZ).date()
    horizon = today + timedelta(days=days)
    existing = read_json(PENDING)
    approved = read_json(APPROVED)
    kept = [x for x in existing.get("events", []) if isinstance(x, dict)
            and str(x.get("endDate") or x.get("date") or "")[:10] >= today.isoformat()]
    seen = {event_key(x) for x in kept + approved.get("events", []) if isinstance(x, dict)}
    found = research(today, horizon)
    added = 0
    for raw in found[:60]:
        event = normalize(raw, today, horizon)
        if not event or event_key(event) in seen:
            continue
        seen.add(event_key(event))
        kept.append(source_check(event))
        added += 1
    PENDING.parent.mkdir(parents=True, exist_ok=True)
    PENDING.write_text(json.dumps({
        "updatedAt": datetime.now(TZ).isoformat(),
        "status": "awaiting_manual_review",
        "sources": SOURCES,
        "events": kept,
    }, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(f"Added {added} candidates; {len(kept)} awaiting review.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--days", type=int, default=45)
    arguments = parser.parse_args()
    try:
        run(days=arguments.days)
    except Exception as exc:
        print(f"Event research failed: {exc}", file=sys.stderr)
        sys.exit(1)
