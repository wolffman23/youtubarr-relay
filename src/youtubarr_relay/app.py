from __future__ import annotations

import hmac

from fastapi import Depends, FastAPI, HTTPException, Request, status
from fastapi.responses import StreamingResponse

from youtubarr_relay.config import RelaySettings
from youtubarr_relay.session import RelayManager, ResolverUnavailable


def create_app(settings: RelaySettings) -> FastAPI:
    app = FastAPI(title="YouTubarr Relay", docs_url=None, redoc_url=None)
    manager = RelayManager(settings)
    app.state.manager = manager

    async def authorize(request: Request) -> None:
        if settings.internal_token is None:
            return
        supplied = request.headers.get("authorization", "").removeprefix("Bearer ")
        if not hmac.compare_digest(supplied, settings.internal_token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="unauthorized")

    @app.get("/healthz")
    async def healthz() -> dict[str, object]:
        return {"status": "ok", "active_sessions": manager.active_count}

    @app.get("/v1/channels", dependencies=[Depends(authorize)])
    async def channels() -> dict[str, object]:
        return {"channels": [{"key": c.key, "title": c.title} for c in settings.channels]}

    @app.get("/v1/streams/{key}.ts", dependencies=[Depends(authorize)])
    async def stream(key: str) -> StreamingResponse:
        if manager.channel(key) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="channel_not_found")
        try:
            iterator = await manager.subscribe(key)
        except ResolverUnavailable as exc:
            raise HTTPException(status_code=status.HTTP_502_BAD_GATEWAY, detail="upstream_unavailable") from exc
        return StreamingResponse(iterator, media_type="video/mp2t")

    @app.get("/v1/diagnostics/{key}", dependencies=[Depends(authorize)])
    async def diagnostics(key: str) -> dict[str, object]:
        if manager.channel(key) is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="channel_not_found")
        return {"channel": key, "active": key in manager._sessions, **settings.public_diagnostics()}

    return app
