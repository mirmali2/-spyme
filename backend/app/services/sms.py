"""SMS via Twilio. Lazily imported. Dev mode prints to console."""
from app.core.config import settings


def send_sms(to_number: str, body: str) -> bool:
    sid = getattr(settings, "TWILIO_ACCOUNT_SID", "")
    token = getattr(settings, "TWILIO_AUTH_TOKEN", "")
    from_num = getattr(settings, "TWILIO_FROM_NUMBER", "")

    if not (sid and token and from_num and to_number):
        # Encode safely for Windows cp1252 console
        safe = body.encode("ascii", "replace").decode("ascii")
        print(f"[sms] (dev) to {to_number}: {safe}")
        return False
    try:
        from twilio.rest import Client
        client = Client(sid, token)
        client.messages.create(to=to_number, from_=from_num, body=body)
        return True
    except Exception as e:
        print(f"[sms] failed: {e}")
        return False
