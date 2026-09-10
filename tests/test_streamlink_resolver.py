from pathlib import Path

import pytest

from youtubarr_relay.streamlink_resolver import build_command


def test_streamlink_command_uses_cookie_file_without_exposing_cookie_content() -> None:
    command = build_command("https://provider.example/live", Path("/run/secrets/cookies.txt"))
    assert command == [
        "streamlink",
        "--stdout",
        "--http-cookies-file",
        "/run/secrets/cookies.txt",
        "https://provider.example/live",
        "best",
    ]


def test_streamlink_command_rejects_blank_source() -> None:
    with pytest.raises(ValueError, match="required"):
        build_command("", None)
