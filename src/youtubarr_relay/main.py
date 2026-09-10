from __future__ import annotations

import os
from pathlib import Path

import uvicorn

from youtubarr_relay.app import create_app
from youtubarr_relay.config import RelaySettings


def load_settings(path: Path) -> RelaySettings:
    return RelaySettings.model_validate_json(path.read_text())


def main() -> None:
    config_path = Path(os.environ.get("YOUTUBARR_RELAY_CONFIG", "/config/channels.json"))
    settings = load_settings(config_path)
    uvicorn.run(create_app(settings), host=settings.bind_host, port=8788, log_level="info", access_log=False)


if __name__ == "__main__":
    main()
