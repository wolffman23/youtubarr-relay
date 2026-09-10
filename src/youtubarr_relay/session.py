from __future__ import annotations

import asyncio
import os
from collections.abc import AsyncIterator
from dataclasses import dataclass, field

from youtubarr_relay.config import Channel, RelaySettings


class ResolverUnavailable(RuntimeError):
    """Resolver failed before producing safe relay bytes."""


@dataclass
class _Session:
    process: asyncio.subprocess.Process
    first_chunk: bytes
    subscribers: set[asyncio.Queue[bytes | None]] = field(default_factory=set)
    pump: asyncio.Task[None] | None = None


class RelayManager:
    def __init__(self, settings: RelaySettings) -> None:
        self._settings = settings
        self._channels = {channel.key: channel for channel in settings.channels}
        self._sessions: dict[str, _Session] = {}
        self._lock = asyncio.Lock()

    @property
    def active_count(self) -> int:
        return len(self._sessions)

    def channel(self, key: str) -> Channel | None:
        return self._channels.get(key)

    async def subscribe(self, key: str) -> AsyncIterator[bytes]:
        channel = self.channel(key)
        if channel is None:
            raise KeyError(key)
        async with self._lock:
            session = self._sessions.get(key)
            if session is None or session.process.returncode is not None:
                session = await self._start(channel)
                self._sessions[key] = session
            queue: asyncio.Queue[bytes | None] = asyncio.Queue()
            queue.put_nowait(session.first_chunk)
            session.subscribers.add(queue)
            if session.pump is None:
                session.pump = asyncio.create_task(self._pump(key, session))
        return self._iterate(key, session, queue)

    async def _start(self, channel: Channel) -> _Session:
        environment = os.environ.copy()
        environment["YOUTUBARR_SOURCE_REF"] = channel.source_ref
        if self._settings.cookie_file is not None:
            environment["YOUTUBARR_COOKIE_FILE"] = str(self._settings.cookie_file)
        try:
            process = await asyncio.create_subprocess_exec(
                *self._settings.resolver_command,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.DEVNULL,
                env=environment,
            )
            assert process.stdout is not None
            first_chunk = await asyncio.wait_for(process.stdout.read(188), self._settings.resolver_timeout_seconds)
        except (OSError, TimeoutError) as exc:
            raise ResolverUnavailable("upstream_unavailable") from exc
        if not first_chunk:
            await process.wait()
            raise ResolverUnavailable("upstream_unavailable")
        return _Session(process=process, first_chunk=first_chunk)

    async def _pump(self, key: str, session: _Session) -> None:
        try:
            assert session.process.stdout is not None
            while chunk := await session.process.stdout.read(64 * 1024):
                for queue in tuple(session.subscribers):
                    queue.put_nowait(chunk)
        finally:
            for queue in tuple(session.subscribers):
                queue.put_nowait(None)
            async with self._lock:
                if self._sessions.get(key) is session:
                    self._sessions.pop(key, None)

    async def _iterate(
        self, key: str, session: _Session, queue: asyncio.Queue[bytes | None]
    ) -> AsyncIterator[bytes]:
        try:
            while (chunk := await queue.get()) is not None:
                yield chunk
        finally:
            async with self._lock:
                session.subscribers.discard(queue)
                if not session.subscribers and session.process.returncode is None:
                    session.process.terminate()
