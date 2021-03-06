#create by yangyinglong at 20180409 for yylc crawl ymfy
# -*- coding: utf-8 -*- 
# coding: utf-8

import urllib.request as urllib2
import urllib.parse as urlparse
import builtwith
import random
import whois
import re
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


old_time = '2018-01-01'
now_time = time.strftime('%Y-%m-%d', time.localtime())
results = {}
listI = [i for i in range(33)]

DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60
SLEEP_TIME = 1
'''
全局变量字典类型result 用来保存各个省份的信息
结构如下:

'''




def addThreeMonth(data):
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


def getZCSSUrlDict(url, pages = 299):
	oldTime = old_time
	ZCSSUrlDict = {}
	while True:
		driver = webdriver.Chrome()
		driver.get(url)
		monthUrl = []
		try:
			driver.find_element_by_id('time').clear()
			driver.find_element_by_id('time1').clear()
			driver.find_element_by_id('time').send_keys(str(oldTime))
			newTime = addThreeMonth(oldTime)
			driver.find_element_by_id('time1').send_keys(str(newTime))
		except:
			pass
		print ('download ' + str(oldTime))
		for page in range(pages):
			nextPages = None
			hrefs = []
			try:
				driver.implicitly_wait(100)
				results = driver.find_elements_by_css_selector('tr.listtr > td > span > a')
				justiceNames = driver.find_elements_by_css_selector('tr.listtr > td > span')

				justiceName = [name.text for name in justiceNames]
				#print len(justiceName)
				a = 0
				putTime = []
				jsNames = []
				for i in range(len(justiceName)):
					if a == 0:
						a = 1
					elif a == 1:
						a = 2
						jsNames.append(justiceName[i])
						#print justiceName[i]
					elif a == 2:
						a = 0
						putTime.append(justiceName[i])

				#print len(jsNames)

				#print len(putTime) 
					
				hrefs = [result.get_attribute('href') for result in results]
				titles = [result.get_attribute('title') for result in results]
				for i in range(len(hrefs)):
					#print titles[i]
					#print jsNames[i]
					#print putTime[i]
					content = [now_time, titles[i], jsNames[i], putTime[i], hrefs[i]]
					#print content
					monthUrl.append(content)
					#time.sleep(3)
					
				nextPages = driver.find_elements_by_css_selector('a.next')
			except:
				pass
			print ('it is ' + str(page))
			if nextPages == None:
				break
			if page == 0:
				nextPage = nextPages[0]
			else:
				try:
					nextPage = nextPages[2]
				except IndexError:
					traceback.print_exc()
					driver.find_element_by_id('time1').click()
					driver.find_element_by_id('time1').send_keys('2000-01-01')
					driver.find_element_by_id('search_sub').click()
					break
			time.sleep(random.randint(0,3))
			try:
				nextPage.click()
			except:
				pass
		try:
			driver.close()
		except:
			pass


		ZCSSUrlDict[str(oldTime).split(' ')[0]] = monthUrl
		oldTime = newTime
		if oldTime > now_time:
			break
	return ZCSSUrlDict



class DiskCache(object):
	"""docstring for DiskCache"""
	def __init__(self, cache_dir='cache',expires=timedelta(days=1)):
		self.cache_dir = cache_dir
		self.expires = expires


	def url_to_path(self, url):
		components = urlparse.urlsplit(url)
		path = components.path
		if not path:
			path = '/index.html'
		elif path.endswith('/'):
			path = path + '/index.html'
		filename = components.netloc + path + components.query
		filename = re.sub('[^/0-9a-zA-Z\-.,;_]', '_', filename)
		filename = '/'.join(segment[:255] for segment in filename.split('/'))
		return os.path.join(self.cache_dir, filename)

	def __getitem__(self, url):
		path = self.url_to_path(url)
		if os.path.exists(path):
			with open(path, 'rb') as fp:
				result, timestamp = pickle.load(fp)
				if self.has_expired(timestamp):
					raise KeyError(url + ' has expires')
				return result
		else:
			raise KeyError(url + ' does not exist')

	def __setitem__(self, url, result):
		path = self.url_to_path(url)
		folder = os.path.dirname(path)
		timestamp = datetime.utcnow()
		data = pickle.dumps((result, timestamp))
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(path, 'wb') as fp:
			fp.write(data)

	def has_expired(self, timestamp):
		return datetime.utcnow() > timestamp + self.expires


