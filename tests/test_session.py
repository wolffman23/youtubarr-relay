import asyncio
import sys

import pytest

from youtubarr_relay.config import Channel, RelaySettings
from youtubarr_relay.session import RelayManager, ResolverUnavailable


@pytest.mark.asyncio
async def test_session_emits_resolver_bytes_and_releases() -> None:
    command = (sys.executable, "-c", "import sys; sys.stdout.buffer.write(b'HELLO')")
    manager = RelayManager(RelaySettings(resolver_command=command, channels=(Channel(key="one", title="One", source_ref="id"),)))
    iterator = await manager.subscribe("one")
    payload = b"".join([chunk async for chunk in iterator])
    assert payload == b"HELLO"
    await asyncio.sleep(0)
    assert manager.active_count == 0


@pytest.mark.asyncio
async def test_two_viewers_receive_the_same_relay_bytes() -> None:
    command = (
        sys.executable,
        "-c",
        "import sys,time; time.sleep(0.05); sys.stdout.buffer.write(b'FANOUT'); sys.stdout.flush()",
    )
    manager = RelayManager(RelaySettings(resolver_command=command, channels=(Channel(key="one", title="One", source_ref="id"),)))
    first = await manager.subscribe("one")
    second = await manager.subscribe("one")
    assert manager.active_count == 1

    async def consume(iterator):
        return b"".join([chunk async for chunk in iterator])

    first_bytes, second_bytes = await asyncio.gather(consume(first), consume(second))
    assert first_bytes == second_bytes == b"FANOUT"


@pytest.mark.asyncio
async def test_session_fails_closed_without_first_byte() -> None:
    command = (sys.executable, "-c", "raise SystemExit(4)")
    manager = RelayManager(RelaySettings(resolver_command=command, channels=(Channel(key="one", title="One", source_ref="id"),)))
    with pytest.raises(ResolverUnavailable):
        await manager.subscribe("one")
