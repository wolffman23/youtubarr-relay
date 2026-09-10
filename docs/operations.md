# Operations

## Resolver contract

`resolver_command` is an argv list, never a shell expression. The relay starts it with these environment variables:

- `YOUTUBARR_SOURCE_REF`: configured stable source identifier
- `YOUTUBARR_COOKIE_FILE`: optional absolute path to a private cookie mount

The resolver must write MPEG-TS-compatible bytes to standard output. The relay waits for the first bytes before accepting playback. It discards resolver standard error so upstream request material cannot leak into the relay logs.

## Safety controls

- Bind only to loopback/private interfaces or the internal container network.
- Keep cookie/authorization files out of the repository and mount them read-only with restrictive permissions.
- Never put source URLs, cookies, headers, signed parameters, or bearer values in logs, issue reports, or diagnostics.
- A missing/empty/slow resolver fails closed with `upstream_unavailable`.

## Live canary checklist

1. Start the relay with an authorized test resolver.
2. Confirm first bytes arrive from one test channel.
3. Play it through Dispatcharr for ten uninterrupted minutes.
4. Confirm a second viewer does not cause uncontrolled resolver churn.
5. Disconnect viewers and verify the resolver subprocess exits.
6. Reboot/restart the relay and verify failure reporting remains truthful before re-enabling a channel.

No live deployment is included in this repository.