class Throttle:
	def __init__(self, delay):
		self.delay = delay
		self.domains = {}

	def wait(self, url):
		domain = urlparse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay > 0 and last_accessed is not None:
			sleep_secs = self.delay - (datetime.now() - 
				last_accessed).seconds
			if sleep_secs > 0:
				time.sleep(sleep_secs)
		self.domains[domain] = datetime.now()


class Downloader:
	def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, opener=None, cache=None):
		socket.setdefaulttimeout(timeout)
		self.throttle = Throttle(delay)
		self.user_agent = user_agent
		self.proxies = proxies
		self.num_retries = num_retries
		self.opener = opener
		self.cache = cache


	def __call__(self, url):
		result = None
		if self.cache:
			try:
				result = self.cache[url]
			except KeyError:
				pass
			else:
				if self.num_retries > 0 and 500 <= result['code'] < 600:
					result = None
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = {'User-agent': self.user_agent}
			result = self.download(url, headers, proxy, self.num_retries)
			if self.cache:
				self.cache[url] = result
		return result['html']

	def download(self, url, headers, proxy, num_retrie, data = None):
		print ('Download:', url)
		request = urllib2.Request(url, data, headers or {})
		opener = self.opener or urllib2.build_opener()
		if proxy:
			proxy_params = {urlparse.urlparse(url).scheme: proxy}
			opener.add_handler(urllib2.ProxyHandler(proxy_params))
		try:
			response = opener.open(request)
			html = response.read()
			code = response.code
		except Exception as e:
			print ('Download error', str(e))
			html = ''
			if hasattr(e, 'code'):
				code = e.code
				if num_retrie > 0 and 500 <= code < 600:
					return _get(url, headers, proxy, num_retrie-1,data)
			else:
				code = None
		return {'html': html, 'code': code}

download = Downloader(cache=DiskCache())

def getProvinceNameUrl(html):
	#<a href="/places/default/index/11">
	webpage_regex = re.compile(r'<td( colspan="2")?><a( target="_blank")? href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
	urls = [url[2] for url in urls]
	tree = lxml.html.fromstring(html)
	provinces = []
	tree = str(tree.cssselect('table.region')[0].text_content())
	provinces = tree.split(' ')
	pro = []
	with open("provinces.txt", 'w') as fp:
		for province in provinces:
			if province != '\r\n' and province != '' and province != '\r\n\r\n':
				#print province
				province = province.replace('\r\n','')
				pro.append(province)
				fp.write(province + '\n')
	#print urls
	hand = re.compile(r'http')
	urlhand = 'http://www.rmfysszc.gov.cn'
	with open('results.txt', 'w') as fp:
		for i in range(35):
			if not re.match(hand ,urls[i]):
				urls[i] = urlhand + urls[i]
			results[i+1] = {'provinceName':pro[i], 'provinceUrl':urls[i], 'noticeUrl':None, 'urlList':None}
			fp.write(pro[i]+':'+urls[i]+'\n')

	return urls, pro, results

def getNoticeUrl(url=None):
	html = download(url).decode('utf-8')
	webpage_regex = re.compile(r'<area shape="rect" coords="184,5,311,29" href="(.*?)"', re.IGNORECASE)
	r = webpage_regex.findall(html)[0]
	#print(r)
	return r

def threadCrawProvince():
	i = listI.pop()
	url = results[i+1]['provinceUrl']
	results[i+1]['noticeUrl'] = getNoticeUrl(url)
	results[i+1]['urlList'] = getZCSSUrlDict(results[i+1]['noticeUrl'])
	filename = 'provinceName/' + str(i) + '.json'
	fileReslut = open(filename, 'w')
	json.dump(results[i+1], fileReslut, ensure_ascii=False)
	fileReslut.close()
	print ('ok')

def main():
	if not os.path.exists("provinceName/"):
		os.mkdir("provinceName/")
	html = download('http://www.rmfysszc.gov.cn').decode('utf-8')
	urls, provinces, _ = getProvinceNameUrl(html)
	print (len(urls), len(provinces), len(results))
	print (results)
	threads = []
	while threads or listI:
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < 1 and listI:
			thread = threading.Thread(target=threadCrawProvince)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)

	'''
	for i in range(1,2):
		url = results[i+1]['provinceUrl']
		results[i+1]['noticeUrl'] = getNoticeUrl(url)
		results[i+1]['urlList'] = getZCSSUrlDict(results[i+1]['noticeUrl'])
		filename = 'provinceName/' + str(i) + '.json'
		fileReslut = open(filename, 'w')
		json.dump(results[i+1], fileReslut, ensure_ascii=False)
		fileReslut.close()
		print 'ok'
	'''

if __name__ == "__main__":
	main()