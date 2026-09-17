"""Local filesystem storage for uploads and generated artifacts."""

from __future__ import annotations

import re
import uuid
from pathlib import Path

_SAFE_NAME = re.compile(r"[^A-Za-z0-9._-]+")
_MEDIA_PREFIX = "/media"


def sanitize_filename(name: str) -> str:
    """Strip path components and unsafe characters from an uploaded filename."""
    base = Path(name).name
    cleaned = _SAFE_NAME.sub("_", base).strip("._") or "file"
    return cleaned[:120]


class LocalStorage:
    """Stores files under a root directory and maps them to /media URLs."""

    def __init__(self, root: Path) -> None:
        self._root = root.resolve()
        self._root.mkdir(parents=True, exist_ok=True)

    @property
    def root(self) -> Path:
        """The storage root directory."""
        return self._root

    def allocate(self, subdir: str, suffix: str, original_name: str | None = None) -> Path:
        """Return a unique, non-colliding path within a subdirectory."""
        target_dir = self._root / subdir
        target_dir.mkdir(parents=True, exist_ok=True)
        token = uuid.uuid4().hex
        stem = sanitize_filename(original_name) if original_name else "file"
        return target_dir / f"{token}_{stem}{suffix}"

    def write_bytes(self, subdir: str, suffix: str, data: bytes, original_name: str) -> Path:
        """Persist raw bytes and return the stored path."""
        path = self.allocate(subdir, suffix, original_name)
        path.write_bytes(data)
        return path

    def media_url(self, path: Path) -> str:
        """Return the public /media URL for a stored path."""
        relative = path.resolve().relative_to(self._root)
        return f"{_MEDIA_PREFIX}/{relative.as_posix()}"
