"""
Cloudflare R2 storage service — S3-compatible object storage via boto3.

Handles file upload, download, deletion, and presigned URL generation.
R2 is configured as an S3-compatible endpoint using the account ID.
"""

import hashlib

import boto3
from botocore.config import Config as BotoConfig

from app.config import settings


def _get_r2_client():
    """Create an S3 client configured for Cloudflare R2."""
    return boto3.client(
        "s3",
        endpoint_url=f"https://{settings.r2_account_id}.r2.cloudflarestorage.com",
        aws_access_key_id=settings.r2_access_key_id,
        aws_secret_access_key=settings.r2_secret_access_key,
        config=BotoConfig(
            region_name="auto",
            signature_version="s3v4",
        ),
    )


def compute_sha256(file_data: bytes) -> str:
    """Compute SHA-256 hex digest for file integrity and dedup checks."""
    return hashlib.sha256(file_data).hexdigest()


def generate_r2_key(user_id: int, course_id: int, filename: str) -> str:
    """Generate a namespaced R2 object key: users/{id}/courses/{id}/{filename}."""
    # Sanitize filename — keep it simple
    safe_name = filename.replace(" ", "_")
    return f"users/{user_id}/courses/{course_id}/{safe_name}"


def upload_file(
    file_data: bytes,
    r2_key: str,
    content_type: str = "application/pdf",
) -> None:
    """Upload a file to R2."""
    client = _get_r2_client()
    client.put_object(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
        Body=file_data,
        ContentType=content_type,
    )


def download_file(r2_key: str) -> bytes:
    """Download a file from R2 and return its bytes."""
    client = _get_r2_client()
    response = client.get_object(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
    )
    return response["Body"].read()


def delete_file(r2_key: str) -> None:
    """Delete a file from R2."""
    client = _get_r2_client()
    client.delete_object(
        Bucket=settings.r2_bucket_name,
        Key=r2_key,
    )


def generate_presigned_url(r2_key: str, expires_in: int = 3600) -> str:
    """Generate a presigned download URL (valid for 1 hour by default)."""
    client = _get_r2_client()
    return client.generate_presigned_url(
        "get_object",
        Params={
            "Bucket": settings.r2_bucket_name,
            "Key": r2_key,
        },
        ExpiresIn=expires_in,
    )
