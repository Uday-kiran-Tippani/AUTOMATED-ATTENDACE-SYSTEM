# services/student_service.py
import re
import numpy as np
from config.firebase_config import get_admin_db

STUDENTS_ROOT = "students"

def sanitize_class_key(class_name: str) -> str:
    """
    Convert human-readable class name to Firebase-safe key.
    Example: "B.Tech I" -> "b_tech_i"
    """
    if not class_name:
        return ""
    # replace invalid characters (., $, #, [, ], /, space) with underscores
    safe = re.sub(r'[.$#[\]/\s]', '_', class_name)
    return safe.lower().strip()

def get_students_for_class(class_name: str):
    """
    Fetch all students for a given class (pretty name or key).
    Returns a list of dicts with 'roll_number', 'name', and 'face_encoding'.
    """
    root = get_admin_db()
    class_key = sanitize_class_key(class_name)
    ref = root.child(f"{STUDENTS_ROOT}/{class_key}")
    snapshot = ref.get()

    if not snapshot:
        return []

    students = []
    for roll_number, data in snapshot.items():
        face_enc = data.get("face_encoding")
        # Convert face_encoding dict/list from Firebase to numpy array
        if face_enc:
            try:
                # If Firebase stored as dict with keys 0-127
                if isinstance(face_enc, dict):
                    arr = np.array([face_enc[str(i)] for i in range(128)], dtype=np.float64)
                # If Firebase stored as list
                elif isinstance(face_enc, list):
                    arr = np.array(face_enc, dtype=np.float64)
                else:
                    arr = None
            except Exception as e:
                print(f"[WARN] Could not convert face_encoding for {roll_number}: {e}")
                arr = None
        else:
            arr = None

        students.append({
            "roll_number": str(data.get("roll_number", roll_number)),
            "name": data.get("name", "Unknown"),
            "face_encoding": arr
        })
    return students
