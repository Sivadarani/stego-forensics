 # main.py
from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io  # ✅ ensure io is imported for StreamingResponse
from stego_utils import encode_message_image, decode_message_image, detect_stego
from audio_stego_utils import encode_message_audio, decode_message_audio

app = FastAPI(title="Steganography Forensics API")

# ===== CORS =====
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== IMAGE ENDPOINTS =====
@app.post("/encode")
async def encode(file: UploadFile = File(...), message: str = Form(...)):
    try:
        image_bytes = await file.read()
        encoded_bytes = encode_message_image(image_bytes, message)
        return StreamingResponse(
            io.BytesIO(encoded_bytes),
            media_type="image/png",
            headers={"Content-Disposition": "inline; filename=encoded.png"}
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

@app.post("/decode")
async def decode(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        message = decode_message_image(image_bytes)
        return {"message": message}
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

@app.post("/detect")
async def detect(file: UploadFile = File(...)):
    try:
        image_bytes = await file.read()
        label, prob, mode = detect_stego(image_bytes)
        payload = {"result": label, "mode": mode}
        if prob is not None:
            payload["probability"] = round(float(prob), 4)
        return payload
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

# ===== AUDIO ENDPOINTS =====
@app.post("/encode_audio")
async def encode_audio(file: UploadFile = File(...), message: str = Form(...)):
    try:
        audio_bytes = await file.read()
        encoded_bytes = encode_message_audio(audio_bytes, message)  # your function
        return StreamingResponse(
            io.BytesIO(encoded_bytes),
            media_type="audio/wav",
            headers={"Content-Disposition": "inline; filename=encoded.wav"}
        )
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

@app.post("/decode_audio")
async def decode_audio(file: UploadFile = File(...), msg_length: int = Form(...)):
    try:
        audio_bytes = await file.read()
        message = decode_message_audio(audio_bytes, int(msg_length))  # convert to int
        return {"message": message}
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
