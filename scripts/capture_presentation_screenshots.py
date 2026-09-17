"""Capture real application screens through headless Chrome for the pitch deck."""

from __future__ import annotations

import base64
import json
import os
import subprocess
import time
import urllib.request
from pathlib import Path
from typing import Any

from websockets.sync.client import connect

CHROME = Path("/Applications/Google Chrome.app/Contents/MacOS/Google Chrome")
OUTPUT = Path("docs/presentation/assets/screenshots")
DEBUG_PORT = 9223


class DevTools:
    def __init__(self, websocket_url: str) -> None:
        self._socket = connect(websocket_url, max_size=None, legacy=True)
        self._counter = 0

    def call(self, method: str, params: dict[str, Any] | None = None) -> dict[str, Any]:
        self._counter += 1
        request_id = self._counter
        self._socket.send(json.dumps({"id": request_id, "method": method, "params": params or {}}))
        while True:
            message = json.loads(self._socket.recv())
            if message.get("id") == request_id:
                if "error" in message:
                    raise RuntimeError(str(message["error"]))
                return dict(message.get("result", {}))

    def close(self) -> None:
        self._socket.close()


def _wait_for_debugger() -> None:
    endpoint = f"http://127.0.0.1:{DEBUG_PORT}/json/version"
    for _ in range(80):
        try:
            urllib.request.urlopen(endpoint, timeout=0.5).close()
            return
        except OSError:
            time.sleep(0.1)
    raise RuntimeError("Chrome DevTools did not start")


def _new_page() -> str:
    request = urllib.request.Request(
        f"http://127.0.0.1:{DEBUG_PORT}/json/new?http://127.0.0.1:5173/",
        method="PUT",
    )
    with urllib.request.urlopen(request, timeout=5) as response:
        return str(json.load(response)["webSocketDebuggerUrl"])


def _navigate(devtools: DevTools, url: str, delay: float = 2.0) -> None:
    devtools.call("Page.navigate", {"url": url})
    time.sleep(delay)


def _evaluate(devtools: DevTools, expression: str) -> Any:
    result = devtools.call(
        "Runtime.evaluate",
        {"expression": expression, "awaitPromise": True, "returnByValue": True},
    )
    return result.get("result", {}).get("value")


def _capture(devtools: DevTools, name: str, scroll_y: int = 0) -> None:
    _evaluate(devtools, f"window.scrollTo({{top: {scroll_y}, behavior: 'instant'}})")
    time.sleep(1.2)
    result = devtools.call(
        "Page.captureScreenshot",
        {"format": "png", "fromSurface": True, "captureBeyondViewport": False},
    )
    OUTPUT.mkdir(parents=True, exist_ok=True)
    (OUTPUT / name).write_bytes(base64.b64decode(result["data"]))
    print(f"captured {name}")


def main() -> None:
    email = os.environ.get("AGROVISION_SCREENSHOT_EMAIL")
    password = os.environ.get("AGROVISION_SCREENSHOT_PASSWORD")
    if not email or not password:
        raise SystemExit("Set AGROVISION_SCREENSHOT_EMAIL and AGROVISION_SCREENSHOT_PASSWORD")
    if not CHROME.exists():
        raise SystemExit(f"Google Chrome not found: {CHROME}")

    profile = Path("/tmp/agrovision-presentation-chrome")
    process = subprocess.Popen(
        [
            str(CHROME),
            "--headless=new",
            f"--remote-debugging-port={DEBUG_PORT}",
            f"--user-data-dir={profile}",
            "--hide-scrollbars",
            "--no-first-run",
            "about:blank",
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
    try:
        _wait_for_debugger()
        devtools = DevTools(_new_page())
        try:
            devtools.call("Page.enable")
            devtools.call("Runtime.enable")
            devtools.call(
                "Emulation.setDeviceMetricsOverride",
                {"width": 1440, "height": 900, "deviceScaleFactor": 1, "mobile": False},
            )
            _navigate(devtools, "http://127.0.0.1:5173/")
            _capture(devtools, "01-landing.png")

            script = f"""
                (async () => {{
                    const response = await fetch('http://127.0.0.1:8000/v1/auth/login', {{
                        method: 'POST',
                        headers: {{'Content-Type': 'application/json'}},
                        body: JSON.stringify({{
                            email: {json.dumps(email)},
                            password: {json.dumps(password)}
                        }})
                    }});
                    const data = await response.json();
                    localStorage.setItem('agrovision_access', data.access_token);
                    localStorage.setItem('agrovision_refresh', data.refresh_token);
                    return response.status;
                }})()
            """
            if _evaluate(devtools, script) != 200:
                raise RuntimeError("Could not authenticate screenshot browser")

            _navigate(devtools, "http://127.0.0.1:5173/app", delay=5.0)
            _capture(devtools, "02-dashboard-top.png")
            _capture(devtools, "03-dashboard-controls.png", scroll_y=700)
            _capture(devtools, "04-dashboard-streams.png", scroll_y=1350)
            _navigate(devtools, "http://127.0.0.1:5173/app/upload")
            _capture(devtools, "05-upload.png")
            _navigate(devtools, "http://127.0.0.1:5173/app/examples", delay=3.0)
            _capture(devtools, "06-examples.png", scroll_y=250)
        finally:
            devtools.close()
    finally:
        process.terminate()
        process.wait(timeout=10)


if __name__ == "__main__":
    main()
