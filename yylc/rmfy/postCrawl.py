import requests
import re
import urllib.request as urllib2
import urllib.parse as urlparse
import builtwith
import random
import whois
from datetime import datetime, timedelta
import time
import csv
import lxml.html
import socket
import os
import pickle
import threading
import sys
from selenium import webdriver
import json
import calendar
import traceback
import copy

URL = 'http://www1.rmfysszc.gov.cn/News/handler.aspx'
SLEEP_TIME = 1
ERROR_RESPONSE = 0
ERROR_DOWNLOAD = 0


provinceInformain = {
	90:'北京市', 
	91:'天津市', 
	92:'河北省',
	93:'山西省', 
	2589:'内蒙古',
	95:'辽宁省', 
	3584:'吉林省', 
	97:'黑龙江省', 
	98:'上海市', 
	99:'江苏省', 
	100:'浙江省', 
	101:'安徽省', 
	102:'福建省',
	103:'江西省',
	104:'山东省', 
	105:'河南省', 
	106:'湖北省', 
	107:'湖南省', 
	108:'广东省', 
	9863:'广西省',
	110:'海南省', 
	111:'重庆市', 
	112:'四川省', 
	113:'贵州省', 
	114:'云南省', 
	12449:'西藏', 
	116:'陕西省', 
	117:'甘肃省', 
	118:'青海省', 
	14003:'新疆', 
	13921:'宁夏', 
	14625:'新疆建设兵团'
}

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

requestHeaders = {
	'Accept':'application/json, text/javascript, */*; q=0.01',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.9',
	'Connection':'keep-alive',
	'Content-Length':'57',
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Host':'www1.rmfysszc.gov.cn',
	'Origin':'http://www1.rmfysszc.gov.cn',
	'Referer':'http://www1.rmfysszc.gov.cn/News/Pmgg.shtml?fid=90&dh=3&st=0',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
	'X-Requested-With':'XMLHttpRequest'
}

def add_one_day(data):
	'get a data as \'2018-08-08\' return a data add one day than it'
	oldTime = datetime.strptime(data,'%Y-%m-%d')
	_,all_2 = calendar.monthrange(int(oldTime.year), int(oldTime.month))
	newTime = oldTime + timedelta(days=1)
	return str(newTime).split(' ')[0]

def add_three_months(data):
	'get a data as \'2018-08-08\' return a data add three months than it'
	oldTime = datetime.strptime(data,'%Y-%m-%d')
	if int(oldTime.day) != 1:
		oldTime = oldTime + timedelta(days=30)
		year = oldTime.year
		month = oldTime.month
		oldTime = str(year) + '-' + str(month) + '-' + str(1)
		oldTime = datetime.strptime(oldTime,'%Y-%m-%d')
	#print oldTime
	for i in range(3):
		_,all_2 = calendar.monthrange(int(oldTime.year), int(oldTime.month))
		#print oldTime.year, oldTime.month
		#print all_2
		newTime = oldTime + timedelta(days=all_2)
		oldTime = newTime
		#print oldTime
	oldTime = oldTime + timedelta(days=-1)
	#print oldTime
	return str(oldTime).split(' ')[0]

def write_log(form_data, id):
	path = "province/"+str(id)+"/log.json"
	with open(path, 'w', encoding='utf-8') as fp:
		log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
		json.dump(log, fp)
		print('log write success')


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
		with open(path, 'w', encoding='utf-8') as fp:
			form_data = copy.deepcopy(formData)
			form_data['fid1'] = str(id)
			form_data['time'] = '2013-01-01'
			form_data['time1'] = '2013-03-31'
			form_data['page'] = '1'
			log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
			json.dump(log, fp)
	with open(path, 'r', encoding='utf-8') as fp:
		log = json.load(fp)
		#print(log)
		#print(type(log))
	form_data = json.loads(log)
	return form_data

def get_response(data=formData):
	'post requests to the server with form data and headers, return response, str'
	try:
		#print(data)
		print('111')
		response = requests.post(URL, data=data, headers=requestHeaders, timeout=30)
		response.raise_for_status()
		print('222')
		response.encoding = response.apparent_encoding
		#print(response.encoding)
		content = response.text
		#print(type(content))
		#print(len(content))
		#print(content)
		print('response success')
		return content
	except:
		return ERROR_RESPONSE

def resolution(content, id=0):
	'resolution response return url, notice title, court name, Release time'
	notice_regex = re.compile(r'<a href=\'(.*?)\' title=\'(.*?)\' target=\'_blank\'>.*?class=\'n_c_l\' title=\'(.*?)\'.*?color: #313131;\'>(.*?)</span>', re.IGNORECASE)
	notice = notice_regex.findall(content)
	return notice

def write_result(form_data, results, id):
	data = form_data['time']
	js = {}
	index = 0
	for result in results:
		index = index + 1
		print(result)
		js[index] = {}
		js[index]["爬取时间'"]=time.strftime('%Y-%m-%d', time.localtime())
		js[index]["公告标题"]=result[1]
		js[index]['法院名称']=result[2]
		js[index]['连接地址']=result[0]
		js[index]['发布时间']=result[3]
		js[index]['发布省份']=provinceInformain[id]
	information = json.dumps(js, sort_keys=True, ensure_ascii=False)
	path = 'province/'+str(id)+'/'+form_data['time']+'.json'
	print(information)
	with open(path, 'w', encoding='utf-8') as fp:
		print('open successed')
		json.dump(information, fp, ensure_ascii=False)
		print('write successed')

def downloader(form_data=None, id=0):
	page = int(form_data['page'])
	information = []
	while True:
		content = get_response(form_data)
		time.sleep(random.uniform(0,3))
		if content != ERROR_RESPONSE:
			results = resolution(content, id)
			if results != []:
				for result in results:
					information.append(result)
				print(information)
				page = page + 1
				form_data['page'] = str(page)
			else:
				print(str(id) + 'write_result')
				write_result(form_data, information, id)
				break
	form_data['time'] = add_one_day(form_data['time1'])
	time_add_three_months = add_three_months(form_data['time'])
	if time_add_three_months > time.strftime('%Y-%m-%d', time.localtime()):
		form_data['time1'] = form_data['time']
	else:
		form_data['time1'] = time_add_three_months
	form_data['page'] = str(1)
	write_log(form_data, id)

def threaded_crawler(max_threads=3):
	provinceId = [90, 91, 92, 93, 2589, 95, 3584, 97, 98, 99, 100, 101, 102,
			 	  103, 104, 105, 106, 107, 108, 9863, 110, 111, 112, 113, 
			 	  114, 12449, 116, 117, 118, 14003, 13921, 14625]	

	def process_queue():
		id = provinceId.pop()
		print(id)
		while True:
			form_data = read_log(id)
			if form_data['time'] > time.strftime('%Y-%m-%d', time.localtime()):
				break
			else:
				downloader(form_data, id)


	threads = []
	while provinceId or threads:
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < max_threads and provinceId:
			thread = threading.Thread(target=process_queue)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
		time.sleep(SLEEP_TIME)

def main():
	now_time = time.strftime('%Y-%m-%d', time.localtime())
	old_time = datetime.strptime(now_time,'%Y-%m-%d')
	old_time = old_time + timedelta(days=-1)
	old_time=str(old_time).split(' ')[0]
	#print(old_time, now_time)
	#threaded_crawler()
	
	#r = get_response()
	#n = resolution(r)
	#print(n)
	
	threaded_crawler()



if __name__ == '__main__':
	main()
