import json
import paho.mqtt.client as mqtt
import sqlite3
import os
import datetime
import datetime
import configparser

DB_PATH = "./rasp.sqlite3"


def on_connect(client, userdata, flag, rc):
	print('mqtt status {0}'.format(rc))
	client.subscribe("sensor")


def on_message(client, userdata, msg):
	print("Received message! -> {0}".format(datetime.datetime.now()))
	try:
		data = json.loads(msg.payload.decode("utf-8"))
		
		if not os.path.isfile(DB_PATH):
			print("Error DB not found!")
			exit(1)
		q = "insert into sensor values (?, ?, ?, ?, ?, ?);"
		d = (
			datetime.datetime.now(),
			data["CO2"],
			data["Pres"],
			data["Temp"],
			data["Humi"],
			data["Light"]
			)
		conn = sqlite3.connect(DB_PATH)
		c = conn.cursor()
		c.execute(q, d)

		conn.commit()
		conn.close()
		print("Insert complete!  -> {0}".format(datetime.datetime.now()))
	except:
		import traceback
		traceback.print_exc()


def on_disconnect(client, userdata, flag, rc):
	if rc != 0:
		print("Unexpected disconnection.")


def main():
	setting_fpath = "./setting.ini"
	config = configparser.ConfigParser()
	if not os.path.isfile(setting_fpath):
		print("please type broker ip address -> ", end="")
		ip = input()
		print("please type broker port -> ", end="")
		port = input()
		config["Broker"] = {
			"ip": ip,
			"port": port
		}
		with open(setting_fpath, 'w') as configfile:
			config.write(configfile)
		print("Finish to save setting file")
		print("exit...")
		exit()
	if not os.path.isfile(DB_PATH):
		q = 'create table sensor(\
			date string, \
			co2 integer, \
			pressure float, \
			temperture float, \
			humidity float, \
			light integer \
			);'

		conn = sqlite3.connect(DB_PATH)
		c = conn.cursor()
		c.execute(q)
		conn.commit()
		conn.close()

	config.read(setting_fpath)
	ip = config["Broker"]["ip"]
	port = int(config["Broker"]["port"])
	print("Broker: {0}:{1}".format(ip, port))

	client = mqtt.Client()
	client.on_connect = on_connect
	client.on_disconnect = on_disconnect
	client.on_message = on_message

	client.connect(ip, port, keepalive=60)

	try:
		client.loop_forever()
	except KeyboardInterrupt:
		pass

if __name__ == "__main__":
	main()
