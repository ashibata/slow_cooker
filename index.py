from bottle import route, run, request, HTTPResponse, template, static_file
from collections import OrderedDict
import paste
import json
import subprocess
import sys
from temp import Temp

TARGET_TEMPARATURE = 59

@route('/static/:path#.+#', name='static')
def static(path):
	return static_file(path, root='static')

@route('/')
def root():
	data = temp.chart_data() 
	return template("index", labels=data['labels'], datasets=data['datasets'])

def main():
	global temp
	if sys.argv[1] is None:
		raise ValueError('Need to set target temparature as float')
	temp = Temp(float(sys.argv[1]))
	run(server='paste', host='0.0.0.0', port=8080, debug=True, reloader=False)

if __name__ == '__main__':
	main()

