import asyncio
import json
from datetime import datetime, timezone

from browser_use import Agent, Browser
from browser_use.llm import ChatAnthropic
from dotenv import load_dotenv

from config import load_family

load_dotenv()


def build_task(family: dict, summaries: list[str]) -> str:
    child = family["child_name"]
    age = family["child_age"]
    persona = f"{age}-year-old boy, showing signs of being nerdy"
    summary_block = "\n".join(f"  - {s}" for s in summaries)
    return f"""\
You are a children's librarian helping pick books for a kid.

## Who the books are for
{persona}

## What they've been interested in lately
{summary_block}

## STEP 1 — Brainstorm candidates in your head
Before you interact with the browser, think of 8-10 children's books that would be
a great fit. Consider picture books, early readers, and engaging non-fiction
appropriate for the age. Keep this ranked list in your memory — you'll work through
it in order. Do NOT call the "done" action yet. You are nowhere near done.

## STEP 2 — Search SFPL catalog
Now go to https://sfpl.org and search for your #1 candidate using the search bar.

For each search:
a) Type the book title into the search box and submit.
b) Look at the results list. Find the matching book.
c) CLICK INTO the book's detail page to check its availability status.
d) If the detail page shows "Available" copies at any branch → this book is CONFIRMED.
   Record it as a winner and note which branch has it.
e) If it shows "All copies in use" or no results → SKIP it and search your next candidate.
f) Go back to the search bar and repeat with the next candidate.

IMPORTANT RULES:
- You must CLICK INTO each book's detail page. Do NOT judge availability from the
  search results list alone — it is not reliable.
- NEVER report a book you did not actually find and verify on sfpl.org.
- If you run out of candidates, brainstorm a few more and keep searching.

## STEP 3 — Report your final picks (this is the ONLY time you should call "done")
Aim for 3 confirmed books, but 2 is acceptable if the browser crashes or the site
becomes unresponsive. Call "done" with:

FINAL PICKS:
1. "Title" by Author — Why it fits + which SFPL branch has it available
2. "Title" by Author — Why it fits + which SFPL branch has it available
3. "Title" by Author — Why it fits + which SFPL branch has it available

Only include books you personally verified as available on sfpl.org in Step 2.
Do NOT call "done" until you have at least 2 confirmed books.
"""


def save_picks(result) -> None:
    picks = {
        "searched_at": datetime.now(timezone.utc).isoformat(),
        "result": result.final_result(),
    }
    with open("picks.json", "w") as f:
        json.dump(picks, f, indent=2)
    print("\nPicks saved to picks.json")


def load_summaries(family_id: str) -> list[str]:
    """Load summaries from Firestore, falling back to interests.py test data."""
    try:
        from firestore_client import get_db
        db = get_db()
        docs = (
            db.collection("families")
            .document(family_id)
            .collection("summaries")
            .order_by("created_at", direction="DESCENDING")
            .limit(5)
            .stream()
        )
        summaries = [doc.to_dict().get("summary_text", "") for doc in docs]
        if summaries:
            return summaries
    except Exception:
        pass

    # Fall back to synthetic test data
    from interests import load_interests
    return load_interests()["summaries"]


async def main():
    family = load_family()
    summaries = load_summaries(family.get("family_id", "leo"))
    task = build_task(family, summaries)

    browser = Browser()
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    agent = Agent(task=task, llm=llm, browser=browser)
    result = await agent.run()
    save_picks(result)


if __name__ == "__main__":
    asyncio.run(main())
