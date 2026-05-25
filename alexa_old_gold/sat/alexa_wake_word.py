import pyaudio
import numpy as np
from openwakeword.model import Model

MODEL_PATH = "/home/lorak/alexa-config/venv/lib/python3.12/site-packages/openwakeword/resources/models/alexa_v0.1.onnx"

RATE = 16000
CHUNK = 1280
FORMAT = pyaudio.paInt16
CHANNELS = 1


def create_detector():

    model = Model(wakeword_model_paths=[MODEL_PATH])
    audio = pyaudio.PyAudio()

    stream = audio.open(
        format=FORMAT,
        channels=CHANNELS,
        rate=RATE,
        input=True,
        frames_per_buffer=CHUNK
    )

    return model, audio, stream

def listen_for_wake_word():

    model, audio, stream = create_detector()

    print("[*] Listening for 'alexa'...")

    try:
        while True:

            audio_data = stream.read(CHUNK, exception_on_overflow=False)
            audio_array = np.frombuffer(audio_data, dtype=np.int16)
            prediction = model.predict(audio_array)

            score = prediction["alexa_v0.1"]

            if score > 0.5:
                print(f"[*] Alexa here! score={score:.3f}")
                return True

    except KeyboardInterrupt:
        return False

    finally:
        stream.stop_stream()
        stream.close()
        audio.terminate()

if __name__ == "__main__":
    result = listen_for_wake_word()
    print(result)
