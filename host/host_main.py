import paho.mqtt.client as mqtt

import time
import json
import threading

import os # chwilowo

import ask_ai
import text_to_speach
import send_response

from read_config import get_from_config as config

ask_ai_active = threading.Event()
ask_ai_active.clear()

text_to_speach_active = threading.Event()
text_to_speach_active.clear()

ai_input = ""
synthesize = ""

# =========================
# ASK QUESTION
# =========================
def ask_ai_loop():
    global ai_input
    print("[*] Ask AI thread started")
    while True:

        ask_ai_active.wait()

        if ai_input and ask_ai_active.is_set():
            print(f"[*] Sending input to AI: {ai_input}")
            response = ask_ai.ask_ai(ai_input, config(parameter="DEF_MODEL"))

            if response:
                global synthesize
                print("[*] Input answered successfully")
                print(f"[*] Answer: {response}")
                synthesize = response

        ask_ai_active.clear()
        text_to_speach_active.set()

def text_to_speach_loop(client):
    global synthesize
    print("[*] TTS thread started")
    while True:

        text_to_speach_active.wait()

        if text_to_speach_active.is_set():
            print("[*] Synthesizing text to speach")

            sucess = text_to_speach.main(synthesize)

            if sucess:
                print("[*] Synthesizing done correctly")
            else:
                print("[!] Synthesizing went wrong")

        print(f"[*] Sending response as {config(parameter="SAT_PATH")}/{config(parameter="RESP_FILE")}")
        send_response.main()

        payload = {
            "siteId": "default",
            "responseStatus": "ready"
        }

        client.publish("hermes/response/ready", json.dumps(payload))
        #os.system("vlc synth_response.wav")
        print("[*] Done")

        text_to_speach_active.clear()

# =========================
# MQTT
# =========================
def on_connect(client, userdata, flags, reason_code, properties):
    print("[*] HOST connected to MQTT Broker")

    topics = [
        "hermes/nlu/intentNotRecognized"
    ]

    for topic in topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"[*] Topic: {msg.topic}")

    # State logic
    if msg.topic == "hermes/nlu/intentNotRecognized":
        global ai_input
        ai_input = "" # probably not necessary

        raw_input = msg.payload
        raw_input = raw_input.decode('utf-8')
        raw_input = json.loads(raw_input)
        input = raw_input["input"]
        ai_input = input

        ask_ai_active.set()

    else:
        print("[!] Not recognized")

# =========================
# MAIN
# =========================
def main():

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    try:
        mqttc.connect(config(parameter="MQTT_IP"), int(config(parameter="MQTT_PORT")), 60)
    except Exception as e:
        print(f"[!] HOST could not connect to MQTT: {e}")
        return

    mqttc.loop_start()

    threads = [
        threading.Thread(target=ask_ai_loop, args=(), daemon=True),
        threading.Thread(target=text_to_speach_loop, args=(mqttc,), daemon=True)
    ]

    for t in threads:
        t.start()

    print("[*] System running. Press Ctrl+C to stop.")

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n[*] Shutting down...")

if __name__ == "__main__":
    main()
