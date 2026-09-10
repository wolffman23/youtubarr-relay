"""Thin Dispatcharr-facing package; playback is owned by the companion relay."""

from __future__ import annotations


class YouTubarrRelayPlugin:
    name = "YouTubarr Relay"
    version = "0.1.0"

    def actions(self) -> list[str]:
        return ["validate", "diagnostics"]

    def run(self, action: str, params: dict[str, object] | None = None) -> dict[str, object]:
        if action == "validate":
            return {"ok": True, "message": "Configure the relay endpoint as a custom stream source."}
        if action == "diagnostics":
            return {"ok": True, "actions": self.actions(), "secrets_exposed": False}
        return {"ok": False, "error": "unknown_action"}
