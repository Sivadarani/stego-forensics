from fastapi import FastAPI, UploadFile, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse
import io

from stego_utils import encode_message, decode_message, detect_stego

app = FastAPI(title="Steganography Forensics API")

# For local demo; tighten in production
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/encode")
async def encode(file: UploadFile, message: str = Form(...)):
    """
    Encode the message into the uploaded image and return the encoded PNG as a downloadable file.
    """
    try:
        image_bytes = await file.read()
        encoded_bytes = encode_message(image_bytes, message)
        stream = io.BytesIO(encoded_bytes)
        # Return as attachment so frontend can download
        return StreamingResponse(stream, media_type="image/png", headers={
            "Content-Disposition": "attachment; filename=encoded.png"
        })
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})

@app.post("/decode")
async def decode(file: UploadFile):
    """
    Decode and return message as JSON.
    """
    try:
        image_bytes = await file.read()
        message = decode_message(image_bytes)
        return {"status": "success", "message": message}
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})

@app.post("/detect")
async def detect(file: UploadFile):
    """
    Detect stego using AI model or heuristic.
    """
    try:
        image_bytes = await file.read()
        label, prob, mode = detect_stego(image_bytes)
        payload = {"status": "success", "result": label, "mode": mode}
        if prob is not None:
            payload["probability"] = round(float(prob), 4)
        return payload
    except Exception as e:
        return JSONResponse(status_code=400, content={"status": "error", "detail": str(e)})
