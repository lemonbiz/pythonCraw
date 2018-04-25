'''
created by yangyinglong at 20180425
对日志文件io
write_log()
read_log()
'''

import copy
import os
import json


formData = {
	'search': '',
	'fid1': '90',
	'fid2': '',
	'fid3': '',
	'time': '',
	'time1': '',
	'page': '2',
	'include': '0'
}


def write_log(form_data, id):
	path = "province/"+str(id)+"/log.json"
	with open(path, 'w', encoding='utf-8') as wfp:
		log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
		json.dump(log, wfp)
		#print('log write success')


def read_log(id):
	'read log as the start of a task'
	path = "province"
	if not os.path.exists(path):
		os.mkdir(path)
	path = "province/"+str(id)
	if not os.path.exists(path):
		os.mkdir(path)
	path = path + '/log.json'
	if not os.path.exists(path):
		with open(path, 'w', encoding='utf-8') as wfp:
			form_data = copy.deepcopy(formData)
			form_data['fid1'] = str(id)
			form_data['time'] = '2013-01-01'
			form_data['time1'] = '2013-03-31'
			form_data['page'] = '1'
			log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
			json.dump(log, wfp)
	with open(path, 'r', encoding='utf-8') as rfp:
		log = json.load(rfp)
		#print(log)
		#print(type(log))
	form_data = json.loads(log)
	return form_data