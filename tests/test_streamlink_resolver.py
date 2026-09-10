from pathlib import Path

import pytest

from youtubarr_relay.streamlink_resolver import build_command, normalize_source


def test_normalize_source_converts_handle_and_channel_id() -> None:
    assert normalize_source("bobandtomshow") == "https://www.youtube.com/@bobandtomshow"
    assert normalize_source("@bobandtomshow") == "https://www.youtube.com/@bobandtomshow"
    assert normalize_source("UC123") == "https://www.youtube.com/channel/UC123"


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
