# # config/firebase_config.py
# import os
# import firebase_admin
# from firebase_admin import credentials, db

# # Paths to service account JSON files (replace with your actual file paths)
# ADMIN_SERVICE_ACCOUNT = os.path.join(os.getcwd(), "config", "admin_service_account.json")
# HOD_SERVICE_ACCOUNT = os.path.join(os.getcwd(), "config", "hod_service_account.json")

# # Firebase Realtime Database URLs
# ADMIN_DB_URL = "https://admin-software-ff838-default-rtdb.firebaseio.com/"
# HOD_DB_URL = "https://face-attendance-system-f6e56-default-rtdb.firebaseio.com/"

# # Firebase app instances
# firebase_apps = {}

# def init_firebase():
#     """
#     Initialize Firebase apps for Admin DB and HOD/Principal DB.
#     This should be called once at the start of the app (from main.py).
#     """
#     global firebase_apps

#     if not firebase_apps.get("admin"):
#         admin_cred = credentials.Certificate(ADMIN_SERVICE_ACCOUNT)
#         firebase_apps["admin"] = firebase_admin.initialize_app(
#             admin_cred,
#             {"databaseURL": ADMIN_DB_URL},
#             name="admin"
#         )

#     if not firebase_apps.get("hod"):
#         hod_cred = credentials.Certificate(HOD_SERVICE_ACCOUNT)
#         firebase_apps["hod"] = firebase_admin.initialize_app(
#             hod_cred,
#             {"databaseURL": HOD_DB_URL},
#             name="hod"
#         )

# def get_admin_db():
#     """Return reference to Admin database root."""
#     return db.reference("/", app=firebase_apps["admin"])

# def get_hod_db():
#     """Return reference to HOD/Principal database root."""
#     return db.reference("/", app=firebase_apps["hod"])


# config/firebase_config.py
import os
import firebase_admin
from firebase_admin import credentials, db

# Paths to service account JSON files
ADMIN_SERVICE_ACCOUNT = os.path.join(os.getcwd(), "config", "admin_service_account.json")
HOD_SERVICE_ACCOUNT = os.path.join(os.getcwd(), "config", "hod_service_account.json")

# Firebase Realtime Database URLs
ADMIN_DB_URL = "https://admin-software-ff838-default-rtdb.firebaseio.com/"
HOD_DB_URL = "https://face-attendance-system-f6e56-default-rtdb.firebaseio.com/"

# Firebase app instances
firebase_apps = {}


def init_firebase():
    """
    Initialize Firebase apps for Admin DB and HOD/Principal DB.
    This should be called once at the start of the app (from main.py or test.py).
    """
    global firebase_apps

    # Initialize Admin Firebase App
    if "admin" not in firebase_apps:
        admin_cred = credentials.Certificate(ADMIN_SERVICE_ACCOUNT)
        firebase_apps["admin"] = firebase_admin.initialize_app(
            admin_cred,
            {"databaseURL": ADMIN_DB_URL},
            name="admin"
        )

    # Initialize HOD Firebase App
    if "hod" not in firebase_apps:
        hod_cred = credentials.Certificate(HOD_SERVICE_ACCOUNT)
        firebase_apps["hod"] = firebase_admin.initialize_app(
            hod_cred,
            {"databaseURL": HOD_DB_URL},
            name="hod"
        )


def get_admin_db():
    """Return reference to Admin database root (auto-initializes if needed)."""
    if "admin" not in firebase_apps:
        init_firebase()
    return db.reference("/", app=firebase_apps["admin"])


def get_hod_db():
    """Return reference to HOD/Principal database root (auto-initializes if needed)."""
    if "hod" not in firebase_apps:
        init_firebase()
    return db.reference("/", app=firebase_apps["hod"])
