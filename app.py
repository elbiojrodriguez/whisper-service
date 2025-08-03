from fastapi import FastAPI, UploadFile, HTTPException
from faster_whisper import WhisperModel
import logging
import requests
import os

app = FastAPI()
model = None
logger = logging.getLogger("uvicorn")

# Configurações do Azure (variáveis de ambiente)
AZURE_KEY = os.getenv("AZURE_KEY")  # ← Será configurada no Render
AZURE_ENDPOINT = "https://api.cognitive.microsofttranslator.com"
AZURE_REGION = "eastus"  # Altere se sua região for diferente

@app.on_event("startup")
async def startup_event():
    global model
    try:
        model = WhisperModel("tiny", device="cpu")
        logger.info("Modelo Whisper carregado com sucesso")
    except Exception as e:
        logger.error(f"Erro ao carregar modelo: {str(e)}")
        raise

@app.post("/transcribe_and_translate")
async def transcribe_and_translate(audio: UploadFile, target_lang: str = "pt"):
    # 1. Transcreve áudio para texto (Whisper)
    if not audio.content_type.startswith('audio/'):
        raise HTTPException(400, "Envie um arquivo de áudio válido")
    
    try:
        audio_bytes = await audio.read()
        segments, _ = model.transcribe(audio_bytes)
        texto_original = " ".join(segment.text for segment in segments)
        
        # 2. Traduz texto (Azure Translator)
        url = f"{AZURE_ENDPOINT}/translate?api-version=3.0&to={target_lang}"
        headers = {
            "Ocp-Apim-Subscription-Key": AZURE_KEY,
            "Ocp-Apim-Subscription-Region": AZURE_REGION,
            "Content-Type": "application/json"
        }
        body = [{"text": texto_original}]
        response = requests.post(url, headers=headers, json=body).json()
        texto_traduzido = response[0]['translations'][0]['text']
        
        return {
            "original": texto_original,
            "translation": texto_traduzido,
            "target_lang": target_lang
        }
        
    except Exception as e:
        logger.error(f"Erro: {str(e)}")
        raise HTTPException(500, "Falha no processamento")

@app.get("/health")
async def health():
    return {
        "status": "online",
        "whisper_ready": model is not None,
        "azure_ready": bool(AZURE_KEY)
    }
