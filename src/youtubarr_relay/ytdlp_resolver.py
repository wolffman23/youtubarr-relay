from __future__ import annotations

import os
from pathlib import Path

from youtubarr_relay.streamlink_resolver import normalize_source


def main() -> None:
    source = normalize_source(os.environ.get("YOUTUBARR_SOURCE_REF", ""))
    command = [
        "yt-dlp", "--no-warnings", "--quiet", "--js-runtimes", "quickjs:/usr/bin/qjs",
        "--live-from-start", "-f", "best", "-o", "-", source,
    ]
    cookie = os.environ.get("YOUTUBARR_COOKIE_FILE")
    if cookie:
        command[1:1] = ["--cookies", str(Path(cookie))]
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
