"""Unit tests for detector device/weights resolution (no model download)."""

from __future__ import annotations

import hashlib
from pathlib import Path

import pytest

import agrovision.infrastructure.ml.yolo_detector as detector_module
from agrovision.config import Settings
from agrovision.infrastructure.ml.yolo_detector import resolve_device


def test_resolve_device_explicit_passthrough() -> None:
    assert resolve_device("cpu") == "cpu"
    assert resolve_device("cuda:1") == "cuda:1"


def test_resolve_device_auto_prefers_cuda(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(detector_module.torch.cuda, "is_available", lambda: True)
    assert resolve_device("auto") == "cuda"


def test_resolve_device_auto_falls_back_to_mps(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(detector_module.torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(detector_module.torch.backends.mps, "is_available", lambda: True)
    assert resolve_device("auto") == "mps"


def test_resolve_device_auto_falls_back_to_cpu(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setattr(detector_module.torch.cuda, "is_available", lambda: False)
    monkeypatch.setattr(detector_module.torch.backends.mps, "is_available", lambda: False)
    assert resolve_device("auto") == "cpu"


def test_resolve_weights_rejects_missing_selected_model(tmp_path: Path) -> None:
    settings = Settings(
        detector_model_path=tmp_path / "missing" / "best.pt",
        detector_fallback_checkpoint="yolo26n.pt",
    )
    with pytest.raises(FileNotFoundError, match="Selected model is missing"):
        detector_module._resolve_weights(settings)


def test_resolve_weights_uses_explicit_fallback_when_missing(tmp_path: Path) -> None:
    settings = Settings(
        detector_model_path=tmp_path / "missing" / "best.pt",
        detector_fallback_checkpoint="yolo26n.pt",
        detector_allow_fallback=True,
    )
    weights, version, digest = detector_module._resolve_weights(settings)
    assert weights == Path("yolo26n.pt")
    assert version == "pretrained-yolo26n-fallback"
    assert digest == "unverified"


def test_resolve_weights_uses_trained_when_present(tmp_path: Path) -> None:
    best = tmp_path / "artifacts" / "training" / "my-run" / "weights" / "best.pt"
    best.parent.mkdir(parents=True)
    best.write_bytes(b"stub")
    digest = hashlib.sha256(b"stub").hexdigest()
    settings = Settings(
        detector_model_path=best,
        detector_model_version="my-run-best",
        detector_model_sha256=digest,
    )
    weights, version, actual_digest = detector_module._resolve_weights(settings)
    assert weights == best
    assert version == "my-run-best"
    assert actual_digest == digest


def test_resolve_weights_rejects_checksum_mismatch(tmp_path: Path) -> None:
    best = tmp_path / "best.pt"
    best.write_bytes(b"tampered")
    settings = Settings(detector_model_path=best, detector_model_sha256="0" * 64)
    with pytest.raises(RuntimeError, match="checksum mismatch"):
        detector_module._resolve_weights(settings)
