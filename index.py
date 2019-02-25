from bottle import route, run, request, HTTPResponse, template, static_file
from collections import OrderedDict
import json
import subprocess
import threading
from temp import Temp

@route('/static/:path#.+#', name='static')
def static(path):
	return static_file(path, root='static')

TARGET_TEMPARATURE = 65

@route('/')
def root():
	data = temp.chart_data() 
	return template("index", labels=data['labels'], datasets=data['datasets'])

def main():
	try:
		print('Temp control Start')
		temp = Temp(TARGET_TEMPARATURE)
		print('Server Start')
		run(host='0.0.0.0', port=8080, debug=True, reloader=True)
	except:
		import traceback
		traceback.print_exc()

if __name__ == '__main__':
	main()

