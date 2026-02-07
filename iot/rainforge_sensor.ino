/**
 * RainForge IoT Sensor Firmware
 * ESP32/ESP8266 Arduino Code for Tank Monitoring
 * 
 * Sensors Supported:
 * - Ultrasonic (HC-SR04) for tank level
 * - Flow meter (YF-S201) for water usage
 * - Temperature (DS18B20) for water temp
 * - Rain gauge (tipping bucket)
 * 
 * Communication: MQTT over WiFi
 * 
 * Hardware Setup:
 * - ESP32 DevKit v1
 * - HC-SR04: TRIG=GPIO4, ECHO=GPIO5
 * - Flow: GPIO18 (interrupt)
 * - DS18B20: GPIO23
 * - Rain: GPIO19 (interrupt)
 */

#include <WiFi.h>
#include <PubSubClient.h>
#include <ArduinoJson.h>
#include <OneWire.h>
#include <DallasTemperature.h>

// ====================  CONFIGURATION ====================

// WiFi credentials
const char* WIFI_SSID = "your-ssid";
const char* WIFI_PASSWORD = "your-password";

// MQTT broker (RainForge server)
const char* MQTT_HOST = "mqtt.rainforge.gov.in";  // Or local IP
const int MQTT_PORT = 1883;
const char* MQTT_USER = "device";
const char* MQTT_PASS = "device-password";

// Device identification
const char* DEVICE_ID = "RF-TANK-001";
const int PROJECT_ID = 1;

// Tank dimensions (cm)
const float TANK_HEIGHT = 150.0;  // Total height
const float TANK_MIN_LEVEL = 10.0;  // Sensor blind zone

// Reading interval (ms)
const unsigned long READ_INTERVAL = 60000;  // 1 minute
const unsigned long MQTT_RETRY = 5000;

// ==================== PIN DEFINITIONS ====================

#define TRIG_PIN 4
#define ECHO_PIN 5
#define FLOW_PIN 18
#define TEMP_PIN 23
#define RAIN_PIN 19
#define LED_PIN 2  // Built-in LED

// ==================== GLOBAL VARIABLES ====================

WiFiClient wifiClient;
PubSubClient mqtt(wifiClient);

OneWire oneWire(TEMP_PIN);
DallasTemperature tempSensor(&oneWire);

// Interrupt counters
volatile unsigned long flowPulses = 0;
volatile unsigned long rainTips = 0;

// Timing
unsigned long lastReadTime = 0;
unsigned long lastReconnect = 0;

// Calibration constants
const float FLOW_CALIBRATION = 7.5;  // Pulses per liter
const float RAIN_MM_PER_TIP = 0.2;  // mm per tip

// ==================== MQTT TOPICS ====================

char topicTankLevel[64];
char topicFlowRate[64];
char topicTemperature[64];
char topicRainfall[64];
char topicStatus[64];
char topicConfig[64];

// ==================== INTERRUPT HANDLERS ====================

void IRAM_ATTR flowISR() {
    flowPulses++;
}

void IRAM_ATTR rainISR() {
    rainTips++;
}

// ==================== SETUP ====================

void setup() {
    Serial.begin(115200);
    Serial.println("\n🌧️ RainForge IoT Sensor v1.0");
    
    // Setup pins
    pinMode(TRIG_PIN, OUTPUT);
    pinMode(ECHO_PIN, INPUT);
    pinMode(FLOW_PIN, INPUT_PULLUP);
    pinMode(RAIN_PIN, INPUT_PULLUP);
    pinMode(LED_PIN, OUTPUT);
    
    // Attach interrupts
    attachInterrupt(digitalPinToInterrupt(FLOW_PIN), flowISR, RISING);
    attachInterrupt(digitalPinToInterrupt(RAIN_PIN), rainISR, FALLING);
    
    // Initialize temp sensor
    tempSensor.begin();
    
    // Build MQTT topics
    snprintf(topicTankLevel, 64, "rainforge/sensors/%d/tank_level", PROJECT_ID);
    snprintf(topicFlowRate, 64, "rainforge/sensors/%d/flow_rate", PROJECT_ID);
    snprintf(topicTemperature, 64, "rainforge/sensors/%d/temperature", PROJECT_ID);
    snprintf(topicRainfall, 64, "rainforge/sensors/%d/rainfall", PROJECT_ID);
    snprintf(topicStatus, 64, "rainforge/devices/%s/status", DEVICE_ID);
    snprintf(topicConfig, 64, "rainforge/devices/%s/config", DEVICE_ID);
    
    // Connect WiFi
    connectWiFi();
    
    // Setup MQTT
    mqtt.setServer(MQTT_HOST, MQTT_PORT);
    mqtt.setCallback(mqttCallback);
    mqtt.setBufferSize(512);
    
    // Initial connection
    connectMQTT();
    
    // Send startup message
    publishStatus("online");
    
    Serial.println("✅ Setup complete");
}

