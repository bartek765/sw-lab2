import json

from llm_client import chat_completion
from tool_registry import TOOLS, execute_tool


SYSTEM_PROMPT = """
Jesteś asystentem sterującym ESP32.
Odpowiadaj po polsku.

Masz dostęp do narzędzi umożliwiających:
- włączanie lub wyłączanie konkretnego pinu (np. set_pin_state)
- włączanie lub wyłączanie wszystkich pinów naraz (np. control_all_pins)
- sprawdzanie stanu pinu lub pinów (np. get_pin_status)
- starsze funkcje LED (turn_led_on, turn_led_off, get_led_state)

Gdy użytkownik prosi o zmianę stanu pinu lub diody, użyj odpowiedniego narzędzia.
Gdy pyta o stan, odczytaj go z urządzenia.

Nie twierdź, że operacja się powiodła,
jeśli narzędzie zwróciło błąd.

Nie wymyślaj danych urządzenia.
"""


class ESP32Agent:

    def __init__(self):
        self.messages = [
            {
                "role": "system",
                "content": SYSTEM_PROMPT
            }
        ]

    def chat(self, user_message):
        self.messages.append({
            "role": "user",
            "content": user_message
        })

        for step in range(8):
            stream = chat_completion(
                messages=self.messages,
                tools=TOOLS
            )

            text_parts = []
            tool_calls = {}

            # Odbieranie fragmentów odpowiedzi LLM
            for chunk in stream:
                if not chunk.choices:
                    continue

                delta = chunk.choices[0].delta

                # Streaming tekstu
                if delta.content:
                    print(delta.content, end="", flush=True)
                    text_parts.append(delta.content)

                # Streaming wywołań narzędzi
                for tool in delta.tool_calls or []:
                    index = tool.index

                    if index not in tool_calls:
                        tool_calls[index] = {
                            "id": "",
                            "name": "",
                            "arguments": ""
                        }

                    current = tool_calls[index]

                    if tool.id:
                        current["id"] += tool.id

                    if tool.function:
                        if tool.function.name:
                            current["name"] += tool.function.name

                        if tool.function.arguments:
                            current["arguments"] += (
                                tool.function.arguments
                            )

            # Odtworzenie wiadomości asystenta
            assistant_message = {
                "role": "assistant",
                "content": "".join(text_parts) or None
            }

            if tool_calls:
                assistant_message["tool_calls"] = [
                    {
                        "id": tool["id"],
                        "type": "function",
                        "function": {
                            "name": tool["name"],
                            "arguments": tool["arguments"]
                        }
                    }
                    for _, tool in sorted(tool_calls.items())
                ]

            self.messages.append(assistant_message)

            # Brak narzędzi = odpowiedź końcowa
            if not tool_calls:
                return "".join(text_parts)

            # Wykonanie narzędzi
            for _, tool in sorted(tool_calls.items()):
                name = tool["name"]

                try:
                    arguments = json.loads(
                        tool["arguments"] or "{}"
                    )

                    print(f"\n[TOOL CALL] {name}({arguments})", flush=True)

                    result = execute_tool(
                        name,
                        arguments
                    )

                except Exception as exc:
                    result = {"error": str(exc)}

                # Wynik narzędzia wraca do LLM
                self.messages.append({
                    "role": "tool",
                    "tool_call_id": tool["id"],
                    "content": json.dumps(
                        result,
                        ensure_ascii=False
                    )
                })

        return "Przekroczono limit kroków agenta."