import mimetypes
import os
from urllib.parse import quote
from werkzeug.utils import secure_filename


class StorageValidationError(ValueError):
    pass


MAX_STORED_FILE_SIZE = 50 * 1024 * 1024
ALLOWED_MIME_PREFIXES = (
    "application/pdf",
    "application/msword",
    "application/vnd.openxmlformats-officedocument",
    "application/vnd.ms-excel",
    "application/vnd.ms-powerpoint",
    "application/vnd.oasis.opendocument",
    "application/json",
    "application/xml",
    "application/zip",
    "application/x-zip-compressed",
    "application/gzip",
    "text/",
    "image/",
)
ALLOWED_EXTENSIONS = {
    ".pdf", ".doc", ".docx", ".xls", ".xlsx", ".ppt", ".pptx",
    ".odt", ".ods", ".odp", ".csv", ".txt", ".rtf", ".md",
    ".jpg", ".jpeg", ".png", ".gif", ".webp", ".svg", ".bmp",
    ".zip", ".gz", ".tar", ".json", ".xml", ".html", ".htm",
}


def sanitize_storage_name(value, field_name="file"):
    candidate = (value or "").strip()
    if not candidate or candidate in {".", ".."} or ".." in candidate or "/" in candidate or "\\" in candidate:
        raise StorageValidationError(f"Invalid {field_name} name")
    cleaned = secure_filename(candidate)
    if not cleaned or cleaned in {".", ".."}:
        raise StorageValidationError(f"Invalid {field_name} name")
    if len(cleaned) > 255:
        raise StorageValidationError(f"{field_name.title()} name is too long")
    return cleaned


def validate_upload_candidate(filename, mime_type, size_bytes, max_size=MAX_STORED_FILE_SIZE):
    safe_name = sanitize_storage_name(filename, "file")
    if size_bytes is None or size_bytes <= 0 or size_bytes > max_size:
        raise StorageValidationError(f"Files must be {max_size // (1024 * 1024)} MB or smaller")

    normalized_mime = (mime_type or "").split(";", 1)[0].strip().lower()
    if not normalized_mime:
        normalized_mime = mimetypes.guess_type(safe_name)[0] or "application/octet-stream"

    extension = os.path.splitext(safe_name)[1].lower()
    is_allowed_mime = (
        normalized_mime in {"application/octet-stream"}
        or normalized_mime.startswith(ALLOWED_MIME_PREFIXES)
        or extension.lower() in ALLOWED_EXTENSIONS
    )
    if not is_allowed_mime:
        raise StorageValidationError("File type is not allowed")

    return safe_name, normalized_mime


def build_object_key(org_id, scope_id, filename, folder_id=None):
    org_segment = sanitize_storage_name(str(org_id or "org"), "organization")
    scope_segment = sanitize_storage_name(str(scope_id or "root"), "scope")
    segments = [org_segment, scope_segment]
    if folder_id:
        segments.append(sanitize_storage_name(str(folder_id), "folder"))
    segments.append(sanitize_storage_name(filename, "file"))
    return "/".join(segments)


class ObjectStorageService:
    def __init__(self):
        self.endpoint_url = (os.getenv("OBJECT_STORAGE_ENDPOINT_URL") or "").strip()
        self.region_name = (os.getenv("OBJECT_STORAGE_REGION") or "eu").strip() or "eu"
        self.bucket_name = (os.getenv("OBJECT_STORAGE_BUCKET") or "academichub").strip() or "academichub"
        self.access_key = (os.getenv("OBJECT_STORAGE_ACCESS_KEY") or "").strip()
        self.secret_key = (os.getenv("OBJECT_STORAGE_SECRET_KEY") or "").strip()
        self.force_path_style = (os.getenv("OBJECT_STORAGE_FORCE_PATH_STYLE", "true") or "true").strip().lower() in {"1", "true", "yes", "on"}
        self.client = None
        self._initialize_client()

    def _initialize_client(self):
        if not self.endpoint_url or not self.access_key or not self.secret_key:
            return
        try:
            import boto3
            from botocore.config import Config
        except ImportError as exc:
            raise RuntimeError("boto3 is required for the Contabo Object Storage layer") from exc

        self.client = boto3.client(
            "s3",
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            config=Config(
                signature_version="s3v4",
                s3={"addressing_style": "path" if self.force_path_style else "virtual"},
            ),
        )

    @property
    def is_enabled(self):
        return self.client is not None and bool(self.bucket_name)

    @staticmethod
    def extract_key(reference_or_key):
        if not reference_or_key:
            return ""
        reference = str(reference_or_key).strip()
        if reference.startswith("s3://"):
            remainder = reference[len("s3://") :]
            if "/" not in remainder:
                return ""
            _, key = remainder.split("/", 1)
            return key
        return reference.lstrip("/")

    def reference_for(self, object_key):
        key = self.extract_key(object_key)
        if not self.is_enabled or not key:
            return key
        return f"s3://{self.bucket_name}/{key}"

    def upload_bytes(self, object_key, payload, content_type="application/octet-stream", metadata=None):
        if not self.is_enabled:
            raise RuntimeError("Contabo Object Storage is not configured")
        key = self.extract_key(object_key)
        self.client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=payload,
            ContentType=content_type,
            ACL="private",
            Metadata=metadata or {},
        )
        return self.reference_for(key)

    def delete_key(self, reference_or_key):
        if not reference_or_key:
            return
        if not self.is_enabled:
            return
        key = self.extract_key(reference_or_key)
        if not key:
            return
        self.client.delete_object(Bucket=self.bucket_name, Key=key)

    def has_key(self, reference_or_key):
        if not self.is_enabled:
            return False
        key = self.extract_key(reference_or_key)
        if not key:
            return False
        try:
            self.client.head_object(Bucket=self.bucket_name, Key=key)
            return True
        except Exception:
            return False

    def generate_signed_download_url(self, reference_or_key, display_name, expires_seconds=3600):
        if not self.is_enabled:
            return None
        key = self.extract_key(reference_or_key)
        if not key:
            return None
        safe_name = sanitize_storage_name(display_name, "file")
        return self.client.generate_presigned_url(
            "get_object",
            Params={
                "Bucket": self.bucket_name,
                "Key": key,
                "ResponseContentDisposition": f"attachment; filename*=UTF-8''{quote(safe_name)}",
            },
            ExpiresIn=expires_seconds,
        )
