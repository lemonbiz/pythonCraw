'''
created by yangyinglong at 20180425
多线程爬取公告详情
threaded_download(urlList)
'''

import threading
import time

from down_class import Downloader,Throttle,DiskCache
from html_exct import extract

SLEEP_TIME = 1

def threaded_download(urlList=None, delay=5, cache=None, scrape_callback=None, user_agent='wswp', proxies=None, num_retries=1, max_threads=10, timeout=60):
	url_list = urlList
	#print("len(url_list): ", str(len(url_list)))
	#print('in threead_download')
	D = Downloader(cache=cache, delay=delay, user_agent=user_agent, proxies=proxies, num_retries=num_retries, timeout=timeout)
	def process_down():
		try:
			inf = url_list.pop()
		except IndexError:
			return
		else:
			title = inf[1]
			if '车' not in title:
				if '挖掘机' not in title and '吊塔' not in title:
					url = inf[0]
					source_id = url.split('/')[-1].split('.')[0]
					time_put = inf[2]
					province_name = inf[3]
					html = D(url)
					#print('*************************************')
					#print(html[400:600])				
					if scrape_callback:
						print('in scrap_callback')
						scrape_callback(source_id, html, [title, time_put, province_name])
			else:
				return


	threads = []
	while url_list or threads:
		for thread in threads:
			if not thread.is_alive():
				threads.remove(thread)
		while len(threads) < max_threads and url_list:
			thread = threading.Thread(target=process_down)
			thread.setDaemon(True)
			thread.start()
			threads.append(thread)
		time.sleep(SLEEP_TIME)