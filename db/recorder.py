import json
import paho.mqtt.client as mqtt
import sqlite3
import os
import configparser

DB_PATH = "./rasp.sqlite3"


def on_connect(client, userdata, flag, rc):
	print('mqtt status {0}'.format(rc))
	client.subscribe("labmen/pi/info")


def on_message(client, userdata, msg):
	print("Received message!")
	try:
		data = json.loads(msg.payload.decode("utf-8"))
		data_time = "{0}-{1}-{2} {3}:{4}:{5}".format(
													data["time"]["year"], 
													data["time"]["month"],
													data["time"]["day"], 
													data["time"]["hour"], 
													data["time"]["minute"], 
													data["time"]["second"]
													)

		if not os.path.isfile(DB_PATH):
			print("Error DB not found!")
			exit(1)
		q = "insert into rasp values (?, ?, ?, ?, ?, ?, ?, ?, ?, ?);"
		d = (
			data_time, 
			data["cpu"]["temp (\'C)"], 
			data["cpu"]["clock (Hz)"],
			data["cpu"]["use rate (%)"], 
			data["memory"]["total (MB)"], 
			data["memory"]["used (MB)"], 
			data["memory"]["free (MB)"], 
			data["system"]["power status"]["raw_value"], 
			data["system"]["power status"]["status"],
			data["system"]["process"]["process_num"]
			)
		conn = sqlite3.connect(DB_PATH)
		c = conn.cursor()
		c.execute(q, d)

		conn.commit()
		conn.close()
		print("Insert complete!")
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
		q = 'create table rasp(\
			time text, \
			cpu_temp float, \
			cpu_freq integer, \
			cpu_usage float, \
			mem_total integer, \
			mem_used integer, \
			mem_free integer, \
			throttled_raw text, \
			throttled_stat text, \
			process_num integer \
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

	client.loop_forever()


if __name__ == "__main__":
	main()
