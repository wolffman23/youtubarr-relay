import pytest
from pydantic import ValidationError

from youtubarr_relay.config import RelaySettings


def test_settings_reject_public_bind() -> None:
    with pytest.raises(ValidationError, match="internal"):
        RelaySettings(bind_host="8.8.8.8", resolver_command=("resolver",))


def test_settings_reject_empty_resolver() -> None:
    with pytest.raises(ValidationError):
        RelaySettings(resolver_command=())


def test_public_diagnostics_do_not_include_source_or_cookie_path() -> None:
    settings = RelaySettings(
        resolver_command=("resolver",),
        cookie_file="/run/secrets/cookies.txt",
        channels=(
            {"key": "weather", "title": "Weather", "source_ref": "private-source-reference"},
        ),
    )
    text = str(settings.public_diagnostics())
    assert "private-source-reference" not in text
    assert "cookies.txt" not in text
    assert text == "{'channel_count': 1, 'resolver_configured': True, 'auth_required': False}"
