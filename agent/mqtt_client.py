import json
import os
import threading
import uuid


def build_command_payload(command_id, action, **parameters):
    payload = {"command_id": command_id, "action": action}
    payload.update({k: v for k, v in parameters.items() if v is not None})
    return payload


def send_command(action, timeout=15, **parameters):
    import paho.mqtt.client as mqtt
    host = os.environ["MQTT_HOST"]
    user = os.environ["MQTT_USER"]
    password = os.environ["MQTT_PASSWORD"]
    commands = os.environ["MQTT_COMMAND_TOPIC"]
    responses = os.environ["MQTT_RESPONSE_TOPIC"]
    command_id = str(uuid.uuid4())
    signal = threading.Event()
    result = {}
    client = mqtt.Client(mqtt.CallbackAPIVersion.VERSION2)
    client.username_pw_set(user, password)
    client.tls_set()

    def on_connect(client, userdata, flags, reason_code, properties):
        if reason_code == 0:
            client.subscribe(responses, qos=1)
        else:
            result.update({"success": False, "error": f"MQTT connect: {reason_code}"})
            signal.set()

    def on_subscribe(client, userdata, mid, reason_codes, properties):
        payload = build_command_payload(command_id, action, **parameters)
        client.publish(commands, json.dumps(payload), qos=1)

    def on_message(client, userdata, msg):
        try:
            data = json.loads(msg.payload.decode("utf-8"))
        except (ValueError, UnicodeDecodeError):
            return
        if data.get("command_id") == command_id:
            result.update(data)
            signal.set()

    client.on_connect = on_connect
    client.on_subscribe = on_subscribe
    client.on_message = on_message
    try:
        client.connect(host, int(os.getenv("MQTT_PORT", "8883")), keepalive=30)
        client.loop_start()
        if not signal.wait(timeout):
            return {"success": False, "error": "Timeout MQTT", "command_id": command_id}
        return result
    finally:
        client.disconnect()
        client.loop_stop()
