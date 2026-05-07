"""Firebase push. Lazily imported so dev mode works without firebase-admin."""
from app.core.config import settings

_initialized = False


def _init():
    global _initialized
    if _initialized or not settings.FIREBASE_CREDENTIALS_PATH:
        return
    try:
        import firebase_admin
        from firebase_admin import credentials
        cred = credentials.Certificate(settings.FIREBASE_CREDENTIALS_PATH)
        firebase_admin.initialize_app(cred)
        _initialized = True
    except Exception as e:
        print(f"[notify] Firebase init skipped: {e}")


def push(token: str, title: str, body: str, data: dict | None = None):
    _init()
    if not _initialized:
        safe = f"{title}: {body}".encode("ascii", "replace").decode("ascii")
        print(f"[notify] (dev) {safe}")
        return
    try:
        from firebase_admin import messaging
        msg = messaging.Message(
            notification=messaging.Notification(title=title, body=body),
            data=data or {},
            token=token,
        )
        messaging.send(msg)
    except Exception as e:
        print(f"[notify] push failed: {e}")
