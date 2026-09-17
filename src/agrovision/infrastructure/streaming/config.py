"""Load stream source definitions from the app config TOML."""

from __future__ import annotations

import tomllib
from pathlib import Path

from agrovision.domain.stream import StreamSource


def load_stream_sources(path: Path) -> list[StreamSource]:
    """Parse configured stream sources; returns an empty list if the file is absent."""
    if not path.exists():
        return []
    data = tomllib.loads(path.read_text())
    sources: list[StreamSource] = []
    for entry in data.get("streams", []):
        sources.append(
            StreamSource(
                id=str(entry["id"]),
                name=str(entry["name"]),
                location=str(entry["location"]),
                uri=str(entry["uri"]),
                kind=str(entry.get("kind", "file")),
            )
        )
    return sources


def startable_sources(sources: list[StreamSource]) -> list[StreamSource]:
    """Keep only sources that can actually be opened (existing files)."""
    startable: list[StreamSource] = []
    for source in sources:
        if source.kind != "file" or Path(source.uri).exists():
            startable.append(source)
    return startable
