import os
import io
import time
import logging
from typing import Optional
from fastapi import FastAPI, File, UploadFile, HTTPException, Query, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import numpy as np
from PIL import Image
import tensorflow as tf
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from dotenv import load_dotenv
import httpx

# Load environment variables
load_dotenv()

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agrivision-backend")

# Initialize SlowAPI Rate Limiter
limiter = Limiter(key_func=get_remote_address)
app = FastAPI(title="AgriVision AI API", version="1.0")
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# Enable CORS for mobile and web connections
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Load Disease database
from disease_data import DISEASE_DATA

# Model setup
MODEL_PATH = r"d:\Crop_app\mobilenet_crop_disease.keras"
model = None

# Class names mapping (ordered alphabetically)
DISEASE_CLASSES = [
    "Corn___Common_Rust",
    "Corn___Gray_Leaf_Spot",
    "Corn___Healthy",
    "Corn___Northern_Leaf_Blight",
    "Potato___Early_Blight",
    "Potato___Healthy",
    "Potato___Late_Blight",
    "Rice___Brown_Spot",
    "Rice___Healthy",
    "Rice___Leaf_Blast",
    "Rice___Neck_Blast",
    "Sugarcane___Bacterial_Blight",
    "Sugarcane___Healthy",
    "Sugarcane___Red_Rot",
    "Wheat___Brown_Rust",
    "Wheat___Healthy",
    "Wheat___Yellow_Rust"
]

@app.on_event("startup")
def load_ml_model():
    global model
    try:
        logger.info(f"Loading Keras model from {MODEL_PATH}...")
        model = tf.keras.models.load_model(MODEL_PATH)
        logger.info("Keras model loaded successfully!")
    except Exception as e:
        logger.error(f"Failed to load Keras model: {e}")
        # Note: We do not fail startup, so developers can test other API endpoints
        # even if Keras model fails to compile on some configurations

# Rate Limiting configuration:
# 20 requests/minute for prediction API, 100/minute for other routes
PREDICT_LIMIT = "20/minute"
GENERAL_LIMIT = "100/minute"

# Helper function for Image Preprocessing
def preprocess_image(image_bytes: bytes) -> np.ndarray:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    img = img.resize((224, 224))
    img_array = np.array(img, dtype=np.float32)
    # MobileNetV2 expected scaling: [-1, 1]
    img_array = (img_array / 127.5) - 1.0
    img_array = np.expand_dims(img_array, axis=0)
    return img_array

# Define Pydantic Models for requests
class TranslationRequest(BaseModel):
    text: str
    target_language: str  # e.g., "Hindi", "Marathi", "English"

class TTSRequest(BaseModel):
    text: str
    language_code: Optional[str] = "en"  # e.g., "en", "hi", "mr"

class ChatRequest(BaseModel):
    message: str
    language: Optional[str] = "English"

@app.get("/")
@limiter.limit(GENERAL_LIMIT)
def read_root(request: Request):
    return {
        "status": "online",
        "app": "AgriVision AI API",
        "supported_crops": ["Corn", "Potato", "Rice", "Wheat", "Sugarcane"],
        "total_disease_classes": len(DISEASE_CLASSES)
    }

@app.post("/api/v1/predict")
@limiter.limit(PREDICT_LIMIT)
async def predict_disease(request: Request, file: UploadFile = File(...)):
    global model
    # File validation
    filename = file.filename.lower()
    if not (filename.endswith(".jpg") or filename.endswith(".jpeg") or filename.endswith(".png")):
        raise HTTPException(status_code=400, detail="Allowed image formats are JPG, JPEG, and PNG")
    
    # Read file content
    contents = await file.read()
    if len(contents) > 5 * 1024 * 1024:
        raise HTTPException(status_code=400, detail="Maximum allowed image size is 5 MB")

    if model is None:
        # Fallback simulation if Keras model could not be initialized
        logger.warning("ML Model not loaded. Running fallback simulation.")
        # Make a mock prediction based on filename keywords or random
        mock_idx = 8  # Rice___Healthy default
        for i, class_name in enumerate(DISEASE_CLASSES):
            if class_name.lower().split("___")[0] in filename or (len(class_name.lower().split("___")) > 1 and class_name.lower().split("___")[1] in filename):
                mock_idx = i
                break
        return {
            "disease": DISEASE_CLASSES[mock_idx],
            "confidence": 92.5,
            "simulated": True
        }

    try:
        # Preprocess and Predict
        input_tensor = preprocess_image(contents)
        # Use direct callable for significantly faster single-image inference
        predictions = model(input_tensor, training=False).numpy()
        predicted_idx = int(np.argmax(predictions[0]))
        confidence = float(predictions[0][predicted_idx]) * 100.0

        return {
            "disease": DISEASE_CLASSES[predicted_idx],
            "confidence": round(confidence, 2),
            "simulated": False
        }
    except Exception as e:
        logger.error(f"Prediction error: {e}")
        raise HTTPException(status_code=500, detail=f"Image processing failed: {str(e)}")

