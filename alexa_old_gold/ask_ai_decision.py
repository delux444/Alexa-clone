import paho.mqtt.client as mqtt
import json

from ollama import chat
from ollama import ChatResponse


def ask_ai(message):
    response: ChatResponse = chat(model='openchat', messages=[
        {
            'role': 'user',
            'content': message
        }
    ])
    return response['message']['content']

def on_connect(client, userdata, flags, reason_code, properties):
    client.subscribe("hermes/nlu/intentNotRecognized")
    client.subscribe("hermes/intent/#") # '#' is for all intents

def on_message(client, userdata, msg):
    parsed_msg = json.loads(msg.payload)
    print(f"topic: {msg.topic}")

    text = parsed_msg.get('input', '')
    if msg.topic == "hermes/nlu/intentNotRecognized":
        print(f"Not recognized intent: {text}")
        print("Asking AI")
        answer = ask_ai(text)
        print(answer)

    elif msg.topic.startswith("hermes/intent/"):
        print(f"Recognized intent: {text}")

    else:
        print("Other message")


def main():

    print("Ask AI?")

    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)

    mqttc.loop_forever()

if __name__ == "__main__":
    main()
