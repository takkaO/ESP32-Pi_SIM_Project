# ESP32-RaspberryPi SIM connection project

## Installation
```
platformio lib install 64
platformio lib install 89
```

## Edit WiFi and Broker setting
1. Push SW1 and reset.  
2. Check turn on LED1.  
3. Access to WiFi ```ESP32-AP```. Password is ```12345678```.  
4. Open browser and access to ```192.168.4.1```.

## Caution
You need to rewrite ```MQTT_MAX_PACKET_SIZE``` in ```PubSubClient.h```.  
Redefine was not work!  
```
#define MQTT_MAX_PACKET_SIZE 2048
```
