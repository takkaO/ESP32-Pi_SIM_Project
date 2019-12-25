# ESP32-RaspberryPi SIM connection project

## Installation
Install ```PlatformIO``` for writing program into ESP32.
```
python3 -m pip install platformio
```

Expose PATH.
```
echo 'export PATH=${PATH}:/home/pi/.local/bin' >> ~/.bashrc
# Check
which platformio
```

(If need) Install library.
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

## Reference
- [CUI で Raspberry Pi から Arduino のスケッチを書き込む（platformio）](https://qiita.com/ancolin/items/d4291b994c422a01b6b3)
- [Raspberry Pi の OS に関する情報やハードウェアの情報を得る](https://www.bnote.net/raspberry_pi/info_cmd.html)
- [Raspberry Pi CPU周波数、CPU温度、CPU使用率の取得Pythonスクリプト](http://my-web-site.iobb.net/~yuki/2017-10/raspberry-pi/cpustat/)
- [ラズパイの電源不足を調べてみました。](https://raspberrypi.mongonta.com/underpower/)
- [RaspberryPi Documentation](https://github.com/raspberrypi/documentation/blob/JamesH65-patch-vcgencmd-vcdbg-docs/raspbian/applications/vcgencmd.md)
- [Python3でpyserialを使う](https://qiita.com/gazami/items/d1d5801beeb4d42393bb)
- [pythonでMQTT送受信](https://qiita.com/hsgucci/items/6461d8555ea1245ef6c2)
- [PythonからSQLite3で初めてのデータベース！](https://qiita.com/DNA1980/items/1fbcb95e8ee5771d6b2b)
