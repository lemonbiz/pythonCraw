#create by yangyinglong at 20180404 for learn threads crawl
import urllib2
import csv
import sys
from datetime import datetime, timedelta
import time
import socket
import urlparse
import re
import threading

DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60
SLEEP_TIME = 1

class DiskCache(object):
	"""docstring for DiskCache"""
	def __init__(self, cache_dir='cache',expires=timedelta(days=30)):
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
		print 'Download:', url
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
			print 'Download error', str(e)
			html = ''
			if hasattr(e, 'code'):
				code = e.code
				if num_retrie > 0 and 500 <= code < 600:
					return _get(url, headers, proxy, num_retrie-1,data)
			else:
				code = None
		return {'html': html, 'code': code}

def threaded_crawler(seed_url, link_regex=None, delay=5, cache=None, user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=60):
	D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)
	crawl_queue = [seed_url]
	seen = set([seed_url])
	#print seen
	#print 'hello world' + link_regex

	def process_queue():
		while True:
			try:
				url = crawl_queue.pop()
			except IndexError:
				break
			else:
				links = []
				html = D(url)
				if link_regex:
					try:
						for link in get_links(html):
							if re.match(link_regex, link):
								links.append(link)
						#print links
					except Exception as e:
						print 'Error in callback for: {}: {}'.format(url,e)
					else:
						if links is not None:
							for link in links:
								link = urlparse.urljoin(seed_url, link)
								if link not in seen:
									seen.add(link)
									#print seen
									crawl_queue.append(link)
									#print crawl_queue
	threads = []
	while threads or crawl_queue:
		#print 'hello world2'
		for thread in threads:
			#print 'hello world3'
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < max_threads and crawl_queue:
			thread = threading.Thread(target=process_queue)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
		time.sleep(SLEEP_TIME)

def get_links(html):
	#<a href="/places/default/index/11">
	webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
	#print urls
	return urls


def main(max_threads=5,num_urls=200):
	seed_url = 'http://example.webscraping.com'
	link_regex = '/places/default/(index|view)'
	threaded_crawler(seed_url=seed_url, link_regex=link_regex)





if __name__ == "__main__":
	main()