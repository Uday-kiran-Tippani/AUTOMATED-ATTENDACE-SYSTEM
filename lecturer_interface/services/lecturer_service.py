# services/lecturer_service.py
from firebase_admin import db
from utils.helpers import email_to_key

# Root path in Firebase for lecturers under HOD database
HOD_ROOT = "hod_db/lecturers"
CLASSES_ROOT = "admin_db/classes"  # classes added by Admin software


def get_lecturer_profile(email: str) -> dict:
    """
    Fetch full lecturer profile from HOD DB using email.
    Expected structure:
    hod_db/lecturers/{lecturer_key} = {
        "name": "...",
        "email": "...",
        "classes": { "MCA I": true, "MCA II": true }
    }
    """
    key = email_to_key(email)
    ref = db.reference(f"{HOD_ROOT}/{key}")
    data = ref.get()
    return data if data else {}


def get_assigned_classes(email: str) -> list:
    """
    Get list of classes assigned to lecturer.
    Normalizes dict or list into a clean list of class names.
    """
    profile = get_lecturer_profile(email)
    raw_classes = profile.get("classes", [])

    classes = []
    if isinstance(raw_classes, dict):
        classes = list(raw_classes.keys())  # Firebase dict → class names
    elif isinstance(raw_classes, list):
        for item in raw_classes:
            if isinstance(item, str):
                classes.append(item)
            elif isinstance(item, dict) and "name" in item:
                classes.append(item["name"])

    return classes


def get_class_details(class_name: str) -> dict:
    """
    Fetch metadata/details for a given class from Admin DB.
    Expected structure:
    admin_db/classes/{class_name} = {
        "year": "...",
        "department": "...",
        "students_count": N
    }
    """
    ref = db.reference(f"{CLASSES_ROOT}/{class_name}")
    data = ref.get()
    return data if data else {}


def refresh_lecturer_classes(email: str) -> dict:
    """
    Return full lecturer profile with normalized class list.
    """
    profile = get_lecturer_profile(email)
    if not profile:
        return {}

    profile["classes"] = get_assigned_classes(email)
    return profile
