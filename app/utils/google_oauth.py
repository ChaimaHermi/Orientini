import requests
from app.core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
GOOGLE_USERINFO_URL = "https://www.googleapis.com/oauth2/v2/userinfo"

def get_google_user_info(code: str):
    data = {
        "code": code,
        "client_id": settings.GOOGLE_CLIENT_ID,
        "client_secret": settings.GOOGLE_CLIENT_SECRET,
        "redirect_uri": settings.GOOGLE_REDIRECT_URI,
        "grant_type": "authorization_code"
    }

    token_res = requests.post(GOOGLE_TOKEN_URL, data=data)
    token_res.raise_for_status()

    access_token = token_res.json()["access_token"]
    headers = {"Authorization": f"Bearer {access_token}"}

    userinfo_res = requests.get(GOOGLE_USERINFO_URL, headers=headers)
    userinfo_res.raise_for_status()

    return userinfo_res.json()
