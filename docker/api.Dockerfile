FROM ghcr.io/astral-sh/uv:0.8.15 AS uv

FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_COMPILE_BYTECODE=1 \
    UV_LINK_MODE=copy \
    PATH="/app/.venv/bin:$PATH" \
    PYTHONPATH="/app/src:/app"

RUN apt-get update \
    && apt-get install --no-install-recommends -y libgl1 libglib2.0-0 libgomp1 libxcb1 \
    && rm -rf /var/lib/apt/lists/* \
    && groupadd --gid 10001 agrovision \
    && useradd --uid 10001 --gid agrovision --create-home agrovision

COPY --from=uv /uv /uvx /bin/
WORKDIR /app

COPY pyproject.toml uv.lock ./
RUN uv sync --frozen --no-dev --no-install-project

COPY alembic.ini ./
COPY alembic ./alembic
COPY apps ./apps
COPY configs ./configs
COPY scripts ./scripts
COPY src ./src

RUN mkdir -p /app/artifacts/uploads /app/data/demo \
    && chown -R agrovision:agrovision /app

USER agrovision
EXPOSE 8000

CMD ["/bin/sh", "-c", "alembic upgrade head && exec uvicorn apps.api.main:app --host 0.0.0.0 --port 8000"]
