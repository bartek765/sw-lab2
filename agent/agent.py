import json
import os
from openai import OpenAI
from .esp32_tools import OUTPUT_PINS, set_digital_output

TOOLS = [{"type": "function", "function": {
    "name": "set_digital_output",
    "description": "Ustawia stan cyfrowy pinu ESP32. Opcjonalny czas przywraca LOW.",
    "parameters": {"type": "object", "properties": {
        "pin": {"type": "integer", "enum": OUTPUT_PINS},
        "state": {"type": "string", "enum": ["high", "low"]},
        "duration_seconds": {"type": "integer", "minimum": 1, "maximum": 3600}
    }, "required": ["pin", "state"], "additionalProperties": False}
}}]
SYSTEM = ("Sterujesz wyjściami ESP32 przez narzędzie set_digital_output. "
          "Nie podawaj sukcesu przed potwierdzeniem MQTT. "
          "Dopuszczalne są tylko GPIO z definicji narzędzia; czas w sekundach. "
          "Gdy wynik zawiera success=false, wyświetl przyczynę.")


def respond(message, history):
    client = OpenAI(api_key=os.environ["OPENROUTER_API_KEY"],
                    base_url="https://openrouter.ai/api/v1")
    messages = [{"role": "system", "content": SYSTEM}]
    for item in history[-12:]:
        if item.get("role") in ("user", "assistant") and isinstance(item.get("content"), str):
            messages.append({"role": item["role"], "content": item["content"]})
    messages.append({"role": "user", "content": message})
    model = os.getenv("OPENROUTER_MODEL", "openai/gpt-4o-mini")
    response = client.chat.completions.create(model=model, messages=messages, tools=TOOLS,
                                              tool_choice="auto")
    choice = response.choices[0].message
    if not choice.tool_calls:
        return choice.content or "Brak odpowiedzi modelu."
    messages.append(choice.model_dump(exclude_none=True))
    for call in choice.tool_calls:
        if call.function.name != "set_digital_output":
            result = {"success": False, "error": "Nieznane narzędzie"}
        else:
            try:
                args = json.loads(call.function.arguments)
                result = set_digital_output(**args)
            except (ValueError, TypeError) as exc:
                result = {"success": False, "error": str(exc)}
        messages.append({"role": "tool", "tool_call_id": call.id,
                         "content": json.dumps(result, ensure_ascii=False)})
    final = client.chat.completions.create(model=model, messages=messages)
    return final.choices[0].message.content or "Brak odpowiedzi."
