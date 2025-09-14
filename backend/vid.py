# backend/main.py
import cv2
import numpy as np
from fastapi import FastAPI, File, Form, UploadFile
from fastapi.responses import FileResponse, JSONResponse
import tempfile
import os

app = FastAPI()

# =====================
# Utility functions
# =====================
def message_to_binary(message: str) -> str:
    return ''.join([format(ord(char), "08b") for char in message])

def binary_to_message(binary: str) -> str:
    chars = [binary[i:i + 8] for i in range(0, len(binary), 8)]
    return ''.join([chr(int(char, 2)) for char in chars])

# =====================
# Encode for Video
# =====================
def encode_video(video_path: str, message: str, output_path: str):
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Invalid video file")

    fourcc = cv2.VideoWriter_fourcc(*"mp4v")
    fps = int(cap.get(cv2.CAP_PROP_FPS))
    width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
    height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))

    out = cv2.VideoWriter(output_path, fourcc, fps, (width, height))

    # Prepare binary message
    binary = message_to_binary(message) + "1111111111111110"  # EOF marker
    data_index = 0
    data_len = len(binary)

    total_capacity = int(cap.get(cv2.CAP_PROP_FRAME_COUNT)) * width * height * 3
    if data_len > total_capacity:
        cap.release()
        out.release()
        raise ValueError("Message too large to hide in this video.")

    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        if data_index < data_len:
            flat = frame.flatten()
            for i in range(len(flat)):
                if data_index < data_len:
                    flat[i] = (flat[i] & np.uint8(254)) | np.uint8(int(binary[data_index]))
                    data_index += 1
            frame = flat.reshape(frame.shape)

        out.write(frame)

    cap.release()
    out.release()

# =====================
# Decode for Video
# =====================
def decode_video(video_path: str) -> str:
    cap = cv2.VideoCapture(video_path)
    if not cap.isOpened():
        raise ValueError("Invalid video file")

    binary = ""
    while cap.isOpened():
        ret, frame = cap.read()
        if not ret:
            break

        flat = frame.flatten()
        for val in flat:
            binary += str(val & 1)
            if binary.endswith("1111111111111110"):  # EOF marker
                cap.release()
                return binary_to_message(binary[:-16])

    cap.release()
    return binary_to_message(binary)

# =====================
# API Routes
# =====================
@app.post("/encode")
async def encode(file: UploadFile = File(...), message: str = Form(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(await file.read())
        tmp_in_path = tmp_in.name

    tmp_out_path = tempfile.mktemp(suffix=".mp4")

    try:
        encode_video(tmp_in_path, message, tmp_out_path)
        return FileResponse(
            tmp_out_path,
            filename="encoded.mp4",
            media_type="video/mp4"
        )
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    finally:
        os.remove(tmp_in_path)

@app.post("/decode")
async def decode(file: UploadFile = File(...)):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".mp4") as tmp_in:
        tmp_in.write(await file.read())
        tmp_in_path = tmp_in.name

    try:
        message = decode_video(tmp_in_path)
        return {"decoded_message": message}
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=400)
    finally:
        os.remove(tmp_in_path)
