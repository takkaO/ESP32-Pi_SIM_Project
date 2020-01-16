import serial
from serial.tools import list_ports
import re
import json
import time
from myMqtt import MyMqtt, CallbackType


def on_connect(client, userdata, flags, respons_code):
	print('status {0}'.format(respons_code))


def on_publish(client, userdata, result):
	print("  published")


def splitData(raw_data):
	pattern = r'([A-Z0-9]*_[0-9]*):([a-zA-Z0-9]*):(.*)\r\n'
	result = re.search(pattern, raw_data)
	if result:
		return result.group(1), result.group(2), result.group(3)
	return "", "", ""


def main(port_name):
	mymqtt = MyMqtt()
	mymqtt.set_callback_function(CallbackType.ON_CONNECT, on_connect)
	mymqtt.set_callback_function(CallbackType.ON_PUBLISH, on_publish)
	mymqtt.connect_to_broker()

	# 使用環境に応じてCOM番号を変えること
	com = serial.Serial(port_name, 9600, timeout=60)
	print("Initializing...")
	print(com.readline())
	print("Ready!")

	while True:
		d = {}
		time.sleep(1)
		while not com.inWaiting() == 0:
			data = com.readline().decode('utf-8')
			ret = splitData(data)
			if ret[1] == "Time" or ret[1] == "":
				continue
			d[ret[1]] = ret[2]
		if not d == {}:
			data = json.dumps(d)
			mymqtt.publish("sensor", data)

if __name__ == "__main__":
	ports = []
	for i, info in enumerate(list_ports.comports()):
		print(i, info.device)
		ports.append(info.device)
	print("Select serial port: ", end="")
	num = input()
	port = 0
	try:
		num = int(num)
		port = ports[num]
	except:
		print("Invalid selection")
		exit(1)
	main(port)
