import io
from typing import Tuple, Optional
from PIL import Image

# -------------------------
# Helper functions
# -------------------------
def _to_bits(data: bytes) -> str:
    return ''.join(f'{b:08b}' for b in data)

def _from_bits(bitstr: str) -> bytes:
    chopped = bitstr[:len(bitstr) - (len(bitstr) % 8)]
    return bytes(int(chopped[i:i+8], 2) for i in range(0, len(chopped), 8))

def _capacity_bits(image: Image.Image) -> int:
    w, h = image.size
    return w * h * 3  # 3 bits per pixel (RGB)

def _set_lsb_bits(image: Image.Image, bits: str) -> Image.Image:
    img = image.convert("RGB").copy()
    pixels = img.load()
    idx = 0
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if idx >= len(bits):
                break
            r, g, b = pixels[x, y]
            r = (r & ~1) | int(bits[idx]) if idx < len(bits) else r; idx += 1
            g = (g & ~1) | int(bits[idx]) if idx < len(bits) else g; idx += 1
            b = (b & ~1) | int(bits[idx]) if idx < len(bits) else b; idx += 1
            pixels[x, y] = (r, g, b)
        if idx >= len(bits):
            break
    if idx < len(bits):
        raise ValueError("Image too small for this message")
    return img

def _read_lsb_bits(image: Image.Image, nbits: int) -> str:
    img = image.convert("RGB")
    pixels = img.load()
    bits = []
    read = 0
    w, h = img.size
    for y in range(h):
        for x in range(w):
            if read >= nbits:
                break
            r, g, b = pixels[x, y]
            if read < nbits: bits.append(str(r & 1)); read += 1
            if read < nbits: bits.append(str(g & 1)); read += 1
            if read < nbits: bits.append(str(b & 1)); read += 1
        if read >= nbits:
            break
    return ''.join(bits)

# -------------------------
# Main functions
# -------------------------
def encode_message(image_bytes: bytes, message: str) -> bytes:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    msg_bytes = message.encode("utf-8")
    header = len(msg_bytes).to_bytes(4, 'big')  # 4 bytes header for length
    payload = header + msg_bytes
    bits = _to_bits(payload)
    if len(bits) > _capacity_bits(img):
        raise ValueError("Message too large for this image.")
    out_img = _set_lsb_bits(img, bits)
    buf = io.BytesIO()
    out_img.save(buf, format="PNG")
    return buf.getvalue()

def decode_message(image_bytes: bytes) -> str:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    header_bits = _read_lsb_bits(img, 32)  # first 32 bits = length
    if len(header_bits) < 32:
        return "[No hidden message]"
    length = int(header_bits, 2)
    max_capacity_bytes = _capacity_bits(img) // 8
    if length == 0 or length > max_capacity_bytes:
        return "[No hidden message]"
    total_bits = 32 + length * 8
    all_bits = _read_lsb_bits(img, total_bits)
    payload_bits = all_bits[32:]
    msg_bytes = _from_bits(payload_bits)
    try:
        return msg_bytes[:length].decode("utf-8", errors="replace")
    except Exception:
        return "[Corrupted message]"

def detect_stego(image_bytes: bytes) -> Tuple[str, Optional[float], str]:
    img = Image.open(io.BytesIO(image_bytes)).convert("RGB")
    pixels = img.load()
    ones = 0
    total = 0
    w, h = img.size
    for y in range(h):
        for x in range(w):
            r, g, b = pixels[x, y]
            ones += (r & 1) + (g & 1) + (b & 1)
            total += 3
    ratio = ones / max(1, total)
    if 0.47 <= ratio <= 0.53:
        return ("Possibly Stego", 0.5, "heuristic")
    else:
        return ("Likely Clean", 1.0 - abs(0.5 - ratio), "heuristic")

# -------------------------
# Wrappers for main.py
# -------------------------
def encode_message_image(image_bytes: bytes, message: str) -> bytes:
    return encode_message(image_bytes, message)

def decode_message_image(image_bytes: bytes) -> str:
    return decode_message(image_bytes)


