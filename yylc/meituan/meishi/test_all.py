#测试脚本


from datetime import timedelta,datetime

import os
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


# 代理服务器
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

    #print(proxyMeta)


    if use_proxies == True:
        proxy_handler = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        resp = requests.get(url, headers=headers, cookies=cookies, proxies=proxy_handler)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
    else:
        resp = requests.get(url, headers=headers, cookies=cookies)
        resp.raise_for_status()
        resp.encoding = resp.apparent_encoding
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
	def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, opener=None, cache=DiskCache()):
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
				pass
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = {'User-agent': self.user_agent}
			result = self.download(url, headers, proxy, self.num_retries)
			if self.cache:
				self.cache[url] = result
		return result

	def download(self, url, headers, proxy, num_retrie, data = None):
		print ('Download:', url)
		try:
			html = prequest(url).text
		except Exception as e:
			print ('Download error', str(e))
			html = ''
			if hasattr(e, 'code'):
				if num_retrie > 0 and 500 <= code < 600:
					return _get(url, headers, proxy, num_retrie-1,data)
		return html


def main():
	# a = prequest('https://www.baidu.com')
	# print(a.text)
	# while True:
	# 	print(prequest())
	d = Downloader()
	html = d('http://hz.meituan.com/meishi/')
	print(html)


if __name__ == "__main__":
	main()
