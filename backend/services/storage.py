"""Supabase Storage for PDD files.

Vercel functions have an ephemeral filesystem — Supabase Storage is the only
durable place for uploaded PDFs.
"""
from supabase import create_client, Client

from core.config import settings

_client: Client | None = None
BUCKET = "pdds"


def get_supabase() -> Client:
    global _client
    if _client is None:
        _client = create_client(settings.supabase_url, settings.supabase_service_role_key)
    return _client


def upload_pdf(verra_id: str, content: bytes) -> str:
    path = f"{verra_id}.pdf"
    sb = get_supabase()
    sb.storage.from_(BUCKET).upload(
        path=path,
        file=content,
        file_options={"content-type": "application/pdf", "upsert": "true"},
    )
    return path


def download_pdf(storage_path: str) -> bytes:
    sb = get_supabase()
    return sb.storage.from_(BUCKET).download(storage_path)