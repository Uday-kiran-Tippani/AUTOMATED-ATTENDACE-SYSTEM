# config.py
import os

# HOD/Principal credentials (simple approach). In production use a secure auth provider.
HOD_EMAIL = os.environ.get("HOD_EMAIL", "hod@example.com")
HOD_PASSWORD = os.environ.get("HOD_PASSWORD", "hodpassword123")

# Path to Firebase service account JSON (download from Firebase console)
# e.g. put serviceAccountKey.json in project root and set path accordingly
SERVICE_ACCOUNT_PATH = os.environ.get("FIREBASE_SERVICE_ACCOUNT", "serviceAccountKey.json")

# Firestore collection name
LECTURERS_COLLECTION = "lecturers"

# Flask secret key for sessions
SECRET_KEY = os.environ.get("FLASK_SECRET_KEY", "change_this_secret")
