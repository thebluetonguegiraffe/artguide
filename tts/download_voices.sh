#!/bin/bash

# Create the directory where the models will be stored
mkdir -p ./tts/models

# --- Spanish Male and Female Voice ---
echo "Downloading Spanish male and female voice model..."
wget -P ./tts/models/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/es/es_ES/sharvard/medium/es_ES-sharvard-medium.onnx.json

# --- English Male and Female Voice ---
echo "Downloading English male and female voice model..."
wget -P ./tts/models/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/en/en_US/libritts/high/en_US-libritts-high.onnx.json

# --- Catalan Male Voice ---
echo "Downloading Catalan male voice model..."
wget -P ./tts/models/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ca/ca_ES/upc_pau/x_low/ca_ES-upc_pau-x_low.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ca/ca_ES/upc_pau/x_low/ca_ES-upc_pau-x_low.onnx.json

# --- Catalan Female Voice ---
echo "Downloading Catalan female voice model..."
wget -P ./tts/models/ \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ca/ca_ES/upc_ona/medium/ca_ES-upc_ona-medium.onnx \
  https://huggingface.co/rhasspy/piper-voices/resolve/main/ca/ca_ES/upc_ona/medium/ca_ES-upc_ona-medium.onnx.json

# Completion message
echo "Model downloads complete."
