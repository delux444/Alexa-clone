def main(text=""):

    if text == "":
        return False

    import wave
    from piper import PiperVoice

    voice = PiperVoice.load("/home/lorak/alexa-config/scripts/host/voices/en_GB-semaine-medium.onnx", use_cuda=True)

    with wave.open("test.wav", "wb") as wav_file:
        voice.synthesize_wav(text, wav_file)
        return True


if __name__ == "__main__":
    main(text="")
