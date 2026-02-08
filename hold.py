import asyncio
import json
import os

from browser_use import Agent, Browser
from browser_use.llm import ChatAnthropic
from dotenv import load_dotenv

load_dotenv()

SFPL_USERNAME = os.environ["SFPL_USERNAME"]
SFPL_PASSWORD = os.environ["SFPL_PASSWORD"]


def load_picks() -> str:
    with open("picks.json") as f:
        return json.load(f)["result"]


def build_task(picks: str) -> str:
    return f"""\
You need to log into the San Francisco Public Library website and place holds on books.

## STEP 1 — Log in
Go to https://sfpl.org and log in:
- Click "Log In" in the top navigation
- Username/Barcode: {SFPL_USERNAME}
- Password/PIN: {SFPL_PASSWORD}
- After logging in, confirm you see your account (e.g. your name or "My Account").
  If login fails, report the error and call "done" immediately.

## STEP 2 — Place holds on these books
{picks}

For each book:
a) Search for the book title using the search bar.
b) Click into the correct book from the results.
c) Click the "Place a Hold" button (or similar).
d) If it asks you to choose a pickup location, pick any available branch.
e) Confirm the hold was placed successfully.
f) Move on to the next book.

If a hold can't be placed (already on hold, not available, etc.), note the reason
and move on.

## STEP 3 — Report results (this is the ONLY time you should call "done")
After attempting all books, call "done" with a summary:

HOLD RESULTS:
1. "Title" — Hold placed successfully (pickup at BRANCH) / Failed: reason
2. "Title" — Hold placed successfully (pickup at BRANCH) / Failed: reason
3. "Title" — Hold placed successfully (pickup at BRANCH) / Failed: reason

Do NOT call "done" until you have attempted holds for all books.
"""


async def main():
    picks = load_picks()
    task = build_task(picks)

    browser = Browser()
    llm = ChatAnthropic(model="claude-sonnet-4-5-20250929")

    agent = Agent(task=task, llm=llm, browser=browser)
    result = await agent.run()
    print(result.final_result())


if __name__ == "__main__":
    asyncio.run(main())
