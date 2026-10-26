import os
import json
import uuid
import threading

import paho.mqtt.client as mqtt
from dotenv import load_dotenv

load_dotenv()

HOST = os.environ["MQTT_HOST"]
PORT = int(os.getenv("MQTT_PORT", "8883"))
USERNAME = os.environ["MQTT_USERNAME"]
PASSWORD = os.environ["MQTT_PASSWORD"]
DEVICE_ID = os.getenv("MQTT_DEVICE_ID", "esp32-001")

COMMAND_TOPIC = f"devices/{DEVICE_ID}/commands"
RESPONSE_TOPIC = f"devices/{DEVICE_ID}/responses"


def send_command(action, timeout=15, **parameters):
    command_id = str(uuid.uuid4())
    finished = threading.Event()
    result = {}

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(RESPONSE_TOPIC, qos=1)
        else:
            result["error"] = f"MQTT connect: {reason_code}"
            finished.set()

    def on_subscribe(client, userdata, mid, reason_codes, properties):
        if any(code.is_failure for code in reason_codes):
            result["error"] = "Subskrypcja odrzucona"
            finished.set()
            return

        # Budowanie ładunku JSON wraz z dodatkowymi parametrami (np. pin, state)
        payload_dict = {
            "command_id": command_id,
            "action": action
        }
        # Dodanie tylko tych parametrów, które nie są None
        payload_dict.update({k: v for k, v in parameters.items() if v is not None})

        payload = json.dumps(payload_dict)

        info = client.publish(
            COMMAND_TOPIC,
            payload,
            qos=1,
            retain=False
        )

        if info.rc != mqtt.MQTT_ERR_SUCCESS:
            result["error"] = f"Publish error: {info.rc}"
            finished.set()

    def on_message(client, userdata, message):
        try:
            data = json.loads(message.payload.decode())

            if data.get("command_id") == command_id:
                result.update(data)
                finished.set()
        except (ValueError, UnicodeDecodeError):
            pass

    client = mqtt.Client(
        mqtt.CallbackAPIVersion.VERSION2,
        client_id=f"python-{uuid.uuid4().hex[:12]}"
    )

    client.username_pw_set(USERNAME, PASSWORD)
    client.tls_set()

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message

    try:
        client.connect(HOST, PORT, keepalive=30)
        client.loop_start()

        if not finished.wait(timeout):
            raise TimeoutError(
                "Brak potwierdzenia od ESP32 przez MQTT"
            )

        if "error" in result:
            raise RuntimeError(result["error"])

        return result

    finally:
        client.disconnect()
        client.loop_stop()


if __name__ == "__main__":
    print(send_command("get_led_state"))