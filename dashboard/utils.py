import base64
import io
from scipy.io import wavfile


def play_audio_streamlit(samples, sr, placeholder):
    """Play audio in Streamlit"""
    byte_io = io.BytesIO()
    wavfile.write(byte_io, sr, samples)

    placeholder.audio(byte_io, format="audio/wav")


def get_base64_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode()
