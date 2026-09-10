from __future__ import annotations

import ipaddress
from collections.abc import Sequence
from pathlib import Path
from typing import Annotated

from pydantic import BaseModel, Field, field_validator, model_validator


class Channel(BaseModel, frozen=True):
    key: Annotated[str, Field(pattern=r"^[a-z0-9][a-z0-9_-]{0,63}$")]
    title: Annotated[str, Field(min_length=1, max_length=200)]
    source_ref: Annotated[str, Field(min_length=1)]


class RelaySettings(BaseModel, frozen=True):
    bind_host: str = "127.0.0.1"
    resolver_command: tuple[str, ...]
    resolver_timeout_seconds: Annotated[float, Field(gt=0, le=60)] = 15
    cookie_file: Path | None = None
    internal_token: str | None = None
    channels: tuple[Channel, ...] = ()

    @field_validator("bind_host")
    @classmethod
    def only_allow_internal_bind(cls, value: str) -> str:
        if value in {"0.0.0.0", "::", "localhost"}:
            return value
        try:
            address = ipaddress.ip_address(value)
        except ValueError as exc:
            raise ValueError("bind host must be internal") from exc
        if not (address.is_private or address.is_loopback):
            raise ValueError("bind host must be internal")
        return value

    @field_validator("resolver_command")
    @classmethod
    def command_must_not_be_empty(cls, value: Sequence[str]) -> tuple[str, ...]:
        command = tuple(value)
        if not command or any(not item.strip() for item in command):
            raise ValueError("resolver command must be non-empty")
        return command

    @field_validator("cookie_file")
    @classmethod
    def cookie_file_must_be_absolute(cls, value: Path | None) -> Path | None:
        if value is not None and not value.is_absolute():
            raise ValueError("cookie file must be an absolute secret mount path")
        return value

    @model_validator(mode="after")
    def channel_keys_must_be_unique(self) -> RelaySettings:
        keys = [channel.key for channel in self.channels]
        if len(keys) != len(set(keys)):
            raise ValueError("channel keys must be unique")
        return self

    def public_diagnostics(self) -> dict[str, object]:
        return {
            "channel_count": len(self.channels),
            "resolver_configured": bool(self.resolver_command),
            "auth_required": self.internal_token is not None,
        }
