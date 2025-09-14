from fastapi import FastAPI, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse, JSONResponse, FileResponse
import io
import os
from stego_utils import encode_message_image, decode_message_image, detect_stego
app = FastAPI(title="Steganography Forensics API")

# Enable CORS for local frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/encode")
async def encode_image(file: UploadFile = File(...), message: str = Form(...)):
    input_path = f"temp_{file.filename}"
    output_path = f"encoded_{file.filename}"

    # Save uploaded file
    with open(input_path, "wb") as f:
        f.write(await file.read())

    # Call your encoding function
    encode(input_path, message, output_path)

    # Remove temporary original file
    os.remove(input_path)

    # Return the encoded image for download
    return FileResponse(output_path, media_type='image/png', filename=output_path)

@app.post("/decode")
async def decode(file: UploadFile):
    try:
        image_bytes = await file.read()
        message = decode_message_image(image_bytes)
        return {"message": message}
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})

@app.post("/detect")
async def detect(file: UploadFile):
    try:
        image_bytes = await file.read()
        label, prob, mode = detect_stego(image_bytes)
        payload = {"result": label, "mode": mode}
        if prob is not None:
            payload["probability"] = round(float(prob), 4)
        return payload
    except Exception as e:
        return JSONResponse(status_code=400, content={"detail": str(e)})
