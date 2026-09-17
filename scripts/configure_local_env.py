"""Add secure local defaults to .env without exposing or replacing user secrets."""

from __future__ import annotations

import argparse
import secrets
from pathlib import Path

INSECURE_JWT = "change-me-in-production-use-a-32-byte-random-hex"
INSECURE_DB_PASSWORDS = {"agrovision", "change-me-before-docker-start"}
MODEL_SHA256 = "29561fa0c96052b9efac892a1dd4a6418508992f4c882b661d08afe5ba124e0d"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--path", type=Path, default=Path(".env"))
    parser.add_argument("--device", choices=("auto", "mps", "cpu", "cuda"), default="auto")
    parser.add_argument("--database", choices=("sqlite", "postgres"), default="sqlite")
    return parser.parse_args()


def _values(lines: list[str]) -> dict[str, str]:
    values: dict[str, str] = {}
    for line in lines:
        key, separator, value = line.partition("=")
        if separator and key and not key.startswith("#"):
            values[key.strip()] = value.strip()
    return values


def _upsert(
    lines: list[str],
    key: str,
    value: str,
    *,
    replace: set[str] | None = None,
    force: bool = False,
) -> None:
    prefix = f"{key}="
    for index, line in enumerate(lines):
        if line.startswith(prefix):
            current = line[len(prefix) :].strip()
            if force or (replace is not None and current in replace):
                lines[index] = f"{prefix}{value}"
            return
    lines.append(f"{prefix}{value}")


def configure(path: Path, device: str, database: str) -> None:
    """Preserve existing values and fill missing or publicly known secrets."""
    text = path.read_text() if path.exists() else ""
    lines = text.splitlines()
    existing = _values(lines)

    jwt_secret = existing.get("JWT_SECRET", "")
    if not jwt_secret or jwt_secret == INSECURE_JWT or len(jwt_secret) < 32:
        jwt_secret = secrets.token_hex(32)
        _upsert(lines, "JWT_SECRET", jwt_secret, replace={existing.get("JWT_SECRET", "")})

    database_password = existing.get("POSTGRES_PASSWORD", "")
    if not database_password or database_password in INSECURE_DB_PASSWORDS:
        database_password = secrets.token_hex(24)
        _upsert(
            lines,
            "POSTGRES_PASSWORD",
            database_password,
            replace={existing.get("POSTGRES_PASSWORD", "")},
        )

    if database == "sqlite":
        database_url = "sqlite+aiosqlite:///./artifacts/agrovision.db"
    else:
        database_url = (
            f"postgresql+asyncpg://agrovision:{database_password}@localhost:5432/agrovision"
        )
    _upsert(lines, "DATABASE_URL", database_url, force=True)
    _upsert(lines, "MODEL_DEVICE", device, force=True)
    _upsert(lines, "DETECTOR_MODEL_VERSION", "yolo26n-aerial-sheep-v1-best-e10")
    _upsert(lines, "DETECTOR_MODEL_SHA256", MODEL_SHA256)
    _upsert(lines, "DETECTOR_ALLOW_FALLBACK", "false")
    _upsert(lines, "MAX_UPLOAD_MB", "100", replace={"50"})

    path.write_text("\n".join(lines).rstrip() + "\n")
    path.chmod(0o600)
    print(f"Configured {path} with protected local values (secret values were not printed).")


def main() -> None:
    args = parse_args()
    configure(args.path, args.device, args.database)


if __name__ == "__main__":
    main()
