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

## 3. Start API container and create tunnel
```bash
make run-api
```
Inside a screen

```bash
screen - S artguide_tunnel
screen -r artguide_tunnel
source ./venv/bin/activate
make run-tunnel
>> exit screen CTRL+ A + D
```


