#include <Arduino.h>
#include <WiFi.h>
#include <WiFiClientSecure.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <time.h>
#include "secrets.h"

// Konfiguracja
const char* COMMAND_TOPIC = "devices/esp32-001/commands";
const char* RESPONSE_TOPIC = "devices/esp32-001/responses";

constexpr int LED_PIN = 2;

// Lista bezpiecznych pinów wyjściowych (zgodnie z wymaganiami prowadzącej)
constexpr int OUTPUT_PINS[] = { 2, 4, 5, 16, 17, 18, 19, 21, 22, 23, 25, 26, 27, 32, 33 };

WiFiClientSecure secureClient;
PubSubClient mqtt(secureClient);

// Funkcja pomocnicza sprawdzająca, czy pin jest dozwolony
bool isAllowedOutputPin(int pin) {
    for (int allowedPin : OUTPUT_PINS) {
        if (allowedPin == pin) {
            return true;
        }
    }
    return false;
}

void onMessage(char* topic, byte* payload, unsigned int length) {
    JsonDocument command;
    DeserializationError error =
        deserializeJson(command, payload, length);

    if (error) {
        Serial.println("Niepoprawny JSON");
        return;
    }

    String action = command["action"] | "";
    String commandId = command["command_id"] | "";

    bool success = true;
    int targetPin = command["pin"] | LED_PIN;
    String responseState = "";

    // 1. Włączenie pojedynczego pinu
    if (action == "pin_on" || action == "led_on") {
        int p = (action == "led_on") ? LED_PIN : targetPin;
        if (isAllowedOutputPin(p)) {
            pinMode(p, OUTPUT);
            digitalWrite(p, HIGH);
            targetPin = p;
        } else {
            success = false;
        }
    } 
    // 2. Wyłączenie pojedynczego pinu
    else if (action == "pin_off" || action == "led_off") {
        int p = (action == "led_off") ? LED_PIN : targetPin;
        if (isAllowedOutputPin(p)) {
            pinMode(p, OUTPUT);
            digitalWrite(p, LOW);
            targetPin = p;
        } else {
            success = false;
        }
    } 
    // 3. Włączenie WSZYSTKICH pinów naraz
    else if (action == "all_pins_on") {
        for (int p : OUTPUT_PINS) {
            pinMode(p, OUTPUT);
            digitalWrite(p, HIGH);
        }
        responseState = "all_on";
    } 
    // 4. Wyłączenie WSZYSTKICH pinów naraz
    else if (action == "all_pins_off") {
        for (int p : OUTPUT_PINS) {
            pinMode(p, OUTPUT);
            digitalWrite(p, LOW);
        }
        responseState = "all_off";
    } 
    // 5. Sprawdzenie stanu
    else if (action != "get_led_state" && action != "get_pin_state") {
        success = false;
    }

    JsonDocument response;
    response["command_id"] = commandId;
    response["success"] = success;
    response["pin"] = targetPin;
    
    if (responseState != "") {
        response["state"] = responseState;
    } else {
        response["state"] = digitalRead(targetPin) == HIGH ? "high" : "low";
    }
    
    // Zachowanie wstecznej kompatybilności dla pola "led"
    response["led"] = digitalRead(LED_PIN) == HIGH ? "on" : "off";

    String output;
    serializeJson(response, output);

    mqtt.publish(RESPONSE_TOPIC, output.c_str());
    Serial.println(output);
}

void setup() {
    Serial.begin(115200);

    pinMode(LED_PIN, OUTPUT);
    digitalWrite(LED_PIN, LOW);

    WiFi.mode(WIFI_STA);
    WiFi.setSleep(false);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);

    Serial.print("Laczenie Wi-Fi");
    while (WiFi.status() != WL_CONNECTED) {
        delay(500);
        Serial.print(".");
    }

    Serial.println("\nWi-Fi polaczone");

    // Synchronizacja czasu dla TLS
    configTime(0, 0, "pool.ntp.org");

    while (time(nullptr) < 1700000000) {
        delay(500);
    }

    secureClient.setCACert(ROOT_CA);

    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    mqtt.setCallback(onMessage);
    mqtt.setBufferSize(512);

    Serial.println("Konfiguracja MQTT gotowa");
}

void loop() {
    if (WiFi.status() != WL_CONNECTED) {
        delay(1000);
        return;
    }

    if (!mqtt.connected()) {
        Serial.println("Laczenie MQTT...");

        if (mqtt.connect(
                "esp32-001",
                MQTT_USER,
                MQTT_PASS
            )) {
            mqtt.subscribe(COMMAND_TOPIC);
            Serial.println("MQTT polaczone!");
        } else {
            Serial.print("MQTT error: ");
            Serial.println(mqtt.state());
            delay(5000);
        }
    }

    mqtt.loop();
}