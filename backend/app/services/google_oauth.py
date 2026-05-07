"""
Google OAuth — verify the ID token coming from the mobile app, return user profile.

Flow:
  1. Mobile uses expo-auth-session to do Google sign-in → gets id_token + access_token
  2. Mobile sends id_token to /auth/google
  3. Backend verifies signature against Google's public keys (no secret needed)
  4. Backend creates or finds the user, returns SPYME JWT
  5. If access_token included with drive.file scope, we can store clips in user's Drive
"""
import json
import time
import urllib.request
from urllib.error import URLError

GOOGLE_TOKENINFO = "https://oauth2.googleapis.com/tokeninfo?id_token="
# Cache google's discovery doc & keys for 1 hour to reduce latency
_cache: dict = {"jwks": None, "ts": 0}


def verify_id_token(id_token: str, expected_audience: str | None = None) -> dict | None:
    """
    Verify a Google ID token. Returns the decoded payload {email, sub, name, picture, email_verified}
    or None on failure.

    Production note: prefer the `google-auth` library (offline JWT verification with cached JWKS).
    For dev / minimal deps we use Google's tokeninfo endpoint which does the verification server-side.
    """
    try:
        with urllib.request.urlopen(GOOGLE_TOKENINFO + id_token, timeout=8) as r:
            data = json.loads(r.read().decode())
    except URLError:
        return None

    # Sanity checks
    if expected_audience and data.get("aud") != expected_audience:
        return None
    if int(data.get("exp", 0)) < time.time():
        return None
    if data.get("iss") not in {"accounts.google.com", "https://accounts.google.com"}:
        return None

    return {
        "google_id": data["sub"],
        "email": data.get("email"),
        "email_verified": data.get("email_verified") == "true",
        "name": data.get("name"),
        "picture": data.get("picture"),
    }