@app.get("/api/v1/disease/{name}")
@limiter.limit(GENERAL_LIMIT)
def get_disease_details(
    request: Request,
    name: str,
    lang: str = Query("English", description="Target language: English, Hindi, Marathi")
):
    if name not in DISEASE_DATA:
        raise HTTPException(status_code=404, detail="Disease class not found in database")
    
    lang_mapped = lang.capitalize()
    if lang_mapped not in ["English", "Hindi", "Marathi"]:
        lang_mapped = "English"

    details = DISEASE_DATA[name].get(lang_mapped, DISEASE_DATA[name]["English"])
    return details

@app.post("/api/v1/translate")
@limiter.limit(GENERAL_LIMIT)
def translate_text(request: Request, payload: TranslationRequest):
    text = payload.text
    target = payload.target_language.capitalize()

    # Simple local dictionary translations for core crop queries
    # Fallback to translation engine logic if credentials existed
    # Supported: "English", "Hindi", "Marathi"
    translation_db = {
        "What fertilizer should I use for rice blast?": {
            "Hindi": "राइस ब्लास्ट के लिए मुझे कौन सा उर्वरक उपयोग करना चाहिए?",
            "Marathi": "भात करपा रोगासाठी मी कोणते खत वापरावे?"
        },
        "How to cure early blight in potato?": {
            "Hindi": "आलू में अगेती झुलसा रोग का इलाज कैसे करें?",
            "Marathi": "बटाट्यावरील लवकर येणाऱ्या करपा रोगाचे नियंत्रण कसे करावे?"
        },
        "My corn leaves have brown spots": {
            "Hindi": "मेरे मक्के के पत्तों पर भूरे रंग के धब्बे हैं।",
            "Marathi": "माझ्या मक्याच्या पानांवर तपकिरी ठिपके आहेत."
        }
    }

    if text in translation_db and target in translation_db[text]:
        translated = translation_db[text][target]
    else:
        # Mock machine translation logic
        translated = f"[{target} Translation] {text}"

    return {
        "original_text": text,
        "target_language": target,
        "translated_text": translated
    }

