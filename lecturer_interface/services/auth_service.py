# services/auth_service.py
import requests
import json

API_KEY = "YOUR API KEY SHOULD BE HERE"
DB_URL = "YOUR PROJECT REALTIME DATABASE LINK FROM THE FIREBASE"

def _safe_key(email: str) -> str:
    return email.replace(".", "_")

def validate_lecturer(email: str, password: str):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}

    try:
        response = requests.post(url, data=json.dumps(payload))
        result = response.json()

        if "error" in result:
            print("❌ Login failed:", result["error"])
            return None

        lecturer = {
            "email": result.get("email"),
            "uid": result.get("localId"),
            "idToken": result.get("idToken"),
        }

        # ✅ Fetch lecturer profile with auth token
        lecturer_key = _safe_key(email.lower())
        db_url = f"{DB_URL}/lecturers/{lecturer_key}.json?auth={lecturer['idToken']}"
        print(f"📡 Fetching lecturer profile from: {db_url}")

        db_res = requests.get(db_url)
        db_data = db_res.json()
        print("📡 DB response:", db_data)

        if db_data:
            classes = db_data.get("classes", [])
            if isinstance(classes, dict):  # Handle dict format
                classes = list(classes.values())

            lecturer.update({
                "name": db_data.get("name", ""),
                "mobile": db_data.get("mobile", ""),
                "classes": classes,
            })
        else:
            lecturer["classes"] = []

        print("✅ Final lecturer object:", lecturer)
        return lecturer

    except Exception as e:
        print(f"❌ Login error: {e}")
        return None

