FROM ghcr.io/astral-sh/uv:python3.11-slim

WORKDIR /app

COPY ../pyproject.toml .
COPY ../uv.lock .   # only if exists

RUN uv sync --frozen --no-dev

COPY . ./api

EXPOSE 8000

CMD make run_api
