from fastapi import FastAPI, UploadFile, HTTPException
from faster_whisper import WhisperModel
import os

app = FastAPI()
model = None

@app.on_event("startup")
async def load_model():
    global model
    model = WhisperModel("tiny", device="cpu")

@app.post("/transcribe")
async def transcribe(audio: UploadFile):
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(400, "Formato de arquivo inválido")
    
    try:
        segments, _ = model.transcribe(await audio.read())
        return {"text": " ".join(segment.text for segment in segments)}
    except Exception as e:
        raise HTTPException(500, f"Erro na transcrição: {str(e)}")

@app.get("/health")
async def health_check():
    return {"status": "ok", "model_loaded": model is not None}
