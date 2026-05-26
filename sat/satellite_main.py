import time
import json
import threading
import paho.mqtt.client as mqtt

import wake_word
import record_command
import send_command
import send_text_as_intent

import os

from read_config import get_from_config as config

import re

wake_word_active = threading.Event()
wake_word_active.set()

record_command_active = threading.Event()
record_command_active.clear()

send_text_as_intent_active = threading.Event()
send_text_as_intent_active.clear()

intent_text=""

# =========================
# WAKE WORD LOOP
# =========================
def wake_word_loop(mqttc):
    print("[*] Wake word thread started")
    while True:

        wake_word_active.wait()
        heard = wake_word.listen_for_wake_word()

        if heard and wake_word_active.is_set():
            payload = {"siteId": "default", "modelId": "alexa"}
            mqttc.publish("hermes/hotword/alexa/detected", json.dumps(payload))
            # optionally
            time.sleep(0.2)

# =========================
# COMMAND LOOP
# =========================
def command_loop(mqttc):
    print("[*] Command thread started")
    while True:

        record_command_active.wait()
        recorded = record_command.main()

        if recorded and record_command_active.is_set():

            print(f"[*] Start Speech to text with Whispercpp on {config(parameter="HOST_IP")}:8080")

            #whitelist = set('abcdefghijklmnopqrstuvwxyz ABCDEFGHIJKLMNOPQRSTUVWXYZ')
            
            raw_text = send_command.main()
            #text = ''.join(filter(whitelist.__contains__, raw_text))
            
            text = re.sub(r'[^\w\s]', '', raw_text)
            text = text.strip()

            if text:
                print(f"[*] Whisper says: {text}")

                payload = {"text": text, "siteId": "default"}
                mqttc.publish("hermes/asr/textCaptured", json.dumps(payload))

            mqttc.publish(
                "hermes/asr/stopListening",
                json.dumps({"siteId": "default"})
            )

        # prevents looping of recording
        time.sleep(0.1)

# =========================
# SEND INTENT LOOP
# =========================
def send_intent_loop():
    global intent_text
    print("[*] Send intent thread started")
    while True:

        send_text_as_intent_active.wait()

        if intent_text:
            print(f"[*] Sending intent to NLU: {intent_text}")

            success = send_text_as_intent.send_intent_to_recognize(intent_text)

            if success:
                print("[*] Intent sent successfully")

        intent_text = ""
        send_text_as_intent_active.clear()


# =========================
# MQTT
# =========================
def on_connect(client, userdata, flags, reason_code, properties):
    print("[*] Connected to MQTT Broker")
    topics = [
        "hermes/hotword/alexa/detected",
        "hermes/hotword/toggleOn",
        "hermes/hotword/toggleOff",
        "hermes/asr/startListening",
        "hermes/asr/stopListening",
        "hermes/asr/textCaptured",
        "hermes/response/ready"
    ]
    for topic in topics:
        client.subscribe(topic)

def on_message(client, userdata, msg):
    print(f"[*] Topic: {msg.topic}")

    # State logic
    if msg.topic == "hermes/hotword/alexa/detected":
        wake_word_active.clear()

        #Session initialize
        session_payload = {
            "siteId": "default",
            "init": {
                "type": "action",
                "canBeEnqueued": False
            },
            "customData": "alexa_session"
        }
        client.publish("hermes/dialogueManager/startSession", json.dumps(session_payload))

        client.publish("hermes/asr/startListening", json.dumps({"siteId": "default"}))

    elif msg.topic == "hermes/hotword/toggleOn":
        wake_word_active.set()

    elif msg.topic == "hermes/hotword/toggleOff":
        wake_word_active.clear()

    elif msg.topic == "hermes/asr/startListening":
        record_command_active.set()

    elif msg.topic == "hermes/asr/stopListening":
        record_command_active.clear()
        client.publish("hermes/hotword/toggleOn", json.dumps({"siteId": "default"}))

    elif msg.topic == "hermes/asr/textCaptured":
        global intent_text

        raw_intent = msg.payload
        raw_intent = raw_intent.decode('utf-8')
        raw_intent = json.loads(raw_intent)
        intent = raw_intent["text"]
        intent_text = intent

        send_text_as_intent_active.set()

    elif msg.topic == "hermes/response/ready":
        print("[* ] >>>>>>>> STARTING AUDIO <<<<<<<<")
        os.system("aplay -D plughw:0,0 -c 2 -t wav response.wav")
        pass

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
        mqttc.connect(config(parameter="HOST_IP"), int(config(parameter="MQTT_PORT")), 60)
    except Exception as e:
        print(f"[!] Could not connect to MQTT: {e}")
        return

    mqttc.loop_start()

    threads = [
        threading.Thread(target=wake_word_loop, args=(mqttc,), daemon=True),
        threading.Thread(target=command_loop, args=(mqttc,), daemon=True),
        threading.Thread(target=send_intent_loop, args=(), daemon=True)
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
