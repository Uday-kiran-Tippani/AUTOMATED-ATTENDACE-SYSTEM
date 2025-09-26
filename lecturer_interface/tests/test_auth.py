import requests, json

API_KEY = "YOUR FIREBASE API KEY"

def validate_lecturer(email, password):
    url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={API_KEY}"
    payload = {"email": email, "password": password, "returnSecureToken": True}
    r = requests.post(url, data=json.dumps(payload))
    result = r.json()
    if "error" in result:
        print("Login failed:", result["error"])
        return None
    else :
        print('SUCCESS')
    return result
email = input("ENTER THE EMAIL : ")
password = input("ENTER THE PASSWORD : ")
validate_lecturer(email,password)