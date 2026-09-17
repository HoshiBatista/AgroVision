"""Environment-driven application settings, validated on startup."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path

from pydantic import Field, model_validator
from pydantic_settings import BaseSettings, SettingsConfigDict

# The placeholder secret shipped in .env.example. Refusing to run with it outside
# development prevents accidentally signing tokens with a publicly known key.
INSECURE_JWT_SECRET = "change-me-in-production-use-a-32-byte-random-hex"
_DEV_ENVS = {"development", "test", "ci"}


class Settings(BaseSettings):
    """Typed application configuration loaded from the environment / .env."""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
        case_sensitive=False,
        protected_namespaces=(),
    )

    app_env: str = "development"
    log_level: str = "INFO"

    # API
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    cors_allow_origins: str = "http://localhost:5173,http://127.0.0.1:5173"

    # Database
    database_url: str = "sqlite+aiosqlite:///./artifacts/agrovision.db"

    # Auth / JWT
    jwt_secret: str = INSECURE_JWT_SECRET
    jwt_algorithm: str = "HS256"
    jwt_access_ttl_minutes: int = 30
    jwt_refresh_ttl_days: int = 7

    # Model
    model_device: str = "auto"
    detector_model_path: Path = Path("artifacts/training/yolo26n-aerial-sheep-v1/weights/best.pt")
    detector_model_version: str = "yolo26n-aerial-sheep-v1-best-e10"
    detector_model_sha256: str = "29561fa0c96052b9efac892a1dd4a6418508992f4c882b661d08afe5ba124e0d"
    detector_allow_fallback: bool = False
    detector_fallback_checkpoint: str = "yolo26n.pt"
    detector_target_class: str = "sheep"
    detector_inference_floor: float = Field(default=0.25, ge=0.0, le=1.0)
    detector_confidence_threshold: float = Field(default=0.40, ge=0.0, le=1.0)
    detector_image_size: int = Field(default=640, ge=32)
    detector_queue_capacity: int = Field(default=8, ge=1, le=128)
    detector_queue_wait_seconds: float = Field(default=5.0, gt=0.0)
    detector_inference_timeout_seconds: float = Field(default=600.0, gt=0.0)

    # Uploads
    max_upload_mb: int = 100
    max_image_pixels: int = 50_000_000
    storage_root: Path = Path("artifacts/uploads")
    demo_artifacts_root: Path = Path("artifacts/demo_predictions")

    # Video inference
    video_max_processed_frames: int = Field(default=600, ge=1)
    video_keyframes: int = Field(default=8, ge=1)

    # Streaming
    streams_config_path: Path = Path("configs/app.toml")
    stream_frame_stride: int = Field(default=3, ge=1)
    stream_jpeg_quality: int = Field(default=75, ge=1, le=100)
    stream_target_fps: int = Field(default=8, ge=1, le=60)
    rtsp_open_timeout_ms: int = Field(default=5000, ge=1000, le=60000)
    rtsp_read_timeout_ms: int = Field(default=5000, ge=1000, le=60000)
    rtsp_reconnect_seconds: float = Field(default=2.0, ge=0.25, le=60.0)

    @model_validator(mode="after")
    def _enforce_secure_secret(self) -> Settings:
        """Refuse to start with a weak/known JWT secret outside development."""
        if self.detector_inference_floor > self.detector_confidence_threshold:
            raise ValueError("DETECTOR_INFERENCE_FLOOR must not exceed the confidence threshold")
        if self.app_env.lower() not in _DEV_ENVS and (
            self.jwt_secret == INSECURE_JWT_SECRET or len(self.jwt_secret) < 32
        ):
            raise ValueError(
                "JWT_SECRET must be a strong secret of at least 32 characters "
                f"when APP_ENV is '{self.app_env}'. Generate one with "
                "`openssl rand -hex 32`."
            )
        return self

    @property
    def is_development(self) -> bool:
        """Whether the app runs in a development-like environment."""
        return self.app_env.lower() in _DEV_ENVS

    @property
    def cors_origins(self) -> list[str]:
        """Return CORS origins as a clean list."""
        return [origin.strip() for origin in self.cors_allow_origins.split(",") if origin.strip()]

    @property
    def max_upload_bytes(self) -> int:
        """Return the maximum upload size in bytes."""
        return self.max_upload_mb * 1024 * 1024


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """Return a cached Settings instance."""
    return Settings()
