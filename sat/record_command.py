import pyaudio
import wave
import webrtcvad

FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000
CHUNK = 480

def is_speech(frame, sample_rate, vad):
    return vad.is_speech(frame, sample_rate)

def record_audio(vad, stream, CHUNK, RATE):
    frames = []
    recording = False
    silence_frames = 0
    MAX_SILENCE_FRAMES = 50

    print("[*] Listening command")

    while True:
        try:
            frame = stream.read(CHUNK, exception_on_overflow=False)
        except Exception as e:
            print(f"[!] Stream read error: {e}")
            break

        if is_speech(frame, RATE, vad):
            if not recording:
                print("[*] Recording started")
                recording = True
            frames.append(frame)
            silence_frames = 0
        else:
            if recording:
                frames.append(frame)
                silence_frames += 1

                if silence_frames > MAX_SILENCE_FRAMES:
                    print("[*] Silence in microphone, saving")
                    break

    return frames

def save_audio(frames, audio_instance, filename="command.wav"):
    wf = wave.open(filename, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio_instance.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

def main():
    # Inicjalizacja PyAudio
    audio = pyaudio.PyAudio()

    # Inicjalizacja VAD
    vad = webrtcvad.Vad()
    vad.set_mode(1) # 1 = mało agresywny, 3 = bardzo agresywny

    try:
        # Otwarcie strumienia
        stream = audio.open(format=FORMAT,
                            channels=CHANNELS,
                            rate=RATE,
                            input=True,
                            frames_per_buffer=CHUNK)

        frames = record_audio(vad, stream, CHUNK, RATE)

        if frames:
            save_audio(frames, audio)
            print("[*] Audio saved as command.wav")

        # Zamykamy tylko strumień, ale NIE robimy terminate() tutaj,
        # jeśli planujemy używać 'audio' ponownie w pętli.
        stream.stop_stream()
        stream.close()

    finally:
        # To wywołujemy TYLKO przy całkowitym zamknięciu programu
        audio.terminate()
        return True

if __name__ == "__main__":
    main()
