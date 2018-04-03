#create by yangyinglong at 20180403 for learn crawl

import urllib2
import builtwith
import random
import whois
import re
import urlparse
from datetime import datetime, timedelta
import time
import robotparser
import Queue
import csv
import lxml.html
import socket
import os
import pickle
from pymongo import MongoClient

DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')

class MongoCache(object):
	def __init__(self, client=None, expires=timedelta(days=30)):
		self.client = MongoClient('127.0.0.1',27017) if client is None else client
		self.db = self.client.cache
		self.db.webpage.create_index('timestamp', expireAfterSeconds=expires.total_seconds())
	def __getitem__(self, url):
		record = self.db.webpage.find_one({'_id': url})
		if record:
			return record['result']
		else:
			raise KeyError(url + ' does not exist')
		
	def __setitem__(self, url, result):
		record = {'result': result, 'timestamp': datetime.utcnow()}
		self.db.webpage.update({'_id':url}, {'$set':record}, upsert=True)

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
def link_crawler(seed_url, link_regex, delay=2, max_depth=10, scrape_callback=None, cache=None):
	crawl_queue = [seed_url]
	seen = {seed_url: 0}
	#seen = set(crawl_queue)
	throttle = Throttle(delay)
	


	while crawl_queue:
		url = crawl_queue.pop()
		throttle.wait(url)
		#html = download(url)
		D = Downloader(delay=delay, cache=cache)
		html = D(url)


		depth = seen[url]
		links = []
		if scrape_callback:
			links.extend(scrape_callback(url, html) or [])


		if depth != max_depth:
			if link_regex:
				# filter for links matching our regular expression
				links.extend(link for link in get_links(html) if re.match(link_regex, link))
			for link in links:
				if re.match(link_regex, link):
					link = urlparse.urljoin(seed_url, link)
					#print link
					if link not in seen:
						seen[link] = depth + 1
						crawl_queue.append(link)
						#print crawl_queue


def get_links(html):
	#<a href="/places/default/index/11">
	webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
	#print urls
	return urls

class ScrapeCallback:
    def __init__(self):
        self.writer = csv.writer(open('countries.csv', 'w'))
        self.fields = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')
        self.writer.writerow(self.fields)

    def __call__(self, url, html):
        if re.search('/places/default/view/', url):
            tree = lxml.html.fromstring(html)
            row = []
            for field in self.fields:
                row.append(tree.cssselect('table > tr#places_{}__row > td.w2p_fw'.format(field))[0].text_content())
            self.writer.writerow(row)


def scrape_callback(url, html):
	if re.search('/places/default/view/', url):
		tree = lxml.html.fromstring(html)
		'''
		for field in FIELDS:
			print field
			information = tree.cssselect('table > tr#places_%s__row > td.w2p_fw' % field)[0].text_content()
			print information
		'''

		try:
			row = [tree.cssselect('table > tr#places_%s__row > td.w2p_fw' % field)[0].text_content() for field in FIELDS]
		except Exception as e:
			raise
		
		print url
		print row

#download = Downloader()
#print download('https://www.baidu.com')

if __name__ == "__main__":
	link_crawler('http://example.webscraping.com', '/places/default/(index|view)', max_depth=2, cache=MongoCache())