from database.firebase_config import get_lecturer_ref

def test_firebase_connection():
    try:
        # Get reference to "lecturers" node
        ref = get_lecturer_ref()

        # Push a test lecturer
        test_data = {
            "name": "Test Lecturer",
            "email": "test@example.com",
            "mobile": "9999999999",
            "classes": ["MCA I", "B.Tech II"]
        }
        new_lecturer = ref.push(test_data)

        print("Test Lecturer added with key:", new_lecturer.key)

        # Read all lecturers
        all_lecturers = ref.get()
        print("All Lecturers in DB:", all_lecturers)

        print("✅ Firebase connection working perfectly!")

    except Exception as e:
        print("❌ Error connecting to Firebase:", e)

if __name__ == "__main__":
    test_firebase_connection()
