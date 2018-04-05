#create by yangyinglong at 20180406 for crawl javascript 

import json
import string
from downloader import Downloader

template_url = 'http://example.webscraping.com/'\
	'places/ajax/search.json?&search_term={}&page_size=10&page={}'

D = Downloader()
countries = set()

for letter in string.lowercase:
	page = 0
	while True:
		html = D(template_url.format(letter, page))
		try:
			ajax = json.loads(html)
		except ValueError as e:
			print e
			ajax = None
		else:
			for record in ajax['records']:
				countries.add(record['country'])
		page += 1
		if ajax is None or page >= ajax['num_pages']:
			break

open('countries.txt', 'w').write('\n'.join(sorted(countries)))


'''
url = 'http://example.webscraping.com/places/ajax/search.json?&search_term=.&page_size=10000&page=0'
#使用.匹配所有的字符,查询所有的数据以json格式返回,原因是 后端在处理时不会检测参数，他们认为请求来自web页面
'''