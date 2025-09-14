# audio_stego_utils.py
import io
import wave
import numpy as np

def encode_message_audio(audio_bytes, message):
    """Encode a text message into a WAV audio file (LSB method)."""
    # Convert message to bits
    message_bits = ''.join(f"{ord(c):08b}" for c in message)
    
    try:
        with io.BytesIO(audio_bytes) as audio_file:
            with wave.open(audio_file, 'rb') as wav:
                params = wav.getparams()
                frames = np.frombuffer(wav.readframes(params.nframes), dtype=np.int16)
    except wave.Error:
        raise ValueError("Invalid WAV file. Make sure your audio is uncompressed PCM WAV.")

    if len(message_bits) > len(frames):
        raise ValueError("Message too long for this audio file.")

    # Encode message bits into LSB of audio frames
    encoded_frames = frames.copy()
    for i, bit in enumerate(message_bits):
        encoded_frames[i] = (encoded_frames[i] & ~1) | int(bit)

    # Save encoded audio to bytes
    output = io.BytesIO()
    with wave.open(output, 'wb') as wav_out:
        wav_out.setparams(params)
        wav_out.writeframes(encoded_frames.tobytes())
    return output.getvalue()

def decode_message_audio(audio_bytes, msg_length):
    """Decode a hidden text message from a WAV audio file."""
    try:
        with io.BytesIO(audio_bytes) as audio_file:
            with wave.open(audio_file, 'rb') as wav:
                frames = np.frombuffer(wav.readframes(wav.getnframes()), dtype=np.int16)
    except wave.Error:
        raise ValueError("Invalid WAV file. Make sure your audio is uncompressed PCM WAV.")

    if len(frames) < msg_length * 8:
        raise ValueError("Audio file too short for the given message length.")

    # Read the LSB of the first msg_length * 8 samples
    bits = [str(frames[i] & 1) for i in range(msg_length * 8)]
    
    # Convert bits to characters
    chars = [chr(int(''.join(bits[i:i+8]), 2)) for i in range(0, len(bits), 8)]
    return ''.join(chars)
