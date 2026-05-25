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
    print("Subscribing:")
    print("-> hermes/nlu/intentNotRecognized")
    print("-> hermes/intent/#")
    print("-> hermes/hotword/alexa/detected")
    client.subscribe("hermes/nlu/intentNotRecognized")
    client.subscribe("hermes/intent/#") # '#' is for all intents
    client.subscribe("hermes/hotword/alexa/detected")
    client.subscribe("hermes/hotword/toggleOn")
    client.subscribe("hermes/hotword/toggleOff")

def on_message(client, userdata, msg):
    parsed_msg = json.loads(msg.payload)
    print(f"topic: {msg.topic}")

    if msg.topic == "hermes/nlu/intentNotRecognized":
        text = parsed_msg.get('input', '')
        print(f"Not recognized: {text}")
        answer = ask_ai(text)
        print(answer)

    elif msg.topic.startswith("hermes/intent/"):
        text = parsed_msg.get('input', '')
        print(f"Intent: {text}")

    elif msg.topic == "hermes/hotword/alexa/detected":
        print("alexa here!")

    else:
        print("Other message")

mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
mqttc.on_connect = on_connect
mqttc.on_message = on_message

mqttc.connect("localhost", 1883, 60)

mqttc.loop_forever()
