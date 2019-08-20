from time import sleep
import datetime
import glob
import json
import os
import RPi.GPIO as GPIO
import threading
import time

class Temp:
	device_files = glob.glob('/sys/bus/w1/devices/*/w1_slave')
	device_file = ""
	temp_json   = {}
	running     = True
	GPIO_RELAY  = 21

	def __init__(self, target_temp):
		if target_temp < 1 or 100.0 < 100.0:
			raise ValueError('Target temp is too low or too high!')
		if len(Temp.device_files) == 0:
			raise EnvironmentError("Thermo sensor device is not found.")
		if len(Temp.device_files) > 1:
			raise EnvironmentError("Too many thermo sensor devices found. Set only 1 device.")
		Temp.device_file = Temp.device_files[0]
		Temp.target_temp = target_temp
		GPIO.setmode(GPIO.BCM)
		GPIO.setup(Temp.GPIO_RELAY, GPIO.OUT)
		os.system('modprobe w1-gpio')
		os.system('modprobe w1-therm')
		Temp.lock   = threading.Lock()
		Temp.thread = threading.Thread(target=self.keep_control_temp)
		Temp.thread.daemon = True
		Temp.thread.start()

	def read_device_temp(self):
		with open(Temp.device_file, 'r') as (f):
			lines = f.readlines()
			return lines

	def read_temp(self):
		lines = self.read_device_temp()
		while lines[0].strip()[-3:] != 'YES':
			sleep(0.2)
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

	def keep_control_temp(self):
		hist = []
		prev = 0
		t = 0
		try:
			while Temp.running:
				now = datetime.datetime.now().strftime('%Y/%m/%d %H:%M:%S')
				with Temp.lock:
					Temp.temp_json[now] = self.read_temp()
				hist.insert(0, Temp.temp_json[now])
				if len(hist) > 7:
					hist.pop()
				pg = self.p(Temp.temp_json[now], Temp.target_temp, 3)
				ig = self.i(hist, Temp.target_temp, 0.01)
				power = pg + ig
				if power > 0:
					power += 0.1
				prev = Temp.temp_json[now]
				print t, Temp.temp_json[now], power
				self.output(power)
				t += 10
				print(now, Temp.target_temp, Temp.temp_json[now])
		finally:
			self.stop_control_temp()
			print'Temp control_temp method finally worked'

	def stop_control_temp(self):
		Temp.running = False
		GPIO.cleanup()
		print 'Temp stop_control_temp method worked'

	def output(self, power):
		if power > 1:
			power = 1
		on = power * 10
		off = (1 - power) * 10
		if on > 0:
			GPIO.output(Temp.GPIO_RELAY, GPIO.HIGH)
			time.sleep(on)
		if off > 0:
			GPIO.output(Temp.GPIO_RELAY, GPIO.LOW)
			time.sleep(off)

	def p(self, temp, target, kp):
		d = target - temp
		if d < 0:
			return 0
		power = d / target * kp
		return power

	def i(self, hist, target, ki):
		s = 0
		for i in range(len(hist)-1):
			d1 = target - hist[i]
			d2 = target - hist[i+1]
			s += (d1 + d2) / 2 * ki
		return s
