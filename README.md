# o-phone

An AI-powered agent that automatically finds and holds books at the San Francisco Public Library. It reads reading context from a Firestore database, searches sfpl.org for relevant books, and places holds on them.

## Current status

The project currently has a single script (`main.py`) that uses [Browser Use](https://github.com/browser-use/browser-use) with Claude to automate the SFPL website. It can navigate to sfpl.org, find the login page, and attempt to log in with library credentials.

## Setup

Requires Python 3.11+.

```bash
uv sync
uvx browser-use install
```

Copy `.env.example` to `.env` and fill in your values:

```
ANTHROPIC_API_KEY=your-api-key
SFPL_USERNAME=your-library-card-number
SFPL_PASSWORD=your-pin
```

## Usage

```bash
uv run main.py
```

This launches a Chromium browser, navigates to sfpl.org, and logs in with the provided credentials.
