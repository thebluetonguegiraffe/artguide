# Project Setup Guide

## 1. Install project dependencies in a virtual environment

```bash
uv sync
```

Activate the virtual environment:
```bash
.venv/bin/activate
```

## 2. Download TTS Models
```bash
./tts/download_voices.sh
```

## 3. Start API container
```bash
make run-api
```

