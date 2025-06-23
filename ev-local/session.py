import requests

BASE_URL = "https://smarteva.in"
LOGIN_URL = f"{BASE_URL}/login/"

session = requests.Session()

# Step 1: Get CSRF token
get_response = session.get(LOGIN_URL, verify=False)
csrf_token = session.cookies.get("csrftoken")

# Step 2: Post credentials as form data
login_data = {
    "username": "sparks",
    "password": "sparks@sparks",
    "csrfmiddlewaretoken": csrf_token,
}
headers = {
    "Referer": LOGIN_URL
}

response = session.post(LOGIN_URL, data=login_data, headers=headers, verify=True)

# ✅ Check if login was successful
if "Log out" in response.text or "/logout/" in response.text:
    print("✅ Login successful")
    print("Session ID:", session.cookies.get("sessionid"))
    print("CSRF Token:", session.cookies.get("csrftoken"))
else:
    print("❌ Login failed!")
    print(response.text[:500])  # Print first 500 chars of HTML for debugging