// ==================== MAIN LOOP ====================

void loop() {
    // Maintain MQTT connection
    if (!mqtt.connected()) {
        if (millis() - lastReconnect > MQTT_RETRY) {
            lastReconnect = millis();
            connectMQTT();
        }
    }
    mqtt.loop();
    
    // Read and publish sensors
    if (millis() - lastReadTime >= READ_INTERVAL) {
        lastReadTime = millis();
        
        digitalWrite(LED_PIN, HIGH);
        
        // Read sensors
        float tankLevel = readTankLevel();
        float flowRate = readFlowRate();
        float temperature = readTemperature();
        float rainfall = readRainfall();
        
        // Publish readings
        publishReading(topicTankLevel, tankLevel, "%");
        
        if (flowRate > 0) {
            publishReading(topicFlowRate, flowRate, "L/min");
        }
        
        if (temperature > -100) {
            publishReading(topicTemperature, temperature, "°C");
        }
        
        if (rainfall > 0) {
            publishReading(topicRainfall, rainfall, "mm");
        }
        
        // Log to serial
        Serial.printf("📊 Tank: %.1f%% | Flow: %.2f L/min | Temp: %.1f°C | Rain: %.1f mm\n",
                      tankLevel, flowRate, temperature, rainfall);
        
        digitalWrite(LED_PIN, LOW);
    }
    
    delay(100);
}

// ==================== SENSOR READING ====================

float readTankLevel() {
    // HC-SR04 ultrasonic reading
    digitalWrite(TRIG_PIN, LOW);
    delayMicroseconds(2);
    digitalWrite(TRIG_PIN, HIGH);
    delayMicroseconds(10);
    digitalWrite(TRIG_PIN, LOW);
    
    long duration = pulseIn(ECHO_PIN, HIGH, 30000);
    
    if (duration == 0) {
        return -1;  // No echo
    }
    
    // Calculate distance (cm)
    float distance = duration * 0.034 / 2;
    
    // Calculate water level
    float waterLevel = TANK_HEIGHT - distance - TANK_MIN_LEVEL;
    waterLevel = constrain(waterLevel, 0, TANK_HEIGHT - TANK_MIN_LEVEL);
    
    // Convert to percentage
    float percentage = (waterLevel / (TANK_HEIGHT - TANK_MIN_LEVEL)) * 100;
    
    return percentage;
}

float readFlowRate() {
    // Calculate flow from pulse count
    static unsigned long lastFlowPulses = 0;
    static unsigned long lastFlowTime = 0;
    
    unsigned long now = millis();
    unsigned long elapsed = now - lastFlowTime;
    unsigned long pulses = flowPulses - lastFlowPulses;
    
    lastFlowPulses = flowPulses;
    lastFlowTime = now;
    
    if (elapsed == 0) return 0;
    
    // Liters per minute
    float litersPerMin = (pulses / FLOW_CALIBRATION) * (60000.0 / elapsed);
    
    return litersPerMin;
}

float readTemperature() {
    tempSensor.requestTemperatures();
    float temp = tempSensor.getTempCByIndex(0);
    
    if (temp == DEVICE_DISCONNECTED_C) {
        return -127;  // Error value
    }
    
    return temp;
}

float readRainfall() {
    // Get accumulated rainfall since last reading
    static unsigned long lastRainTips = 0;
    
    unsigned long tips = rainTips - lastRainTips;
    lastRainTips = rainTips;
    
    float mm = tips * RAIN_MM_PER_TIP;
    
    return mm;
}

