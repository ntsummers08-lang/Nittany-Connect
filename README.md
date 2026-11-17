# Nittany Connect — AI Event Radar

This package **extends** the existing Nittany Connect app. It includes the original onboarding survey, weighted recommendations, 80 requested organizations, 20 requested Fall 2026 events, and 12 original example listings. It adds a new **Event Radar** navigation tab, candidate-review screen, import/export workflow, and optional live-feed support.

## Try the prototype now (no setup or API key)

1. Open **index.html** directly in Chrome. Complete the survey if prompted.
2. Select **Event Radar → Simulate AI research**. This creates **clearly fictional sample candidates**, not real event announcements.
3. Select **Approve** beside a sample event. It will appear on the **For You**, **Explore**, and **Live Events** views and is scored using the same survey-based algorithm.
4. Save an event, inspect its details, or open **Profile** to view your saved items.
5. Use **Import research JSON** to test event batches created elsewhere. Imported records enter the review queue and require approval.

In local `file://` mode the app does not retrieve the hosted JSON files; it continues to run fully offline. No API key is included in the HTML. The local simulation does not perform internet searches.

## Enable automatic research and a live website

You need a **GitHub repository**, **GitHub Pages**, and **an OpenAI API key** (paid API usage is separate from a ChatGPT subscription).

1. Create a GitHub repository and upload the **contents of this folder** to its default branch, preserving the `.github/workflows` and `data` directories.
2. In **Repository Settings → Secrets and variables → Actions**, add an Actions secret named `OPENAI_API_KEY`. Never put this key into the HTML, JavaScript, or JSON files.
3. In **Settings → Actions → General**, permit GitHub Actions to read and write repository contents so the research job can update `data/pending-events.json`.
4. Under **Settings → Pages**, publish the default branch from `/ (root)` (if offered for your repository). Use the resulting URL to open your hosted Nittany Connect site.
5. In **Actions → Nittany Connect event research**, trigger **Run workflow** to test. The job is configured to run four times per day (01:13, 07:13, 13:13 and 19:13 UTC). Local Eastern times shift with daylight saving time. GitHub schedules can be delayed and may be disabled due to inactivity on some repositories.
6. The job searches and attempts to corroborate upcoming event information, then writes new discoveries to **data/pending-events.json**. **It never changes the publicly approved event file automatically.**
7. Open the hosted app's **Event Radar** page, review pending items, and click **Approve** on good candidates. Approval is **browser-local** until publication.
8. Click **Export approved JSON** and upload/replace **data/approved-events.json** in GitHub. On the next site refresh, all visitors will see published events. The exported file omits fictional demo events.

**Important:** Event Radar's reviewer controls are **not secured**. This is a presentation prototype, not a real admin account system. Anyone visiting the page can approve items **in their own browser only**; they cannot change the shared published feed without GitHub repository write access. For a production deployment, add authenticated admin approval, source-specific ingestion rules, formal audit trails and privacy protections.

## How verification works

- Search is restricted to specified public campus/local event publishers, with a source URL for each proposed event.
- Candidate records need an individual HTTPS source link and a valid upcoming ISO date. The script checks that the publisher hostname is expected and attempts to find the event name/date on the page. Marking an item `verified` means **basic source corroboration**, not full factual verification.
- Unconfirmed event time, prices, and details are not filled in with guesses. If source access is blocked or information is ambiguous, records are marked **unverified** and must be checked by a reviewer.
- **The model is not trusted as a verification authority.** Reviewers should confirm event pages, details, cancellation notices, and venue/ticket terms before publishing.
- The system intentionally **does not bypass paywalls, login restrictions, or bot protection**, and sources may stop being readable or change their page structure.
- The event pipeline keeps past static events visible in the app but excludes them from Upcoming Events. New event recommendations respond to the user's original survey answers.

## JSON file format

Example **fictional record** for importing. It is **not a confirmed event**:

```json
{
  "status": "awaiting_manual_review",
  "events": [{
    "title": "Example Student Music Night — DEMO ONLY",
    "date": "2027-01-20",
    "endDate": "2027-01-20",
    "startTime": null,
    "endTime": null,
    "location": "Location not confirmed",
    "description": "Demonstration candidate, not a confirmed event.",
    "organizer": "Fictional",
    "category": "Social",
    "cost": "Not confirmed",
    "tags": ["Music & Arts", "Social Events"],
    "officialUrl": null,
    "verified": false,
    "demo": true
  }]
}
```

`data/pending-events.json` is visible in the review queue. `data/approved-events.json` is the public feed. Personal survey answers, saved items and requests remain only in the user's browser `localStorage` (no student data is uploaded by this project).

## Manual pipeline development

```bash
pip install -r requirements.txt
# Requires an OpenAI key in your environment:
python scripts/research_events.py --days 45
python -m unittest discover -s tests
```

Both local HTML and hosted website work without the API key. Automatic research requires configuring the scheduler and key. **Automatic research is installed but cannot run until OPENAI_API_KEY is configured; it has not been run against your own API account.**

Official resources: [OpenAI web search API](https://developers.openai.com/api/docs/guides/tools-web-search) · [GitHub scheduled workflows](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax)