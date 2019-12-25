#include <WiFi.h>
#include <WebServer.h>
#include <PubSubClient.h>
#include <SPIFFS.h>
#include <ArduinoJson.h>
#include "dynamicWiFi.h"


// PIN
const int MODE_SWITCH = SWITCH1;

// Wi-Fi Config file
const char *settings = "/wifi_settings.txt";
const char *broker_settings = "/broker_settings.txt";
const char ssid[] = "ESP32-AP"; // SSID
const char pass[] = "12345678"; // password


enum OP_MODE op_mode = SERVER;

WebServer server(80);
IPAddress local_ip(192, 168, 4, 1);
IPAddress gateway(192, 168, 4, 1);
IPAddress subnet(255, 255, 255, 0);

WiFiClient espClient;
PubSubClient client(espClient);

void setup() {
    Serial.begin(115200);    
    delay(1000);

    // Initialize file system
    if (!SPIFFS.begin(true)){
        Serial.println("An Error has occurred while mounting SPIFFS");
		delay(1000);
		ESP.restart();
    }

    pinMode(MODE_SWITCH, INPUT);
	pinMode(LED_WIFI, OUTPUT);
	pinMode(LED1, OUTPUT);
	pinMode(LED5, OUTPUT);

	digitalWrite(LED1, LOW);
	digitalWrite(LED5, LOW);
	digitalWrite(LED_WIFI, LOW);

    if (digitalRead(MODE_SWITCH) == LOW) {	
        serverSetup();
        op_mode = SERVER;
		digitalWrite(LED1, HIGH);
    }
    else{
        clientSetup();
        op_mode = CLIENT;
		brokerSetup();
    }
}

int mqtt_error_counter = 0;
void loop() {
    if (op_mode == SERVER) {
        /* If server mode */
        server.handleClient();
        return;
    }

    /* If client mode */
	// check WiFi Connection
	if (WiFi.status() != WL_CONNECTED) {
		digitalWrite(LED_WIFI, LOW);
		clientSetup();
		return;
	}
	digitalWrite(LED_WIFI, HIGH);

	String s;
	char c[2048] = {0};
	StaticJsonDocument <2048> doc;

	if (Serial.available()) {
		s = Serial.readStringUntil('\n');
		DeserializationError error = deserializeJson(doc, s);
		s.toCharArray(c, s.length() + 1);
		
		if(checkMqttConnection()){		
			if (error) {
				// Json format error
				//client.publish("labmen/pi/info", "error");
			}
			else{
				client.publish("labmen/pi/info", c);
			}
		}
	}

	if(checkMqttConnection()){
		mqtt_error_counter = 0;
		digitalWrite(LED5, HIGH);
	}
	else{
		mqtt_error_counter += 1;
		if (mqtt_error_counter == 5) {
			// Faild to connect broker 5 times,
			// Reset ESP32
			Serial.println("\nRestart ESP32");
			ESP.restart();
		}
		digitalWrite(LED5, LOW);
	}
	client.loop();
}


void brokerSetup(){
	File f = SPIFFS.open(broker_settings, "r");
    String host = f.readStringUntil('\n');
    String port = f.readStringUntil('\n');
    f.close();

	host.trim();
    port.trim();

	Serial.println("HOST: " + host);
    Serial.println("PORT: " + port);

	char host_c[128] = {0};
	host.toCharArray(host_c, host.length() + 1);
	client.setServer(host_c, port.toInt());
}


bool checkMqttConnection(){
    // MQTT connection
    if (!client.connected()) {
        // IDが重複しないように乱数を追加
        String clientID = "LabMenV2_ESP32_SIM-" + String(esp_random());
        Serial.println(clientID);
        client.connect(clientID.c_str());
        if (client.connected()) {
            // Broker接続成功
            Serial.print("MQTT connected!");
        }
        else {
            Serial.println("MQTT connection failed: ");
            switch(client.state()){
                case -4:
                    Serial.println("[MQTT Error] Broker connection timeout.");
                    break;
                case -3:
                    Serial.println("[MQTT Error] Network connection broken.");
                    break;
                case -2:
                    Serial.println("[MQTT Error] Network connection failed.");
                    break;
                case -1:
                    Serial.println("[MQTT Warning] Disconnect OK.");
                    break;
                case 0:
                    break;
                default:
                    Serial.print("[MQTT Error] status code = ");
                    Serial.println(client.state());
                    break;
            }
            //Serial.println(client.state());
            delay(1000);
            return false;
        }
    }
    return true;
}