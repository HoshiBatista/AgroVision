"""Unit tests for settings parsing and local storage safety."""

from __future__ import annotations

from pathlib import Path

import pytest
from pydantic import ValidationError as PydanticValidationError

from agrovision.config import INSECURE_JWT_SECRET, Settings
from agrovision.infrastructure.storage.local_storage import LocalStorage, sanitize_filename


def test_cors_origins_parsed_and_trimmed() -> None:
    settings = Settings(cors_allow_origins="http://a.com, http://b.com ,")
    assert settings.cors_origins == ["http://a.com", "http://b.com"]


def test_max_upload_bytes() -> None:
    assert Settings(max_upload_mb=3).max_upload_bytes == 3 * 1024 * 1024


def test_production_rejects_public_jwt_secret() -> None:
    with pytest.raises(PydanticValidationError, match="JWT_SECRET"):
        Settings(app_env="production", jwt_secret=INSECURE_JWT_SECRET)


def test_detector_floor_must_not_exceed_uncertainty_threshold() -> None:
    with pytest.raises(PydanticValidationError, match="DETECTOR_INFERENCE_FLOOR"):
        Settings(detector_inference_floor=0.5, detector_confidence_threshold=0.4)


def test_sanitize_filename_strips_paths_and_unsafe_chars() -> None:
    assert sanitize_filename("../../etc/passwd") == "passwd"
    assert sanitize_filename("my file (1).MP4") == "my_file_1_.MP4"
    assert sanitize_filename("...") == "file"
    assert sanitize_filename("/tmp/clip.mov").endswith("clip.mov")


def test_sanitize_filename_truncates() -> None:
    assert len(sanitize_filename("a" * 500)) <= 120


def test_local_storage_allocates_unique_paths(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path / "store")
    first = storage.allocate("videos", ".mp4", "clip")
    second = storage.allocate("videos", ".mp4", "clip")
    assert first != second
    assert first.suffix == ".mp4"
    assert first.parent.exists()


def test_local_storage_media_url(tmp_path: Path) -> None:
    storage = LocalStorage(tmp_path / "store")
    path = storage.write_bytes("videos", ".mp4", b"data", "clip")
    url = storage.media_url(path)
    assert url.startswith("/media/videos/")
    assert path.read_bytes() == b"data"
