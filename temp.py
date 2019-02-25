import datetime
import json
import os
import RPi.GPIO as GPIO
import threading
from time import sleep

class Temp:
	DEVICE_FILE = '/sys/bus/w1/devices/28-051680d0f7ff/w1_slave'
	target_temp = 0
	temp_json   = {}

	def __init__(self, target_temp):
		Temp.target_temp = target_temp
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(21, GPIO.OUT)
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		Temp.lock   = threading.Lock()
		Temp.thread = threading.Thread(target=self.control_temp)
		Temp.thread.daemon = True
		Temp.thread.start()

	def __del__(self):
		GPIO.cleanup()
		print'Temp class destructor worked'

	def read_device_temp(self):
		with open(Temp.DEVICE_FILE, 'r') as (f):
			lines = f.readlines()
			return lines

	def read_temp(self):
		lines = self.read_device_temp()
		while lines[0].strip()[-3:] != 'YES':
			sleep(100)
			lines = slef.read_device_temp()
		equals_pos = lines[1].find('t=')
		if equals_pos != -1:
			temp_string = lines[1][equals_pos + 2:]
			temp_c = float(temp_string) / 1000.0
			return temp_c

	def chart_data(self):
		data = {'labels': [],'datasets': []}
		for key,val in sorted(Temp.temp_json.iteritems()):
			# removing u prefix of string
			data['labels'].append(key.encode("ascii","replace"))
			data['datasets'].append(val)
		return data

	def control_temp(self):
		if Temp.target_temp == 0:
			raise ValueError('Target temp is not set!')
		try:
			while True:
				now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
				with Temp.lock:
					Temp.temp_json[now] = self.read_temp()
				if Temp.temp_json[now] < Temp.target_temp:
					GPIO.output(21, GPIO.HIGH)
					low_high = 'GPIO.HIGH'
				else:
					GPIO.output(21, GPIO.LOW)
					low_high = 'GPIO.LOW'
				print(now, Temp.target_temp, Temp.temp_json[now], low_high)
		except (KeyboardInterrupt, SystemExit):
			print'Temp control_temp method execpt worked'
		finally:
			GPIO.cleanup()
			print'Temp control_temp method finally worked'
