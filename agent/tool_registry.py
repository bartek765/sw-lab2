from esp32_tools import (
    get_led_state,
    turn_led_on,
    turn_led_off,
    set_pin_state,
    control_all_pins,
    get_pin_status,
    OUTPUT_PINS
)

TOOL_FUNCTIONS = {
    "get_led_state": get_led_state,
    "turn_led_on": turn_led_on,
    "turn_led_off": turn_led_off,
    "set_pin_state": set_pin_state,
    "control_all_pins": control_all_pins,
    "get_pin_status": get_pin_status,
}

# Definicje schematów narzędzi dla LLM (w tym wsparcie dla argumentów)
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "get_led_state",
            "description": "Sprawdza aktualny stan LED na ESP32.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "turn_led_on",
            "description": "Włącza diodę LED na ESP32.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "turn_led_off",
            "description": "Wyłącza diodę LED na ESP32.",
            "parameters": {"type": "object", "properties": {}, "additionalProperties": False}
        }
    },
    {
        "type": "function",
        "function": {
            "name": "set_pin_state",
            "description": "Włącza lub wyłącza wybrany pin GPIO.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "enum": OUTPUT_PINS,
                        "description": "Numer dozwolonego pinu wyjściowego."
                    },
                    "state": {
                        "type": "string",
                        "enum": ["high", "low"],
                        "description": "Stan pinu: 'high' (włączony) lub 'low' (wyłączony)."
                    }
                },
                "required": ["pin", "state"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "control_all_pins",
            "description": "Włącza lub wyłącza wszystkie dozwolone piny naraz.",
            "parameters": {
                "type": "object",
                "properties": {
                    "action_type": {
                        "type": "string",
                        "enum": ["on", "off"],
                        "description": "Akcja: 'on' (włącz wszystkie) lub 'off' (wyłącz wszystkie)."
                    }
                },
                "required": ["action_type"],
                "additionalProperties": False
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "get_pin_status",
            "description": "Sprawdza stan wybranego pinu.",
            "parameters": {
                "type": "object",
                "properties": {
                    "pin": {
                        "type": "integer",
                        "enum": OUTPUT_PINS,
                        "description": "Opcjonalny numer pinu do sprawdzenia."
                    }
                },
                "additionalProperties": False
            }
        }
    }
]


def execute_tool(name, arguments):
    if name not in TOOL_FUNCTIONS:
        return {"error": f"Nieznane narzędzie: {name}"}

    # Narzędzia przyjmujące argumenty
    if name in ["set_pin_state", "control_all_pins"]:
        return TOOL_FUNCTIONS[name](**arguments)
    
    # Narzędzia z opcjonalnymi argumentami
    if name == "get_pin_status":
        pin = arguments.get("pin") if arguments else None
        return TOOL_FUNCTIONS[name](pin=pin)

    # Stare narzędzia bez argumentów
    if arguments:
        return {"error": "To narzędzie nie przyjmuje argumentów"}

    return TOOL_FUNCTIONS[name]()