import serial
from serial.tools import list_ports
import re
import json
import time
import datetime
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
	interval_minutes = 1
	delta_sec = interval_minutes * 60

	mymqtt = MyMqtt()
	mymqtt.set_callback_function(CallbackType.ON_CONNECT, on_connect)
	mymqtt.set_callback_function(CallbackType.ON_PUBLISH, on_publish)
	mymqtt.connect_to_broker()

	# 使用環境に応じてCOM番号を変えること
	com = serial.Serial(port_name, 9600, timeout=60)
	print("Initializing...")
	print(com.readline())
	print("Ready!")
	dt = datetime.datetime.now()
	prev_time = datetime.datetime(
            dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)

	print("Data will transmit each {0} minutes.".format(interval_minutes))
	
	while True:
		d = {}
		delta = datetime.datetime.now() - prev_time
		com.reset_input_buffer()
		if delta.seconds >= delta_sec:
			while com.in_waiting == 0:
				pass
			time.sleep(1)
			while not com.in_waiting == 0:
				data = com.readline().decode('utf-8')
				ret = splitData(data)
				#print(ret)
				if ret[1] == "Time" or ret[1] == "":
					continue
				d[ret[1]] = ret[2]

			data = json.dumps(d)
			mymqtt.publish("sensor", data)

			dt = datetime.datetime.now()
			prev_time = datetime.datetime(
				dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)

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
