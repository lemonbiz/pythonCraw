import urllib2
import builtwith
import whois
import re
import urlparse
from datetime import datetime
import time
import robotparser
import Queue

def printWebWhois(url):
	return whois.whois(url)

def printWebTechnology(url):
	return builtwith.parse(url)

def download(url, user_agent='wswp',proxy=None, num_retries=2):
	print 'Downloading:', url
	#time.sleep(1)
	headers = {'User-agent': user_agent}
	request = urllib2.Request(url, headers = headers)

	opener = urllib2.build_opener()
	if proxy:
		proxy_params = {urlparse.urlparse(url).scheme: proxy}
		opener.add_handler(urllib2.ProxyHandler(proxy_params))
	try:
		response = opener.open(request)
		html = response.read()
		code = response.code
	except urllib2.URLError as e:
		print 'Download error:', e.reason
		html = None
		if hasattr(e, 'code'):
			code = e.code
			if num_retries > 0 and 500 <= e.code < 600:
				# recursively retry 5xx HTTP errrors
				return download(url, user_agent, proxy, num_retries-1)
		else:
			code = None
	return html

#print download('http://example.webscraping.com')

def crawl_sitemap(url):
	sitemap = download(url)
	#print sitemap
	links = re.findall('<loc>(.*?)</loc>', sitemap)
	print links
	for link in links:
		html = download(link)


#crawl_sitemap('http://example.webscraping.com/sitemap.xml')

def link_crawler(seed_url, link_regex, delay=2, max_depth=2):
	max_depth = 2
	crawl_queue = [seed_url]
	seen = {seed_url: 0}
	#seen = set(crawl_queue)
	throttle = Throttle(delay)
	


	while crawl_queue:
		url = crawl_queue.pop()
		throttle.wait(url)
		html = download(url)

		depth = seen[url]
		if depth != max_depth:
			for link in get_links(html):
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

#http://example.webscraping.com/places/default/index/25
#http://example.webscraping.com/places/default/view/Aland-Islands-2


link_crawler('http://example.webscraping.com', '/places/default/(index|view)')