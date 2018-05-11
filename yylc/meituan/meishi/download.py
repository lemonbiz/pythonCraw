#-*- coding:utf-8 -*-
#created by yangyinglong at 20180503 
'''
下载模块，使用代理IP下载，并将下载过的页面保存在本地文件中，避免重复下载
'''


from datetime import timedelta,datetime

import json
import os
import pymysql
import requests
import random
import re
import socket
import time
import urllib.parse

ERROR_RESPONSE = 0
ERROR_DOWNLOAD = 0
DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60
SLEEP_TIME = 1


request_headers = {
	# 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	# 'Accept-Encoding': 'gzip, deflate',
	# 'Cache-Control': 'max-age=0',
	# 'Accept-Language': 'zh-CN,zh;q=0.9',
	# 'Connection': 'keep-alive',
	# 'Host': 'hz.meituan.com',
	# 'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

# 代理服务器下载url
def prequest(url= "http://ip.chinaz.com/getip.aspx", headers=None, cookies=None, use_proxies=True):

    time.sleep(random.random()/999)

    proxyHost = "http-pro.abuyun.com"
    proxyPort = "9010"

    # 代理隧道验证信息
    proxyUser = "H39A0HL50PCCB02P"
    proxyPass = "29148984E07D9E97"


    proxyMeta = "http://%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }

    # print(proxyMeta)

    if use_proxies == True:
    	proxy_handler = {
    	    "http": proxyMeta,
    	    "https": proxyMeta,
    	}
    	resp = requests.get(url, headers=headers, cookies=cookies, proxies=proxy_handler)
    	res = requests.get(url='http://jsonip.com',proxies=proxy_handler)
    	ip = json.loads(res.text)['ip']
    	print('ip:', ip)
    	resp.raise_for_status()
    	resp.encoding = resp.apparent_encoding
    	if resp.encoding == 'Windows-1254':
    		resp.encoding = 'utf-8'
    else:
    	resp = requests.get(url, headers=headers, cookies=cookies)
    	resp.raise_for_status()
    	resp.encoding = resp.apparent_encoding
    	if resp.encoding == 'Windows-1254':
    		resp.encoding = 'utf-8'
    return resp 




class DiskCache(object):
	"""docstring for DiskCache"""
	def __init__(self, cache_dir='cache',expires=timedelta(days=100)):
		self.cache_dir = cache_dir
		self.expires = expires


	def url_to_path(self, url):
		components = urllib.parse.urlsplit(url)
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
			with open(path, 'r', encoding='utf-8') as fp:
				result= fp.read()
				return result
		else:
			raise KeyError(url + ' does not exist')

	def __setitem__(self, url, result):
		path = self.url_to_path(url)
		folder = os.path.dirname(path)
		timestamp = datetime.utcnow()
		#data = pickle.dumps((result, timestamp))
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(path, 'w', encoding='utf-8') as fp:
			fp.write(result)

	def has_expired(self, timestamp):
		return datetime.utcnow() > timestamp + self.expires


class Throttle:
	def __init__(self, delay):
		self.delay = delay
		self.domains = {}

	def wait(self, url):
		domain = urllib.parse.urlparse(url).netloc
		last_accessed = self.domains.get(domain)

		if self.delay > 0 and last_accessed is not None:
			sleep_secs = self.delay - (datetime.now() - 
				last_accessed).seconds
			if sleep_secs > 0:
				time.sleep(sleep_secs)
		self.domains[domain] = datetime.now()


class Downloader:
	def __init__(self, delay=DEFAULT_DELAY, headers=request_headers, cookies=None, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, opener=None, cache=DiskCache()):
		socket.setdefaulttimeout(timeout)
		self.throttle = Throttle(delay)
		self.user_agent = user_agent
		self.proxies = proxies
		self.num_retries = num_retries
		self.opener = opener
		self.cache = cache
		self.headers = headers
		self.cookies = cookies


	def __call__(self, url):
		result = None
		if self.cache:
			try:
				result = self.cache[url]
			except KeyError:
				pass
			else:
				pass
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			result = self.download(url, self.headers, proxy, self.num_retries, self.cookies)
			# index = 0
			# while True:
			# 	index = 1 + index
				# result = self.download(url, self.headers, proxy, self.num_retries)
			# 	if not(len(result) == 0 or '验证' in result) or index > 8:
			# 		break
			if self.cache:
				self.cache[url] = result
		return result

	def download(self, url, headers, proxy, num_retrie, data = None):
		print ('Download:', url)
		try:
			html = prequest(url=url, headers=self.headers, cookies=self.cookies)
			# self.cookies = html.cookies
			html = html.text
		except Exception as e:
			print ('Download error', str(e))
			html = ''
			if hasattr(e, 'code'):
				if num_retrie > 0 and 500 <= code < 600:
					return _get(url, headers, proxy, num_retrie-1,data)
		return html


class Database():
	"""docstring for Database"""
	def __init__(self):
		self.conn = pymysql.connect(host='122.144.217.112',
							   		port=13306,
							   		user='pc_user4',
		                       		passwd='lldfd9937JJye',
		                       		db='crawler',
		                       		charset='utf8',
		                       		cursorclass = pymysql.cursors.DictCursor #查询结果以字典形式返回
		                       		)
		self.cursor = self.conn.cursor()
		self.user_list = []

	def insert_into(self,data):
		select_sql = 'SELECT * FROM crawler.mt_meishi where SHOP_ID = %d' % data['SHOP_ID']
		if self.select_from(select_sql):
			print('*****data*****has*****already*****existed*****')
			return
		now_time = datetime.now()
		now_time = str(now_time)
		now_time = now_time.split('.')[0]
		data['INBASE_TIME'] = now_time
		data['UPDATE_TIME'] = now_time
		sql_1 = 'INSERT INTO mt_meishi ('
		sql_2 = ') VALUES ('
		for key, value in data.items():
			if data[key] != None:
				sql_1 = sql_1 + key
				# keys.append(key)
				# values.append("'"+str(data[key])+"'")
				if type(data[key]) == str:
					sql_2 = sql_2 + "'" + data[key] + "'"
				else:
					sql_2 = sql_2 + str(data[key])
				sql_1 = sql_1 + ','
				sql_2 = sql_2 + ','
		sql_1 = sql_1[:-1]
		sql_2 = sql_2[:-1]
		sql = sql_1 + sql_2 +')'
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			a = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
			print(a + ' write successful')
		except Exception as e:
			print(e)
			self.conn.rollback()

	def select_from(self,sql=None):
		'''select from table return a list'''
		try:
			self.user_list = []
			# cursor = self.conn.cursor()
			self.cursor.execute(sql)
			rows = self.cursor.fetchall()
			# print(rows)
			for row in rows:
				self.user_list.append(row)
				# print(row['user_id'],row['user_name'])
			return self.user_list
		except Exception as e:
			print('error:', e)
			self.conn.rollback()	

	def update_data(self,sql=None):
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			a = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
			print(a + ' update successful')
		except Exception as e:
			print(e)
			self.conn.rollback()	

	def insert_data(self,sql=None):
		try:
			self.cursor.execute(sql)
			self.conn.commit()
			a = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
			print(a + ' insert comment successful')
		except Exception as e:
			print(e)
			self.conn.rollback()	

	def close(self):
		try:
			self.conn.close()
		except Exception as e:
			print('db close error:', e)
		print('*****db*****close*****')


def main():
	down = Downloader()
	url = 'http://hz.meituan.com/'
	html_home = down(url)
	print(down.cookies)
	print(html_home)
	url = 'http://meituan.com/meishi/5109685/'
	html_uuid = down(url)
	if 'uuid' in html_uuid:
		print('******')
	# a = prequest('https://www.baidu.com')
	# print(a.text)
	# while True:
	# 	print(prequest())
	# d = Downloader()
	# html = d('http://hz.meituan.com/meishi/')
	# print(html)
	# while 1:
	# 	print(prequest().text)
	# 	# print(prequest.url)
	# url = r'http://hz.meituan.com/meishi/c11/pn3/'
	# html_uuid = prequest(url)
	# text = html_uuid.text
	# re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
	# uuid = re_uuid.findall(text)[0]
	# # print(uuid)


	# url = r'http://hz.meituan.com/meishi/api/poi/getPoiList?uuid='+uuid+r'&platform=1&partner=126&originUrl=http%3A%2F%2Fhz.meituan.com%2Fmeishi%2Fc11%2Fpn2%2F&riskLevel=1&optimusCode=1&cityName=%E6%9D%AD%E5%B7%9E&cateId=11&areaId=0&sort=&dinnerCountAttrId=&page=3&userId=0'
	# html = prequest(url)
	# print(html.text)


if __name__ == "__main__":
	main()
