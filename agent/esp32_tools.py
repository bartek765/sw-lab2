from .mqtt_client import send_command

OUTPUT_PINS = [2, 4, 5, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]


def set_digital_output(pin, state, duration_seconds=None):
    if pin not in OUTPUT_PINS:
        return {"success": False, "error": "Niedozwolony GPIO"}
    if state not in ("high", "low"):
        return {"success": False, "error": "Stan musi być high/low"}
    if duration_seconds is not None and not (1 <= duration_seconds <= 3600):
        return {"success": False, "error": "Czas poza zakresem 1–3600 s"}
    return send_command("digital_write", pin=pin, state=state,
                        duration_seconds=duration_seconds)
