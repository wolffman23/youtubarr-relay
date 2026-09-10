import sys

from fastapi.testclient import TestClient

from youtubarr_relay.app import create_app
from youtubarr_relay.config import Channel, RelaySettings


def test_health_and_public_channel_list() -> None:
    app = create_app(RelaySettings(resolver_command=(sys.executable, "-c", "pass"), channels=(Channel(key="weather", title="Weather", source_ref="secret-ref"),)))
    client = TestClient(app)
    assert client.get("/healthz").json() == {"status": "ok", "active_sessions": 0}
    response = client.get("/v1/channels")
    assert response.status_code == 200
    assert response.json() == {"channels": [{"key": "weather", "title": "Weather"}]}
    assert "secret-ref" not in response.text


def test_stream_returns_bytes() -> None:
    command = (sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'TS')")
    app = create_app(RelaySettings(resolver_command=command, channels=(Channel(key="weather", title="Weather", source_ref="id"),)))
    response = TestClient(app).get("/v1/streams/weather.ts")
    assert response.status_code == 200
    assert response.content == b"TS"


def test_failed_resolver_is_safe_bad_gateway() -> None:
    command = (sys.executable, "-c", "raise SystemExit(2)")
    app = create_app(RelaySettings(resolver_command=command, channels=(Channel(key="weather", title="Weather", source_ref="never-show"),)))
    response = TestClient(app).get("/v1/streams/weather.ts")
    assert response.status_code == 502
    assert response.json() == {"detail": "upstream_unavailable"}
    assert "never-show" not in response.text
