"""Run the API and Vite development server together until interrupted."""

from __future__ import annotations

import os
import signal
import subprocess
import sys
import time
from pathlib import Path


def main() -> None:
    env = os.environ.copy()
    env.setdefault("PYTORCH_ENABLE_MPS_FALLBACK", "1")
    commands = [
        [
            sys.executable,
            "-m",
            "uvicorn",
            "apps.api.main:app",
            "--host",
            "0.0.0.0",
            "--port",
            "8000",
        ],
        ["npm", "run", "dev", "--", "--host", "0.0.0.0"],
    ]
    processes = [
        subprocess.Popen(command, cwd=Path("apps/web") if command[0] == "npm" else None, env=env)
        for command in commands
    ]

    def stop(_signum: int | None = None, _frame: object | None = None) -> None:
        for process in processes:
            if process.poll() is None:
                process.terminate()
        for process in processes:
            try:
                process.wait(timeout=10)
            except subprocess.TimeoutExpired:
                process.kill()

    signal.signal(signal.SIGINT, stop)
    signal.signal(signal.SIGTERM, stop)
    try:
        while all(process.poll() is None for process in processes):
            time.sleep(0.5)
    finally:
        stop()
    failed = next((process.returncode for process in processes if process.returncode), 0)
    raise SystemExit(failed)


if __name__ == "__main__":
    main()
