from __future__ import annotations

import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

from youtubarr_relay.streamlink_resolver import normalize_source


def main() -> None:
    source = normalize_source(os.environ.get("YOUTUBARR_SOURCE_REF", ""))
    with tempfile.TemporaryDirectory(prefix="youtubarr-ytdlp-") as temp_dir:
        command = [
            "yt-dlp", "--no-warnings", "--quiet", "--js-runtimes", "quickjs:/usr/bin/qjs",
            "--live-from-start", "-f", "bestvideo", "-o", "-", source,
        ]
        cookie = os.environ.get("YOUTUBARR_COOKIE_FILE")
        if cookie:
            writable_cookie = Path(temp_dir) / "cookies.txt"
            shutil.copyfile(cookie, writable_cookie)
            command[1:1] = ["--cookies", str(writable_cookie)]
        ytdlp = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        ffmpeg = subprocess.Popen(
            ["ffmpeg", "-hide_banner", "-loglevel", "error", "-i", "pipe:0", "-map", "0:v:0", "-c:v", "copy", "-f", "mpegts", "pipe:1"],
            stdin=ytdlp.stdout,
            stdout=sys.stdout.buffer,
            stderr=sys.stderr.buffer,
        )
        if ytdlp.stdout:
            ytdlp.stdout.close()
        code = ffmpeg.wait()
        ytdlp.wait()
        raise SystemExit(code or ytdlp.returncode or 0)


if __name__ == "__main__":
    main()
