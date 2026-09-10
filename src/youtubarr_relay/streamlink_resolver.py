from __future__ import annotations

import os
from pathlib import Path


def normalize_source(source_ref: str) -> str:
    source = source_ref.strip()
    if not source:
        raise ValueError("YOUTUBARR_SOURCE_REF is required")
    if source.startswith(("http://", "https://")):
        return source
    if source.startswith("UC"):
        return f"https://www.youtube.com/channel/{source}/live"
    handle = source if source.startswith("@") else f"@{source}"
    return f"https://www.youtube.com/{handle}/live"


def build_command(source_ref: str, cookie_file: Path | None, quality: str = "best") -> list[str]:
    source = normalize_source(source_ref)
    command = [os.environ.get("STREAMLINK_BIN", "streamlink"), "--stdout"]
    if cookie_file is not None:
        command.extend(["--http-cookies-file", str(cookie_file)])
    command.extend([source, quality])
    return command


def main() -> None:
    source_ref = os.environ.get("YOUTUBARR_SOURCE_REF", "")
    cookie_value = os.environ.get("YOUTUBARR_COOKIE_FILE")
    cookie_file = Path(cookie_value) if cookie_value else None
    command = build_command(source_ref, cookie_file, os.environ.get("YOUTUBARR_STREAM_QUALITY", "best"))
    os.execvp(command[0], command)


if __name__ == "__main__":
    main()
