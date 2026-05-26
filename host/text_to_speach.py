def main(text=""):

    if text == "":
        return False

    import wave
    from piper import PiperVoice, SynthesisConfig

    voice = PiperVoice.load(
        "/home/lorak/Templates/host/voices/pl_PL-gosia-medium.onnx",
        use_cuda=True
    )

    syn_config = SynthesisConfig(
        volume=1.0,  # half as loud
        length_scale=1.0,  # twice as slow
        #noise_scale=1.0,  # more audio variation
        #noise_w_scale=1.0,  # more speaking variation
        #normalize_audio=False, # use raw audio from voice
    )

    with wave.open("synth_response.wav", "wb") as wav_file:
        voice.synthesize_wav(text, wav_file, syn_config)
        return True
    
    return False


if __name__ == "__main__":
    text = input("text to tts(ENTER to default text): ")

    if text:
        pass
    else:
        text = """
        Litwo, Ojczyzno moja! ty jesteś jak zdrowie;
        Ile cię trzeba cenić, ten tylko się dowie,
        Kto cię stracił. Dziś piękność twą w całej ozdobie
        Widzę i opisuję, bo tęsknię po tobie.
        """

    if main(text=text):
        print("Done!")
    else:
        print("[!] error synthesyzing")
