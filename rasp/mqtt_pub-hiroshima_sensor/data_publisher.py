import serial
from serial.tools import list_ports
import re
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
		data = com.readline().decode('utf-8')
		ret = splitData(data)
		if ret[1] == "Temp" or ret[1] == "Time" or ret[1] == "":
			continue
		if ret[1] in {"CO2", "Pres"}:
			base_topic = "sensor1/data1/"
			print(base_topic + ret[1], ret[2], end="")
			mymqtt.publish(base_topic + ret[1], ret[2])
		elif ret[1] in {"Humi", "Light"}:
			base_topic = "sensor1/data2/"
			print(base_topic + ret[1], ret[2], end="")
			mymqtt.publish(base_topic + ret[1], ret[2])


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
