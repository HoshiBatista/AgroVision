# AgroVision API reference

AgroVision exposes the same application use cases used by the web interface
through a versioned FastAPI API. Unless noted otherwise, examples assume the API
is available at `http://localhost:8000`.

In a development environment, the generated OpenAPI interfaces are available at
`/docs`, `/redoc`, and `/openapi.json`. They are disabled outside development.

## Conventions

- Versioned product endpoints use the `/v1` prefix.
- JSON is used for structured requests and responses; uploads use
  `multipart/form-data`.
- Protected endpoints require `Authorization: Bearer <access-token>`.
- Every HTTP response includes `X-Request-ID`. A caller-supplied value is echoed;
  otherwise the server generates one.
- Timestamps are ISO 8601 values. Bounding-box coordinates are absolute pixels.
- Access tokens expire after 30 minutes and refresh tokens after seven days by
  default. Both values are configurable.

## Endpoint summary

| Method | Path | Authentication | Purpose |
|---|---|---|---|
| `GET` | `/health` | No | Process liveness and application version |
| `GET` | `/ready` | No | Model readiness |
| `POST` | `/v1/auth/register` | No | Create a user and issue a token pair |
| `POST` | `/v1/auth/login` | No | Issue a token pair |
| `POST` | `/v1/auth/refresh` | No | Rotate a refresh token |
| `GET` | `/v1/auth/me` | Yes | Return the current user |
| `GET` | `/v1/model-info` | No | Model version, class map, threshold, and limitations |
| `PATCH` | `/v1/model-threshold` | Yes | Change the in-memory operating threshold |
| `POST` | `/v1/predictions` | Optional | Detect and count sheep in one image |
| `POST` | `/v1/predictions/video` | Optional | Analyse an uploaded video |
| `GET` | `/v1/streams` | No | List configured and runtime streams |
| `POST` | `/v1/streams` | Yes | Attach an RTSP or RTSPS stream |
| `DELETE` | `/v1/streams/{stream_id}` | Yes | Remove a runtime RTSP stream |
| `GET` | `/v1/streams/{stream_id}/mjpeg` | No | Read annotated MJPEG frames |
| `GET` | `/v1/dashboard` | No | Current aggregate stream snapshot |
| `WS` | `/v1/dashboard/ws` | No | Snapshot updates approximately once per second |
| `GET` | `/v1/reports/sessions` | Yes | Current user's recent inference sessions |
| `GET` | `/v1/reports/export.csv` | Yes | Export the user's journal as CSV |
| `GET` | `/v1/reports/export.pdf` | Yes | Export the user's journal as PDF |

Authenticated image and video requests are journalled. Anonymous inference is
accepted but does not create a user history record.

## Authentication

Register with an email address and a password between 8 and 128 characters:

```bash
curl --request POST http://localhost:8000/v1/auth/register \
  --header 'Content-Type: application/json' \
  --data '{"email":"operator@example.test","password":"replace-this-password"}'
```

Registration, login, and refresh return an access/refresh token pair:

```json
{
  "access_token": "<access-token>",
  "refresh_token": "<refresh-token>",
  "token_type": "bearer"
}
```

Do not place tokens in source files, shell history, screenshots, or issue text.
Production clients should store them using platform-appropriate secure storage.

## Image inference

Supported declared media types are JPEG, PNG, BMP, and WebP. The server verifies
that the content can be decoded and rejects images above the configured pixel
limit.

```bash
curl --request POST http://localhost:8000/v1/predictions \
  --header 'X-Request-ID: demo-image-001' \
  --form 'file=@sample.jpg;type=image/jpeg'
```

The response contains the model version and threshold, image dimensions,
confident and uncertain counts, processing time, detections, and an annotated
JPEG as a base64 data URL. A detection is counted when its confidence is at or
above the operating threshold. Detections from the inference floor up to that
threshold contribute to `uncertain_count`.

## Video inference

Supported declared media types are MP4, QuickTime, AVI, and WebM. Input and
annotated output are stored below the configured local storage root.

```bash
curl --request POST http://localhost:8000/v1/predictions/video \
  --form 'file=@short-flight.mp4;type=video/mp4'
```

The response reports processed frames, maximum and mean counts, peak timestamp,
processing time, sampled count history, keyframes, and a URL for the annotated
video. By default, at most 600 frames are processed and eight keyframes are
returned.

## Model threshold

The accepted range is `0.25` through `0.95`. Updating it affects all inference
entry points in the current application process and is not persisted as a new
model version.

```bash
curl --request PATCH http://localhost:8000/v1/model-threshold \
  --header 'Authorization: Bearer <access-token>' \
  --header 'Content-Type: application/json' \
  --data '{"confidence_threshold":0.45}'
```

Choose a durable operating threshold from validation behavior and the business
cost of misses versus duplicate detections; do not tune it on the test set.

## RTSP streams

Only `rtsp://` and `rtsps://` URLs with a hostname are accepted. Credentials in
the URL remain server-side and are never returned by the stream-list endpoint.
An omitted `id` is generated by the server. A supplied ID must be a lowercase,
hyphenated identifier between 3 and 64 characters.

```json
{
  "name": "North pasture drone",
  "location": "North pasture",
  "uri": "rtsps://camera-host.example.test/live"
}
```

Runtime RTSP connections can be deleted. File streams declared in
[`configs/app.toml`](../configs/app.toml) are protected from runtime deletion.

## Limits and media validation

The defaults below are defined in [`src/agrovision/config.py`](../src/agrovision/config.py)
and can be overridden by environment variables.

| Limit | Default |
|---|---:|
| Maximum upload | 100 MiB |
| Maximum decoded image area | 50,000,000 pixels |
| Maximum processed video frames | 600 |
| Detector queue capacity | 8 |
| Queue wait | 5 seconds |
| Inference timeout | 600 seconds |

An extension is never trusted on its own. The declared media type is checked and
image content must decode successfully. Deployments should also enforce body and
request timeouts at the reverse proxy.

## Errors

Expected errors use one stable envelope:

```json
{
  "error": {
    "code": "unsupported_media_type",
    "message": "Could not decode the uploaded image"
  },
  "request_id": "demo-image-001"
}
```

| HTTP status | Error code | Meaning |
|---:|---|---|
| 400 | `validation_error` | A syntactically valid operation was rejected |
| 401 | `unauthorized` | Credentials are missing or invalid |
| 403 | `forbidden` | The current identity lacks permission |
| 404 | `not_found` | The requested resource does not exist |
| 409 | `conflict` | The operation conflicts with current state |
| 413 | `payload_too_large` | The configured upload limit was exceeded |
| 415 | `unsupported_media_type` | Media type or content cannot be handled |
| 422 | `invalid_request` | Request shape or field validation failed |
| 503 | `inference_busy` | The bounded inference queue is full |
| 504 | `inference_timeout` | Inference exceeded its configured deadline |
| 500 | `internal_error` | An unexpected server error occurred |

Generic framework-generated HTTP errors use `http_error`. Report failures with
the request ID, endpoint, time, and application version, but never attach tokens,
raw private imagery, or RTSP credentials.

## Compatibility

Additive fields may appear in `/v1` responses. Removing fields, changing their
meaning, or altering endpoint behavior requires a new API version or an explicit
migration period. The Pydantic schemas in
[`src/agrovision/presentation/schemas.py`](../src/agrovision/presentation/schemas.py)
are the executable source of truth.
