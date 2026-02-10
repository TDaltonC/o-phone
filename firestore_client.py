import os

from google.cloud import firestore

os.environ.setdefault(
    "GOOGLE_APPLICATION_CREDENTIALS",
    os.path.join(os.path.dirname(__file__), "service-account.json"),
)

PROJECT_ID = "o-phone-c0b25"

_client = None


def get_db() -> firestore.Client:
    global _client
    if _client is None:
        _client = firestore.Client(project=PROJECT_ID)
    return _client
