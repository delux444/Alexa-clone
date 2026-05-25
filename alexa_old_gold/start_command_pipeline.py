import threading
import queue
import paho.mqtt.client as mqtt

pipeline_queue = queue.Queue()

def pipeline_worker():

    while True:

        task = pipeline_queue.get()
        if task == "START_PIPELINE":
            print("Starting pipeline in worker thread...")
            try:
                import record_command
                record_command.main()

                import speach_to_text
                speach_to_text.main()

                import send_text_as_intent
                send_text_as_intent.main()
            except Exception as e:
                print(f"Pipeline error: {e}")

        pipeline_queue.task_done()

def on_connect(client, userdata, flags, reason_code, properties):
    print("Connected to Broker. Subscribing...")
    client.subscribe("hermes/hotword/alexa/detected")

def on_message(client, userdata, msg):
    print("Wake word detected! Adding to queue...")
    pipeline_queue.put("START_PIPELINE")

def main():
    worker_thread = threading.Thread(target=pipeline_worker, daemon=True)
    worker_thread.start()

    MQTT_BROKER = "localhost"
    MQTT_PORT = 1883

    mqttc = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    mqttc.on_connect = on_connect
    mqttc.on_message = on_message

    print("Waiting for wake word...")
    mqttc.connect(MQTT_BROKER, MQTT_PORT, 60)
    mqttc.loop_forever()

if __name__ == "__main__":
    main()
