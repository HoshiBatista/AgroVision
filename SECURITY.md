# Security policy

AgroVision processes uploaded media, authentication credentials, model artifacts,
database records, and optional RTSP addresses. Security reports are handled
separately from ordinary bug reports.

## Supported versions

The project has not published long-term-support releases. Security fixes target
the latest commit on `main` and the current `0.1.x` development line.

| Version | Security support |
|---|---|
| Latest `main` | Supported |
| `0.1.x` | Best effort |
| Older snapshots | Not supported |

## Reporting a vulnerability

Do not open a public issue for a suspected vulnerability or include exploit
details, credentials, tokens, private media, or RTSP addresses in public channels.

Preferred process:

1. Open the repository's **Security** tab on GitHub.
2. Select **Report a vulnerability** to create a private security advisory.
3. Describe the affected revision, entry point, impact, and safe reproduction.
4. Include only synthetic or redacted evidence.

If private security advisories are unavailable, contact a repository maintainer
privately and ask for a secure reporting channel. Do not send secrets until that
channel is confirmed.

Maintainers should acknowledge reports, reproduce them in an isolated environment,
assess affected versions, prepare a fix and regression test, and coordinate public
disclosure after users have a reasonable opportunity to update.

## In-scope security areas

- authentication, authorization, token validation, and password storage;
- upload validation, decompression or pixel bombs, and path traversal;
- RTSP URI disclosure, server-side request forgery, and reconnect behavior;
- model checkpoint substitution and unsafe artifact loading;
- SQL injection, cross-user report access, and migration safety;
- request queue exhaustion, inference denial of service, and timeout handling;
- container privilege, exposed ports, writable mounts, and secret injection;
- accidental logging or committing of images, tokens, or personal metadata.

## Security baseline

- Passwords are hashed with Argon2.
- Access and refresh tokens have separate configured lifetimes.
- Non-development environments reject the public placeholder JWT secret.
- Uploads are bounded by bytes, decoded media type, dimensions, and frame limits.
- Filenames are not trusted as media-type evidence or storage paths.
- Every request receives an `X-Request-ID`; raw media and tokens are not logged by
  default.
- The selected model is verified by SHA-256 and target class before readiness.
- Inference uses a bounded queue with wait and execution timeouts.
- RTSP URIs stay server-side and are omitted from response schemas.
- The API container runs as a non-root user; model and demo inputs are read-only.
- PostgreSQL and the API bind to loopback in the provided Docker profile.

## Deployment responsibilities

The repository configuration is a self-contained demo baseline, not a complete
internet-facing security posture. Operators are responsible for:

- TLS termination and secure headers at the external boundary;
- a secret manager and regular JWT/database credential rotation;
- HttpOnly, Secure, SameSite cookies or another reviewed token-storage design;
- network allowlists and egress controls for RTSP sources;
- internal-only database networking and encrypted backups;
- dependency, container, and base-image vulnerability scanning;
- rate limits, request budgets, monitoring, alerting, and incident response;
- retention and deletion policies for uploaded agricultural media.

See the [operations runbook](docs/OPERATIONS.md) before deploying beyond a local
demonstration.

## Secret handling

Never commit, print, quote, or copy values from `.env`. Use `.env.example` only as
a list of variable names and safe placeholders. If a secret is exposed:

1. revoke or rotate it immediately;
2. determine where it was logged, cached, or copied;
3. remove it from the current tree and, when necessary, coordinate history
   rewriting with all repository users;
4. document the incident without reproducing the secret;
5. add a regression control or scanner rule.

## Safe research

Use local synthetic data and a dedicated test database. Do not test against farms,
camera networks, accounts, or infrastructure without explicit authorization. Stop
testing if it could affect animal operations, overwrite records, expose private
imagery, or degrade a live monitoring feed.
