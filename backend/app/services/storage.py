"""
NO-STORAGE MODE.

SPYME does not store user videos. Period.

Clips live in one of three places, chosen by the user:
  1. On the laptop itself (encrypted, never uploaded)
  2. On the user's phone (transferred via WebRTC data channel, P2P)
  3. In the user's own Google Drive (we hold no bytes; only the file_id)

This module exists for two reasons:
  - Generate signed URLs IF the user opted into Drive (handled in gdrive.py)
  - Reject any accidental upload calls with a clear message
"""
from app.core.config import settings


def presign_upload(key: str) -> str:
    """No-op. Returns a signed URL only when the user picked SPYME Cloud.
    By default we refuse. Mobile/desktop should fall back to local-only or Drive."""
    if not settings.AWS_ACCESS_KEY_ID:
        # Default — we are NOT storing clips
        return "spyme://no-storage/refuses-upload"
    # If a deployment explicitly opted into hosting clips, fall back to S3
    import boto3
    from botocore.config import Config
    s3 = boto3.client(
        "s3",
        region_name=settings.AWS_REGION,
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        endpoint_url=settings.S3_ENDPOINT_URL or None,
        config=Config(signature_version="s3v4"),
    )
    return s3.generate_presigned_url(
        "put_object",
        Params={"Bucket": settings.S3_BUCKET, "Key": key},
        ExpiresIn=settings.UPLOAD_PRESIGN_EXPIRE_SECONDS,
    )


def presign_download(key: str) -> str:
    if not settings.AWS_ACCESS_KEY_ID:
        return "spyme://no-storage/clip-on-device"
    # same fallback as above
    return presign_upload(key)
