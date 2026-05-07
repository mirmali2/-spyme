"""
Google Drive storage adapter — store SPYME clips in the user's own Drive.

This is the privacy-first option:
  - Users grant the `drive.file` scope (only files this app creates, never their personal stuff)
  - Clips uploaded to a hidden 'SPYME Clips' folder in their Drive
  - We store only the Drive file_id, not the bytes
  - Pre-signed download URL = a short-lived Google Drive sharing link

Flow:
  1. User signs in with Google + grants drive.file scope
  2. Backend stores google_refresh_token
  3. On clip upload: exchange refresh_token for fresh access_token, upload bytes
  4. On clip view: generate temporary share link
"""
import json
import urllib.parse
import urllib.request
from urllib.error import HTTPError

from app.core.config import settings

GOOGLE_TOKEN_URL = "https://oauth2.googleapis.com/token"
DRIVE_UPLOAD_URL = "https://www.googleapis.com/upload/drive/v3/files?uploadType=multipart"
DRIVE_API_URL = "https://www.googleapis.com/drive/v3/files"

SPYME_FOLDER_NAME = "SPYME Clips"


def _exchange_refresh_token(refresh_token: str) -> str | None:
    client_id = getattr(settings, "GOOGLE_CLIENT_ID", "")
    client_secret = getattr(settings, "GOOGLE_CLIENT_SECRET", "")
    if not (client_id and client_secret):
        return None
    body = urllib.parse.urlencode({
        "client_id": client_id,
        "client_secret": client_secret,
        "refresh_token": refresh_token,
        "grant_type": "refresh_token",
    }).encode()
    req = urllib.request.Request(GOOGLE_TOKEN_URL, data=body, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())["access_token"]
    except HTTPError:
        return None


def get_or_create_folder(access_token: str) -> str | None:
    """Find the 'SPYME Clips' folder in user's Drive, create if missing. Returns folder id."""
    headers = {"Authorization": f"Bearer {access_token}"}
    q = f"name='{SPYME_FOLDER_NAME}' and mimeType='application/vnd.google-apps.folder' and trashed=false"
    url = f"{DRIVE_API_URL}?q={urllib.parse.quote(q)}&fields=files(id,name)"
    req = urllib.request.Request(url, headers=headers)
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            files = json.loads(r.read()).get("files", [])
            if files:
                return files[0]["id"]
    except HTTPError:
        return None

    # Create folder
    body = json.dumps({
        "name": SPYME_FOLDER_NAME,
        "mimeType": "application/vnd.google-apps.folder",
    }).encode()
    req = urllib.request.Request(
        DRIVE_API_URL, data=body, method="POST",
        headers={**headers, "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=10) as r:
            return json.loads(r.read())["id"]
    except HTTPError:
        return None


def upload_clip_to_drive(refresh_token: str, file_bytes: bytes, filename: str) -> str | None:
    """
    Upload a clip to user's Drive. Returns Drive file_id, or None on failure.
    Stored in their 'SPYME Clips' folder.
    """
    access_token = _exchange_refresh_token(refresh_token)
    if not access_token:
        return None

    folder_id = get_or_create_folder(access_token)
    if not folder_id:
        return None

    metadata = json.dumps({
        "name": filename,
        "parents": [folder_id],
        "mimeType": "video/mp4",
    }).encode()

    boundary = "spyme_boundary_8x4n2"
    body = (
        f"--{boundary}\r\n"
        f"Content-Type: application/json; charset=UTF-8\r\n\r\n"
    ).encode() + metadata + (
        f"\r\n--{boundary}\r\nContent-Type: video/mp4\r\n\r\n"
    ).encode() + file_bytes + f"\r\n--{boundary}--\r\n".encode()

    req = urllib.request.Request(
        DRIVE_UPLOAD_URL, data=body, method="POST",
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": f"multipart/related; boundary={boundary}",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=120) as r:
            return json.loads(r.read())["id"]
    except HTTPError as e:
        print(f"[gdrive] upload failed: {e}")
        return None


def get_drive_link(refresh_token: str, file_id: str) -> str | None:
    """Generate a temporary view link for a clip stored in user's Drive."""
    access_token = _exchange_refresh_token(refresh_token)
    if not access_token:
        return None
    return f"https://drive.google.com/file/d/{file_id}/view?usp=drivesdk&access_token={access_token}"
