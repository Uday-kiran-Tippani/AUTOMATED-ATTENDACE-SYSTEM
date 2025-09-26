# firebase_config.py
import os
import firebase_admin
from firebase_admin import credentials, db, auth

# Get the absolute path to the JSON file inside the database folder
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
json_path = os.path.join(BASE_DIR, "attendance-system.json") #rename if necessary

cred = credentials.Certificate(json_path)

# Initialize the Firebase app only once
if not firebase_admin._apps:
    firebase_admin.initialize_app(cred, {
        "databaseURL": "your firebase url"
    })

# Function to get lecturer reference (profile data)
def get_lecturer_ref():
    return db.reference("lecturers")

# Function to create lecturer account in Firebase Authentication
def create_lecturer_auth(email: str, password: str):
    """
    Creates a lecturer in Firebase Authentication with email & password.
    Returns UID if successful, None if failed.
    """
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return user.uid
    except Exception as e:
        print("❌ Error creating lecturer auth:", e)
        return None
