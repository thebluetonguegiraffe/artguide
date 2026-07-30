FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

# curl + unzip are required by `reflex init` to fetch its bundled bun runtime
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    unzip \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /dashboard_reflex

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

COPY dashboard_reflex/requirements.txt ./dashboard_reflex/requirements.txt
RUN uv pip install -r dashboard_reflex/requirements.txt

COPY src ./src
COPY config.py .
COPY .env .
COPY dashboard_reflex/rxconfig.py ./dashboard_reflex/rxconfig.py
COPY dashboard_reflex/reflex.lock ./dashboard_reflex/reflex.lock
COPY dashboard_reflex/assets ./dashboard_reflex/assets
COPY dashboard_reflex/artguide_app ./dashboard_reflex/artguide_app

ENV PYTHONPATH=/dashboard_reflex

WORKDIR /dashboard_reflex/dashboard_reflex

# api_url/deploy_url are compiled into the frontend bundle, so the image must
# be rebuilt (not just restarted) if the public URL changes.
ARG DASHBOARD_PUBLIC_URL=http://localhost:8502
ENV DASHBOARD_PUBLIC_URL=${DASHBOARD_PUBLIC_URL}
ENV REFLEX_PORT=8502

RUN uv run reflex init

EXPOSE 8502

CMD ["uv", "run", "reflex", "run", "--env", "prod", "--single-port"]
