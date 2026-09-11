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
        resolve = [
            "yt-dlp", "--no-warnings", "--quiet", "--js-runtimes", "quickjs:/usr/bin/qjs",
            "-f", "bestvideo+bestaudio/best", "-g", source,
        ]
        cookie = os.environ.get("YOUTUBARR_COOKIE_FILE")
        if cookie:
            writable_cookie = Path(temp_dir) / "cookies.txt"
            shutil.copyfile(cookie, writable_cookie)
            resolve[1:1] = ["--cookies", str(writable_cookie)]
        resolved = subprocess.run(resolve, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL, timeout=45, check=False)
        manifest = resolved.stdout.decode("utf-8", errors="replace").strip().splitlines()
        if resolved.returncode or not manifest:
            raise SystemExit(1)
        ffmpeg_command = ["ffmpeg", "-hide_banner", "-loglevel", "error"]
        for url in manifest:
            ffmpeg_command.extend(["-i", url])
        audio_input = "1:a:0?" if len(manifest) > 1 else "0:a:0?"
        ffmpeg_command.extend(
            [
                "-map", "0:v:0", "-map", audio_input, "-c:v", "copy", "-c:a", "copy",
                "-f", "mpegts", "pipe:1",
            ]
        )
        ffmpeg = subprocess.Popen(
            ffmpeg_command,
            stdout=sys.stdout.buffer,
            stderr=subprocess.DEVNULL,
        )
        raise SystemExit(ffmpeg.wait())


if __name__ == "__main__":
    main()
