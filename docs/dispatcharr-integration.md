# Dispatcharr integration

The relay is a separate service. Do not run it inside a Dispatcharr plugin worker.

## Mapping a channel

1. Put the relay and Dispatcharr on the same internal Docker network.
2. Configure a stable custom stream URL in Dispatcharr:

   ```text
   http://youtubarr-relay:8788/v1/streams/<channel-key>.ts
   ```

3. Use Dispatcharr's normal Proxy path for the local MPEG-TS source.
4. Keep the upstream source identity only in the relay's private `channels.json` configuration.

## Pre-deployment gate

Before adding a live custom stream, prove all of the following from inside the relay network:

- `GET /healthz` returns `200`.
- `GET /v1/channels` lists only key/title metadata.
- A test request to `/v1/streams/<key>.ts` receives bytes.
- A resolver failure returns `502 {"detail":"upstream_unavailable"}`.
- Logs contain neither upstream URLs nor cookie/header material.

The companion does not create or modify Dispatcharr channels automatically. This is intentional: mapping changes remain operator-reviewed and reversible.
