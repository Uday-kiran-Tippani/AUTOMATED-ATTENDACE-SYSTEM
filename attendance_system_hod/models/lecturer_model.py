# models/lecturer_model.py
from database.firebase_config import init_firebase
from config import LECTURERS_COLLECTION
from werkzeug.security import generate_password_hash, check_password_hash
import uuid

db = init_firebase()
collection = db.collection(LECTURERS_COLLECTION)

def create_lecturer(lec_name, mobile, email, password_plain, classes_list):
    """
    Create a new lecturer document.
    classes_list -> list of strings.
    """
    lec_id = str(uuid.uuid4())
    hashed = generate_password_hash(password_plain)
    doc = {
        "lec_id": lec_id,
        "lec_name": lec_name,
        "mobile": mobile,
        "email": email,
        "password_hash": hashed,
        "classes": classes_list
    }
    collection.document(lec_id).set(doc)
    return lec_id

def get_lecturer_by_name(lec_name):
    q = collection.where("lec_name", "==", lec_name).limit(1).stream()
    for doc in q:
        data = doc.to_dict()
        data["_doc_id"] = doc.id
        return data
    return None

def get_lecturer_by_id(lec_id):
    doc = collection.document(lec_id).get()
    if doc.exists:
        data = doc.to_dict()
        data["_doc_id"] = doc.id
        return data
    return None

def verify_lecturer_credentials(lec_name, password_plain):
    lec = get_lecturer_by_name(lec_name)
    if not lec:
        return False, None
    if check_password_hash(lec.get("password_hash", ""), password_plain):
        return True, lec
    return False, None

def update_lecturer_classes(lec_id, classes_list):
    doc_ref = collection.document(lec_id)
    doc_ref.update({"classes": classes_list})
    return True

def remove_lecturer(lec_id):
    collection.document(lec_id).delete()
    return True

def list_all_lecturers():
    docs = collection.stream()
    out = []
    for d in docs:
        data = d.to_dict()
        data["_doc_id"] = d.id
        out.append(data)
    return out
