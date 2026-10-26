# ESP32 AI Agent — Bartosz Kędra

Projekt do ćwiczenia „Systemy wbudowane”: interfejs Gradio, agent LLM (OpenRouter),
komunikacja MQTT/JSON oraz firmware ESP32 z czasowym sterowaniem GPIO.

## Struktura
- `src/main.cpp` — firmware ESP32, walidacja GPIO i timer oparty na `millis()`.
- `agent/mqtt_client.py` — MQTT/TLS, `command_id`, dopasowanie odpowiedzi.
- `agent/esp32_tools.py` — funkcja `set_digital_output` i walidacja argumentów.
- `agent/agent.py` — deklaracja narzędzia LLM oraz obsługa wyniku MQTT.
- `app.py` — interfejs Gradio.
- `tests/test_payload.py` — testy niezależne od urządzenia.

## Instalacja
1. `python -m venv .venv` i aktywacja środowiska.
2. `pip install -r requirements.txt`.
3. Ustaw zmienne: `OPENROUTER_API_KEY`, `OPENROUTER_MODEL`, `MQTT_HOST`,
   `MQTT_PORT` (domyślnie 8883), `MQTT_USER`, `MQTT_PASSWORD`,
   `MQTT_COMMAND_TOPIC`, `MQTT_RESPONSE_TOPIC`.
4. `python -m unittest discover -s tests -v`.
5. `python app.py`.
6. Skopiuj `include/secrets.example.h` do `include/secrets.h` i uzupełnij dane.
7. **Przed użyciem MQTT/TLS na ESP32** w `src/main.cpp` dodaj `secureClient.setCACert(...)`
   z prawidłowym certyfikatem CA brokera; bez tego połączenie TLS nie zadziała.
8. `pio run`, następnie `pio run -t upload` po podłączeniu ESP32.

## Render
Utwórz Web Service z repozytorium GitHub albo użyj `render.yaml` (Blueprint).
Sekrety ustaw w Environment — nie publikuj ich w repozytorium.
Start: `python app.py`.

## MQTT
Polecenie: `{"command_id":"abc", "action":"digital_write", "pin":25,
"state":"high", "duration_seconds":10}`. Firmware odsyła JSON z `success`
i tym samym `command_id`. Po upływie czasu pin wraca do LOW.

## Bezpieczeństwo
Do wyjść podłączaj obciążenia przez odpowiednie układy i ograniczaj prąd.
Lista pinów jest przykładem dla klasycznego ESP32 DevKit; sprawdź zgodność
z konkretną płytką i urządzeniami podłączonymi do GPIO.
