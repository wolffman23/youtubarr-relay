# YouTubarr Relay

A session-owning internal playback relay for Dispatcharr custom streams.

## Why this exists

Upstream media URLs can be short lived and can require the same request context that resolved them. This project keeps resolution and segment retrieval in one supervised relay process, then exposes a stable internal MPEG-TS endpoint to Dispatcharr.

The relay deliberately stores only stable channel identifiers in its configuration. It does **not** log upstream URLs, cookies, authorization headers, or signed parameters.

## Boundaries

- The relay is intended for internal Docker/LAN use only.
- A resolver command is operator supplied and receives source identity via environment variables, not shell interpolation.
- Cookie material, if required by an authorized source, lives in an external `0600` secret mount and is never committed.
- A relay response starts only after the resolver produces bytes; failure is surfaced as a safe typed error.
- The included Dispatcharr plugin package is a thin metadata/diagnostics integration. Long-running playback remains in the companion relay.

## Development

```bash
uv run pytest -q
uv run ruff check .
python scripts/build_plugin_zip.py
```

## Deployment status

This repository is source and packaging only. It does not modify or deploy to an existing Dispatcharr installation.

See `docs/operations.md` and `docs/dispatcharr-integration.md` after build completion.
