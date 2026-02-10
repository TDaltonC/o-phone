"""One-time script to seed the families/leo document in Firestore."""

from dotenv import load_dotenv

from firestore_client import get_db

load_dotenv()


def seed():
    db = get_db()
    db.collection("families").document("leo").set({
        "parent_name": "Dalton",
        "child_name": "Leo",
        "child_age": 4,
        "preferred_branch": "Noe Valley",
        "phone_number": "+19492806125",
    })
    print("Seeded families/leo")


if __name__ == "__main__":
    seed()
