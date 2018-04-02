import urllib2
import builtwith
import whois
import re
import urlparse
from datetime import datetime
import time
import robotparser
import Queue
import csv
import lxml.html

FIELDS = ('area', 'population', 'iso', 'country', 'capital', 'continent', 'tld', 'currency_code', 'currency_name', 'phone', 'postal_code_format', 'postal_code_regex', 'languages', 'neighbours')


def printWebWhois(url):
	return whois.whois(url)

def printWebTechnology(url):
	return builtwith.parse(url)

def download(url, user_agent='wswp',proxy=None, num_retries=2):
	#print 'Downloading:', url
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

def link_crawler(seed_url, link_regex, delay=2, max_depth=2, scrape_callback=None):
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


#http://example.webscraping.com/places/default/index/25
#http://example.webscraping.com/places/default/view/Aland-Islands-2


link_crawler('http://example.webscraping.com', '/places/default/(index|view)', scrape_callback=ScrapeCallback())