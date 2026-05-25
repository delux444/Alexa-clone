def send_intent_to_recognize(text, site_id="default", confidence=1.0):

    import paho.mqtt.client as mqtt
    import uuid
    import json
    from read_config import get_from_config as config

    MQTT_BROKER = config(parameter="HOST_IP")
    MQTT_PORT = int(config(parameter="MQTT_PORT"))
    MQTT_TOPIC = config(parameter="MQTT_TOPIC")

    payload = {

        "input": text,
        "siteId": site_id,
        "id": str(uuid.uuid4()),
        "intentFilter": None,
        "sessionId": None,
        "asrConfidence": confidence

    }

    client = mqtt.Client(callback_api_version=mqtt.CallbackAPIVersion.VERSION2)

    try:
        client.connect(MQTT_BROKER, MQTT_PORT, 60)
        client.publish(MQTT_TOPIC, json.dumps(payload))
        client.disconnect()
        print(f"[*] Published to {MQTT_TOPIC}")
        return True
    except Exception as e:
        print(f"[!] MQTT Error: {e}")
        return False


def main(command="null"):

    if command != "null":
        send_intent_to_recognize(command)

if __name__ == "__main__":
    text = input("intent: ")
    main(command=text)



