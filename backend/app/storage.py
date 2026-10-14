import os
import io
import mimetypes
import tempfile
import httpx
from typing import Optional, Tuple
from .config import settings

class StorageService:
    def __init__(self):
        self.supabase_url = settings.SUPABASE_URL.rstrip("/") if settings.SUPABASE_URL else None
        self.supabase_key = settings.SUPABASE_KEY
        self.bucket = settings.SUPABASE_STORAGE_BUCKET or "omr-sheets"
        self.use_supabase = bool(self.supabase_url and self.supabase_key)
        
        # Local cache directory for CV processing
        self.cache_dir = os.path.join(settings.UPLOAD_DIR, "cache")
        os.makedirs(self.cache_dir, exist_ok=True)
        
        if self.use_supabase:
            self._ensure_bucket_exists()

    def _get_headers(self, content_type: Optional[str] = None) -> dict:
        headers = {
            "apikey": self.supabase_key,
            "Authorization": f"Bearer {self.supabase_key}"
        }
        if content_type:
            headers["Content-Type"] = content_type
        return headers

    def _ensure_bucket_exists(self):
        """Ensures the storage bucket exists in Supabase."""
        try:
            url = f"{self.supabase_url}/storage/v1/bucket/{self.bucket}"
            with httpx.Client(timeout=10.0) as client:
                res = client.get(url, headers=self._get_headers())
                if res.status_code == 404:
                    # Create bucket with public access for easiest image serving
                    create_url = f"{self.supabase_url}/storage/v1/bucket"
                    payload = {
                        "id": self.bucket,
                        "name": self.bucket,
                        "public": True
                    }
                    client.post(create_url, headers=self._get_headers("application/json"), json=payload)
        except Exception as e:
            # Non-blocking, bucket might already exist or will be verified on upload
            print(f"[Notice] Supabase bucket check: {e}")

    def upload_file(
        self, 
        file_bytes: bytes, 
        file_name: str, 
        folder: str = "uploads", 
        content_type: Optional[str] = None
    ) -> str:
        """
        Uploads a file to Supabase Storage if configured; otherwise saves locally.
        Returns a storage reference string (local file path or supabase URL/key).
        """
        if not content_type:
            content_type, _ = mimetypes.guess_type(file_name)
            content_type = content_type or "application/octet-stream"

        clean_filename = os.path.basename(file_name)
        storage_path = f"{folder}/{clean_filename}"

        if self.use_supabase:
            try:
                url = f"{self.supabase_url}/storage/v1/object/{self.bucket}/{storage_path}"
                headers = self._get_headers(content_type)
                headers["x-upsert"] = "true"
                with httpx.Client(timeout=30.0) as client:
                    resp = client.post(url, headers=headers, content=file_bytes)
                    if resp.status_code in (200, 201):
                        return f"supabase://{self.bucket}/{storage_path}"
                    else:
                        print(f"[Warning] Supabase upload failed ({resp.status_code}): {resp.text}. Falling back to local storage.")
            except Exception as e:
                print(f"[Warning] Supabase upload exception: {e}. Falling back to local storage.")

        # Local fallback
        target_dir = settings.ANNOTATED_DIR if folder == "annotated" else settings.UPLOAD_DIR
        os.makedirs(target_dir, exist_ok=True)
        local_path = os.path.join(target_dir, clean_filename)
        with open(local_path, "wb") as f:
            f.write(file_bytes)
        return local_path

    def get_file_bytes(self, storage_ref: str) -> bytes:
        """Retrieves raw file bytes from either Supabase or local disk."""
        if storage_ref.startswith("supabase://"):
            parts = storage_ref[len("supabase://"):].split("/", 1)
            bucket = parts[0]
            obj_path = parts[1]
            url = f"{self.supabase_url}/storage/v1/object/{bucket}/{obj_path}"
            with httpx.Client(timeout=30.0) as client:
                res = client.get(url, headers=self._get_headers())
                if res.status_code == 200:
                    return res.content
                raise FileNotFoundError(f"Supabase file not found: {storage_ref} (status {res.status_code})")
        elif storage_ref.startswith("http://") or storage_ref.startswith("https://"):
            with httpx.Client(timeout=30.0) as client:
                res = client.get(storage_ref)
                if res.status_code == 200:
                    return res.content
                raise FileNotFoundError(f"Remote file not found: {storage_ref}")
        else:
            if not os.path.exists(storage_ref):
                raise FileNotFoundError(f"Local file not found: {storage_ref}")
            with open(storage_ref, "rb") as f:
                return f.read()

    def get_local_path_for_cv(self, storage_ref: str) -> str:
        """
        Ensures the file is accessible as a local file path on disk so OpenCV
        and PyMuPDF can process it directly. Caches cloud downloads.
        """
        if not storage_ref.startswith("supabase://") and not storage_ref.startswith("http"):
            # Already a local path
            if os.path.exists(storage_ref):
                return storage_ref

        # Download and cache locally
        clean_name = os.path.basename(storage_ref.replace("supabase://", "").replace("/", "_"))
        cached_path = os.path.join(self.cache_dir, clean_name)
        
        file_bytes = self.get_file_bytes(storage_ref)
        with open(cached_path, "wb") as f:
            f.write(file_bytes)
            
        return cached_path

    def get_public_url(self, storage_ref: str) -> Optional[str]:
        """Returns the public HTTPS URL if using Supabase with public bucket."""
        if storage_ref.startswith("supabase://") and self.supabase_url:
            parts = storage_ref[len("supabase://"):].split("/", 1)
            bucket = parts[0]
            obj_path = parts[1]
            return f"{self.supabase_url}/storage/v1/object/public/{bucket}/{obj_path}"
        elif storage_ref.startswith("http://") or storage_ref.startswith("https://"):
            return storage_ref
        return None

storage = StorageService()
