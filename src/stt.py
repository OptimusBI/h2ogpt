import numpy as np
from src.utils import get_device


def get_transcriber(model="openai/whisper-base.en", use_gpu=True, gpu_id='auto'):
    if gpu_id == 'auto':
        gpu_id = 0
    device = get_device()
    if device == 'cpu' or not use_gpu:
        device_map = {"", 'cpu'}
    else:
        device_map = {"": gpu_id} if gpu_id >= 0 else {'': 'cuda'}

    from transformers import pipeline
    transcriber = pipeline("automatic-speech-recognition", model=model, device_map=device_map)
    return transcriber


def transcribe(text0, chunks, new_chunk, transcriber=None, debug=False):
    # assume sampling rate always same
    # keep chunks so don't normalize on noise periods, which would then saturate noise with non-noise
    sr, y = new_chunk
    chunks = chunks + [y] if chunks else [y]
    stream = np.concatenate(chunks)
    stream = stream.astype(np.float32)
    stream /= np.max(np.abs(stream) + 1E-7)

    text = transcriber({"sampling_rate": sr, "raw": stream})["text"]
    if debug:
        print("y.shape: %s stream.shape: %s text0=%s text=%s" % (str(y.shape), str(stream.shape), text0, text))
    return chunks, text0 + text