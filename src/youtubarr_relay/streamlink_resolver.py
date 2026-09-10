from __future__ import annotations

import os
from pathlib import Path


def build_command(source_ref: str, cookie_file: Path | None, quality: str = "best") -> list[str]:
    if not source_ref.strip():
        raise ValueError("YOUTUBARR_SOURCE_REF is required")
    command = [os.environ.get("STREAMLINK_BIN", "streamlink"), "--stdout"]
    if cookie_file is not None:
        command.extend(["--http-cookies-file", str(cookie_file)])
    command.extend([source_ref, quality])
    return command


def main() -> None:
    source_ref = os.environ.get("YOUTUBARR_SOURCE_REF", "")
    cookie_value = os.environ.get("YOUTUBARR_COOKIE_FILE")
    cookie_file = Path(cookie_value) if cookie_value else None
    command = build_command(source_ref, cookie_file, os.environ.get("YOUTUBARR_STREAM_QUALITY", "best"))
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
