from fastapi import FastAPI, UploadFile, HTTPException
from faster_whisper import WhisperModel
import logging

app = FastAPI()
model = None
logger = logging.getLogger("uvicorn")

@app.on_event("startup")
async def startup_event():
    global model
    try:
        model = WhisperModel("tiny", device="cpu")
        logger.info("Modelo Whisper carregado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {str(e)}")
        raise

@app.post("/transcribe")
async def transcribe(audio: UploadFile):
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(400, "Envie um arquivo de áudio válido")

    try:
        audio_bytes = await audio.read()
        segments, _ = model.transcribe(audio_bytes)
        return {"text": " ".join(segment.text for segment in segments)}
    except Exception as e:
        logger.error(f"Erro na transcrição: {str(e)}")
        raise HTTPException(500, "Falha na transcrição")

@app.get("/health")
async def health():
    return {"status": "online", "model_ready": model is not None}
