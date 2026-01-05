FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim

WORKDIR /dashboard

COPY pyproject.toml .
COPY uv.lock .

RUN uv sync

COPY dashboard ./dashboard
COPY img ./img
COPY src ./src
COPY config.py .
COPY .env .

ENV PYTHONPATH=/dashboard

EXPOSE 8502

CMD ["uv", "run", "streamlit", "run", "dashboard/main.py", "--server.address=0.0.0.0", "--server.port=8502"]