from mqtt_client import send_command

# Lista dozwolonych pinów wyjściowych zgodna z firmware ESP32
OUTPUT_PINS = [2, 4, 5, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33]

# --- Stare funkcje (zachowane dla kompatybilności) ---

def get_led_state():
    return send_command("get_led_state")


def turn_led_on():
    return send_command("led_on")


def turn_led_off():
    return send_command("led_off")


# --- Nowe funkcje dodane zgodnie z wymaganiami ---

def set_pin_state(pin: int, state: str):
    """Włącza ('high') lub wyłącza ('low') wybrany pin GPIO."""
    action = "pin_on" if state.lower() == "high" else "pin_off"
    return send_command(action, pin=pin, state=state)


def control_all_pins(action_type: str):
    """Włącza ('on') lub wyłącza ('off') wszystkie dozwolone piny naraz."""
    action = "all_pins_on" if action_type.lower() == "on" else "all_pins_off"
    return send_command(action)


def get_pin_status(pin: int = None):
    """Sprawdza stan wybranego pinu lub domyślnego LED."""
    target_pin = pin if pin is not None else 2
    return send_command("get_pin_state", pin=target_pin)