import logging
import subprocess

import numpy as np
import soundfile as sf

from config import tts_config

logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(levelname)s - %(name)s - %(message)s"
)
logger = logging.getLogger(__name__)

PIPER_VOICE_MAPPER = {
    ("en", "male"): ("en_US-libritts-high", "2"),
    ("en", "female"): ("en_US-libritts-high", "0"),
    ("es", "male"): ("es_ES-sharvard-medium", "0"),
    ("es", "female"): ("es_ES-sharvard-medium", "1"),
    ("ca", "male"): ("ca_ES-upc_pau-x_low", ""),
    ("ca", "female"): ("ca_ES-upc_ona-medium", ""),
}


class PiperSpeaker:
    def __init__(self, model: str, speaker: str):
        self.model = model
        self.speaker = speaker
        self.model_path = f"{tts_config['path']}/{model}.onnx"
        self.config_path = self.model_path.replace(".onnx", ".onnx.json")

    def synthesize(self, text: str) -> str:
        """Generate speech audio from text using the Piper model."""

        logger.info(f"Synthesizing audio: '{text[:50]}...'")

        cmd = ["piper", "--model", self.model_path, "--config", self.config_path, "--output-raw"]

        if self.speaker:
            cmd.extend(["--speaker", self.speaker])

        result = subprocess.run(cmd, input=text.encode("utf-8"), capture_output=True, check=True)

        audio_array = np.frombuffer(result.stdout, dtype=np.int16).astype(np.float32) / 32768.0
        sample_rate = 22050
        if self.model == PIPER_VOICE_MAPPER[("ca", "male")][0]:
            sample_rate = 16000

        logger.info(f"  Samples: {len(audio_array)}")
        logger.info(f"  Duration: {len(audio_array) / sample_rate:.2f}s")

        return audio_array, sample_rate


if __name__ == "__main__":
    model, speaker = PIPER_VOICE_MAPPER[("ca", "male")]
    tts = PiperSpeaker(model=model, speaker=speaker)
    audio_array, sample_rate = tts.synthesize("Hola!")
    sf.write("test.wav", audio_array, sample_rate)