@app.post("/api/v1/chat")
@limiter.limit(GENERAL_LIMIT)
async def chat_assistant(request: Request, payload: ChatRequest):
    gemini_key = os.getenv("GEMINI_API_KEY")
    user_message = payload.message
    lang = payload.language or "English"

    if not gemini_key:
        logger.warning("GEMINI_API_KEY not configured. Running fallback NLP mock.")
        # Fallback NLP mock to keep the app functional
        reply_text = "I understand you have a question. To give you the best advice, please take a photo of the crop leaf using the Scan feature."
        query_lower = user_message.lower()
        if 'blast' in query_lower or 'धान' in query_lower or 'धान के पत्ते' in query_lower:
            reply_text = "For Rice Blast (Magnaporthe oryzae), proper fertilization management is crucial. Avoid excessive Nitrogen (Urea) as it promotes fungal growth. I recommend applying Potash to strengthen plant walls."
        elif 'blight' in query_lower or 'झुलसा' in query_lower:
            reply_text = "Early Blight of Potato is caused by Alternaria solani. Key treatments include spraying protectant fungicides like Mancozeb or Chlorothalonil at 10-day intervals."
        elif 'rust' in query_lower or 'गेरूआ' in query_lower:
            reply_text = "Rust is a fungal disease causing powdery rust-colored pustules. Spray copper-based fungicides if disease appears early in the season."
        return {"reply": reply_text, "source": "mock"}

    try:
        system_instruction = (
            f"You are AgriVision AI, an expert agricultural chatbot assistant helping a farmer. "
            f"Provide professional, accurate, and direct agricultural answers, disease diagnosis advice, "
            f"fertilizer application recommendations, and treatment details. "
            f"You MUST write your entire response in the following language: {lang}."
        )

        gemini_url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={gemini_key}"
        headers = {"Content-Type": "application/json"}
        data = {
            "contents": [
                {
                    "parts": [
                        {
                            "text": user_message
                        }
                    ]
                }
            ],
            "systemInstruction": {
                "parts": [
                    {
                        "text": system_instruction
                    }
                ]
            }
        }

        async with httpx.AsyncClient() as client:
            response = await client.post(gemini_url, json=data, headers=headers, timeout=30.0)
            if response.status_code != 200:
                logger.error(f"Gemini API returned non-200 status: {response.status_code} - {response.text}")
                raise HTTPException(status_code=response.status_code, detail="Failed to communicate with Gemini AI")
            
            res_json = response.json()
            reply_text = res_json['candidates'][0]['content']['parts'][0]['text']
            return {"reply": reply_text, "source": "gemini"}
    except Exception as e:
        logger.error(f"Error in chat_assistant: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/text-to-speech")
@limiter.limit(GENERAL_LIMIT)
def text_to_speech(request: Request, payload: TTSRequest):
    try:
        from gtts import gTTS
        
        lang_code = payload.language_code
        try:
            # Generate Audio using Google Text-to-Speech API for the requested language code
            tts = gTTS(text=payload.text, lang=lang_code)
        except Exception:
            # Fallback to English if gTTS fails to parse the language code
            tts = gTTS(text=payload.text, lang="en")
        
        # Save audio to a bytes stream
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return StreamingResponse(fp, media_type="audio/mpeg", headers={
            "Content-Disposition": "inline; filename=response.mp3"
        })
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")

@app.get("/api/v1/text-to-speech")
@limiter.limit(GENERAL_LIMIT)
def text_to_speech_get(
    request: Request,
    text: str = Query(..., description="Text to convert to speech"),
    language_code: str = Query("en", description="Language code (e.g. en, hi, mr, es, fr)")
):
    try:
        from gtts import gTTS
        
        lang_code = language_code
        try:
            # Generate Audio using Google Text-to-Speech API for the requested language code
            tts = gTTS(text=text, lang=lang_code)
        except Exception:
            # Fallback to English if gTTS fails to parse the language code
            tts = gTTS(text=text, lang="en")
        
        # Save audio to a bytes stream
        fp = io.BytesIO()
        tts.write_to_fp(fp)
        fp.seek(0)
        
        return StreamingResponse(fp, media_type="audio/mpeg", headers={
            "Content-Disposition": "inline; filename=response.mp3"
        })
    except Exception as e:
        logger.error(f"TTS generation failed: {e}")
        raise HTTPException(status_code=500, detail=f"Text-to-speech failed: {str(e)}")

@app.post("/api/v1/speech-to-text")
@limiter.limit(GENERAL_LIMIT)
async def speech_to_text(request: Request, file: UploadFile = File(...)):
    # Simple transcript simulation mapping standard voice recordings to text queries
    # Real pipeline uses Whisper if needed. Let's make it fully responsive for test voice files
    filename = file.filename.lower()
    
    # Read audio file bytes
    audio_data = await file.read()
    logger.info(f"Received audio recording for transcription: {file.filename} ({len(audio_data)} bytes)")
    
    # Mock transcriber based on duration / audio length or mock test names
    # Returns known queries for demo flows
    mock_transcripts = [
        "What fertilizer should I use for rice blast?",
        " मेरे धान के पत्तों पर भूरे धब्बे हैं",
        "How to cure early blight in potato?"
    ]
    
    import random
    transcribed_text = random.choice(mock_transcripts)
    
    return {
        "status": "success",
        "transcribed_text": transcribed_text
    }
