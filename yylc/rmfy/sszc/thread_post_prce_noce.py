'''
created by yangyinglong at 20180425
多线程爬取http://www.rmfysszc.gov.cn网站
各个省份公告的url,title,court name,release time
'''

from datetime import datetime, timedelta
import threading
import time    

from crwl_prce_inon import downloader
from io_log import read_log

SLEEP_TIME = 1


def threaded_crawler(max_threads=10):
    provinceId = [90, 91, 92, 93, 2589, 95, 3584, 97, 98, 99, 100, 101, 102,
                  103, 104, 105, 106, 107, 108, 9863, 110, 111, 112, 113, 
                  114, 12449, 116, 117, 118, 14003, 13921, 14625]

    def process_queue():
        id = provinceId.pop()
        print(id)
        while True:
            form_data = read_log(id)
            if form_data['time'] == time.strftime('%Y-%m-%d', time.localtime()):
                #print(str(id) + ' had crawled')
                break
            else:
                #print(str(id) + 'is crawling')
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