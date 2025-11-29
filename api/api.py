import os
import time
from typing import Literal
from dotenv import load_dotenv
from fastapi import Depends, FastAPI, HTTPException, Security
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from pydantic import BaseModel

from src.services.piper_speaker import PIPER_VOICE_MAPPER, PiperSpeaker
from src.services.qdrant_db import QdrantDB


load_dotenv()

security = HTTPBearer(
    scheme_name="Bearer Token",
    description="Ingresa tu token de API"
)

API_TOKEN = os.getenv("API_TOKEN")

if not API_TOKEN:
    raise ValueError("API_TOKEN must be set in environment variables")

app = FastAPI(
    title="ArtGuide API",
    description="API para búsqueda de imágenes y síntesis de voz",
    version="1.0.0"
)

db = QdrantDB()

# create class instances to load all models into memory
speaker_models = {
    key: PiperSpeaker(*PIPER_VOICE_MAPPER[key])
    for key in PIPER_VOICE_MAPPER
}


def verify_token(credentials: HTTPAuthorizationCredentials = Security(security)) -> str:
    if credentials.credentials != API_TOKEN:
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    return credentials.credentials


@app.get("/status")
def status():
    return {"status": "healthy"}


class ImageSearchRequest(BaseModel):
    image_data: str  # Base64 encoded image


@app.post("/search")
def search(request: ImageSearchRequest, token: str = Depends(verify_token)):
    results = db.search(request.image_data)
    return results


class SynthesizeRequest(BaseModel):
    text: str
    speaker: Literal['male', 'female']
    language: Literal['en', 'es', 'ca']


@app.post("/synthesize")
def synthesize(request: SynthesizeRequest, token: str = Depends(verify_token)):
    start_time = time.time()

    audio_array, sample_rate = speaker_models[(request.language, request.speaker)].synthesize(
        request.text
    )

    elapsed = time.time() - start_time

    return {
        "samples": audio_array.tolist(),
        "sr": sample_rate,
        "elapsed_seconds": elapsed,
        "language": request.language,
        "speaker": request.speaker,
    }
