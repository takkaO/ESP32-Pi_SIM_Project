import serial
import json
import time
import datetime
import subprocess


class SystemInfo():
	def __init__(self):
		self.prev_cpu_use_time = None
		self.cpu_use_time = None
	
	def fetch_cpu_temperature(self):
		res = subprocess.run(["vcgencmd", "measure_temp"], stdout=subprocess.PIPE)
		return res.stdout.decode().rstrip().split("=")[1].split("'")[0]
	
	def fetch_cpu_clock(self):
		res = subprocess.run(["vcgencmd", "measure_clock", "arm"], stdout=subprocess.PIPE)
		return res.stdout.decode().rstrip().split("=")[1]
	
	def fetch_cpu_use_time(self):
		res = subprocess.check_output("cat /proc/stat | grep cpu", shell=True)
		raw_data = res.decode().rstrip().split('\n')[0]
		values = raw_data.replace("  ", " ").split(" ")
		keys = ["name", "user", "nice", "system", "idle", "iowait", "irq", "softirq", "steal", "guest", "guest_nice"]
		self.cpu_use_time = {}
		for key, val in zip(keys, values):
			self.cpu_use_time[key] = val
		return self.cpu_use_time

	def calc_cpu_use_rate(self, realtime=True):
		if self.prev_cpu_use_time is None:
			self.prev_cpu_use_time = self.fetch_cpu_use_time()
			return False, 0.0
		
		if realtime:
			self.cpu_use_time = self.fetch_cpu_use_time()
		
		idle = int(self.cpu_use_time["idle"]) - int(self.prev_cpu_use_time["idle"])
		busy = int(self.cpu_use_time["user"]) + int(self.cpu_use_time["nice"]) + int(self.cpu_use_time["system"])
		busy = busy - (int(self.prev_cpu_use_time["user"]) + int(self.prev_cpu_use_time["nice"]) + int(self.prev_cpu_use_time["system"]))
		self.prev_cpu_use_time = self.cpu_use_time

		return True, round(((busy * 100) / (busy + idle)), 1)
	
	def fetch_cpu_info(self, delta_time = 0.1):
		d = {}
		d["temp ('C)"] = self.fetch_cpu_temperature()
		d["clock (Hz)"] = self.fetch_cpu_clock()
		res, rate = self.calc_cpu_use_rate()
		if not res:
			time.sleep(delta_time)
			_, rate = self.calc_cpu_use_rate()
		d["use rate (%)"] = str(rate)
		return d

	def fetch_memory_info(self):
		res = subprocess.check_output("free | grep Mem", shell=True)
		values = [f for f in res.decode().rstrip().split(" ") if not f == ""]
		values[0] = values[0].replace(":", "")
		d = {}
		#keys = ["name", "total (MB)", "used (MB)", "free (MB)", "shared (MB)", "buff_cache (MB)", "available (MB)"]
		keys = ["name", "total (MB)", "used (MB)", "free (MB)"]
		for key, val in zip(keys, values):
			d[key] = val
		return d
	
	def get_power_shortage_flag_info(self):
		res = subprocess.run(["vcgencmd", "get_throttled"], stdout=subprocess.PIPE)
		value = res.stdout.decode().rstrip().split("=")[1]
		d = {"raw_value": value}
		value = int(value, 16)
		if value == 0x00:
			d["status"] = "normal"
		elif value == 0x50000:
			d["status"] = "normal (past low voltage)"
		elif value == 0x50005:
			d["status"] = "low voltage"
		elif value == 0x80000:
			d["status"] = "normal (past clockdown)"
		elif value == 0x80008:
			d["status"] = "clockdown"
		else:
			d["status"] = "unknown"
		return d
	
	def get_process_info(self):
		res = subprocess.check_output("ps aux | wc -l", shell=True)
		d = {}
		d["process_num"] = res.decode().rstrip()
		return d
	
	def get_datetime_info(self):
		dt_now = datetime.datetime.now()
		d = {}
		d["year"] = str(dt_now.year)
		d["month"] = str(dt_now.month)
		d["day"] = str(dt_now.day)
		d["hour"] = str(dt_now.hour)
		d["minute"] = str(dt_now.minute)
		d["second"] = str(dt_now.second)
		return d


def transmit_serial_data(com_port):
	si = SystemInfo()
	d = {}
	d["cpu"] = si.fetch_cpu_info()
	d["memory"] = si.fetch_memory_info()
	d["system"] = {}
	d["system"]["process"] = si.get_process_info()
	d["system"]["power status"] = si.get_power_shortage_flag_info()
	d["time"] = si.get_datetime_info()
	data = json.dumps(d)
	
	try:
		tx_data = bytes(data + '\n', "utf-8")
		com_port.write(tx_data)
		print("transmit complete!: {0}".format(datetime.datetime.now()))
	except:
		print("something error")
	
	# 明示的に削除
	del si

def main():
	#transmit_serial_data()

	interval_minutes = 5
	delta_sec = interval_minutes * 60
	prev_time = None
	com_port = serial.Serial("/dev/ttyUSB0", 115200)
	com_port.reset_input_buffer()
	com_port.reset_output_buffer()
	print("Open com port")
	print(com_port)
	
	print("Waiting start time...")
	while not int(datetime.datetime.now().minute) % 5 == 0:
		if not com_port.inWaiting() == 0:
			# for debug
			res = com_port.read(com_port.inWaiting())
			try:
				print("#> " + res.decode("utf-8").replace("\n", "\n#> "))
			except:
				print("RAW#> " + str(res))
		time.sleep(1)
	dt = datetime.datetime.now()
	prev_time = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
	print("OK!", prev_time)
	transmit_serial_data(com_port)


	print("Data will transmit each {0} minutes.".format(interval_minutes))
	try:
		while True:
			delta = datetime.datetime.now() - prev_time
			if delta.seconds >= delta_sec:
				transmit_serial_data(com_port)
				dt = datetime.datetime.now()
				prev_time = datetime.datetime(dt.year, dt.month, dt.day, dt.hour, dt.minute, 0)
				#print("debug -> ", datetime.datetime.now())

			if not com_port.inWaiting() == 0:
				# for debug
				res = com_port.read(com_port.inWaiting())
				try:
					print("#> " + res.decode("utf-8").replace("\n", "\n#> "))
				except:
					print("RAW#> " + str(res))
			time.sleep(1)
	except:
		com_port.close()


if __name__ == "__main__":
	main()