// ==================== WIFI CONNECTION ====================

void connectWiFi() {
    Serial.printf("🔗 Connecting to WiFi: %s", WIFI_SSID);
    
    WiFi.mode(WIFI_STA);
    WiFi.begin(WIFI_SSID, WIFI_PASSWORD);
    
    int attempts = 0;
    while (WiFi.status() != WL_CONNECTED && attempts < 20) {
        delay(500);
        Serial.print(".");
        attempts++;
    }
    
    if (WiFi.status() == WL_CONNECTED) {
        Serial.printf("\n✅ Connected! IP: %s\n", WiFi.localIP().toString().c_str());
    } else {
        Serial.println("\n❌ WiFi connection failed!");
        ESP.restart();
    }
}

// ==================== MQTT CONNECTION ====================

void connectMQTT() {
    Serial.print("🔗 Connecting to MQTT...");
    
    String clientId = String(DEVICE_ID) + "-" + String(random(0xffff), HEX);
    
    if (mqtt.connect(clientId.c_str(), MQTT_USER, MQTT_PASS)) {
        Serial.println(" connected!");
        
        // Subscribe to config topic
        mqtt.subscribe(topicConfig);
        
        // Publish online status
        publishStatus("online");
    } else {
        Serial.printf(" failed (rc=%d)\n", mqtt.state());
    }
}

// ==================== MQTT PUBLISHING ====================

void publishReading(const char* topic, float value, const char* unit) {
    if (!mqtt.connected()) return;
    
    StaticJsonDocument<256> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["value"] = value;
    doc["unit"] = unit;
    doc["timestamp"] = getISO8601Time();
    doc["battery"] = getBatteryPercent();
    doc["rssi"] = WiFi.RSSI();
    
    char payload[256];
    serializeJson(doc, payload);
    
    mqtt.publish(topic, payload, false);
}

void publishStatus(const char* status) {
    if (!mqtt.connected()) return;
    
    StaticJsonDocument<256> doc;
    
    doc["device_id"] = DEVICE_ID;
    doc["status"] = status;
    doc["firmware"] = "1.0.0";
    doc["ip"] = WiFi.localIP().toString();
    doc["rssi"] = WiFi.RSSI();
    doc["uptime"] = millis() / 1000;
    
    char payload[256];
    serializeJson(doc, payload);
    
    mqtt.publish(topicStatus, payload, true);
}

// ==================== MQTT CALLBACK ====================

void mqttCallback(char* topic, byte* payload, unsigned int length) {
    Serial.printf("📨 MQTT message on %s\n", topic);
    
    // Handle config updates
    if (strcmp(topic, topicConfig) == 0) {
        StaticJsonDocument<256> doc;
        DeserializationError error = deserializeJson(doc, payload, length);
        
        if (!error) {
            // Apply config updates
            if (doc.containsKey("read_interval")) {
                // Update read interval (would need to restart)
                Serial.printf("Config: read_interval = %d\n", doc["read_interval"].as<int>());
            }
        }
    }
}

// ==================== UTILITIES ====================

String getISO8601Time() {
    // In production, use NTP sync
    // For now, return placeholder
    unsigned long uptime = millis() / 1000;
    char buffer[32];
    snprintf(buffer, 32, "2024-01-01T00:00:%02luZ", uptime % 60);
    return String(buffer);
}

int getBatteryPercent() {
    // ESP32 ADC reading for battery (if using battery power)
    // Connected through voltage divider to GPIO 34
    // For USB power, return 100
    return 100;
}

// ==================== DEBUG ====================

void printDebug() {
    Serial.println("==== Debug Info ====");
    Serial.printf("WiFi: %s (RSSI: %d)\n", WiFi.status() == WL_CONNECTED ? "Connected" : "Disconnected", WiFi.RSSI());
    Serial.printf("MQTT: %s\n", mqtt.connected() ? "Connected" : "Disconnected");
    Serial.printf("Uptime: %lu seconds\n", millis() / 1000);
    Serial.printf("Flow pulses: %lu\n", flowPulses);
    Serial.printf("Rain tips: %lu\n", rainTips);
    Serial.printf("Free heap: %u bytes\n", ESP.getFreeHeap());
    Serial.println("====================");
}
