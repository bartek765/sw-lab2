#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include "secrets.h"

constexpr int OUTPUT_PINS[] = {2, 4, 5, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33};
constexpr unsigned long MAX_SECONDS = 3600;
WiFiClientSecure secureClient;
PubSubClient mqtt(secureClient);
struct Timer {int pin; unsigned long endsAt; bool active;};
Timer timers[15] = {};

bool allowed(int pin) {
  for (int p : OUTPUT_PINS) if (p == pin) return true;
  return false;
}
void reply(const String& id, bool ok, int pin, const char* state, const char* error = "") {
  JsonDocument doc;
  doc["command_id"] = id; doc["action"] = "digital_write";
  doc["success"] = ok; doc["pin"] = pin; doc["state"] = state;
  if (!ok) doc["error"] = error;
  String out; serializeJson(doc, out);
  mqtt.publish(MQTT_RESPONSE_TOPIC, out.c_str());
}
void onMessage(char* topic, byte* payload, unsigned int length) {
  JsonDocument doc;
  if (deserializeJson(doc, payload, length)) return;
  String id = doc["command_id"] | "";
  String action = doc["action"] | "";
  if (action != "digital_write") { reply(id, false, -1, "", "Nieznana akcja"); return; }
  if (!doc["pin"].is<int>() || !doc["state"].is<const char*>()) {
    reply(id, false, -1, "", "Brak parametrow"); return;
  }
  int pin = doc["pin"].as<int>();
  String state = doc["state"].as<String>();
  if (!allowed(pin) || (state != "high" && state != "low")) {
    reply(id, false, pin, "", "GPIO lub stan niepoprawny"); return;
  }
  long seconds = doc["duration_seconds"] | 0L;
  if (seconds < 0 || seconds > (long)MAX_SECONDS ||
      (doc.containsKey("duration_seconds") && seconds == 0)) {
    reply(id, false, pin, "", "Czas spoza zakresu"); return;
  }
  pinMode(pin, OUTPUT); digitalWrite(pin, state == "high" ? HIGH : LOW);
  for (auto &t : timers) if (t.pin == pin && t.active) t.active = false;
  if (seconds > 0) {
    for (auto &t : timers) if (!t.active) {
      t = {pin, millis() + (unsigned long)seconds * 1000UL, true}; break;
    }
  }
  reply(id, true, pin, state.c_str());
}
void reconnect() {
  if (mqtt.connected()) return;
  if (mqtt.connect("esp32-bartosz", MQTT_USER, MQTT_PASSWORD))
    mqtt.subscribe(MQTT_COMMAND_TOPIC);
}
void setup() {
  Serial.begin(115200);
  WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
  while (WiFi.status() != WL_CONNECTED) delay(250);
  // Wymagany zaufany certyfikat CA brokera zamiast trybu insecure.
  // Uzupełnij secureClient.setCACert(...) certyfikatem swojego brokera.
  mqtt.setServer(MQTT_HOST, MQTT_PORT);
  mqtt.setCallback(onMessage);
  mqtt.setBufferSize(512);
}
void loop() {
  reconnect(); mqtt.loop();
  for (auto &t : timers) if (t.active && (long)(millis() - t.endsAt) >= 0) {
    digitalWrite(t.pin, LOW); t.active = false;
  }
  delay(10);
}
