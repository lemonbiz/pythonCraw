# -*- coding:utf-8 -*-

import time
import re
from multiprocessing import Pool,cpu_count,Process,Lock,Queue
# import redis
import queue
import threading
import requests
import os

from proxies import ProxyPool

# redis1 = redisConnector()

class Landchinadetail_spider(object):
    def __init__(self):
        self.domain = 'http://hz.meituan.com/'
        self.ProxyPool = ProxyPool(self.domain)
        self.proxy = self.ProxyPool.getproxy()
        self.init_session()
        #logger name
        loggerName =  'process-%s---thread-%s' % (os.getpid(),threading.current_thread().getName())
        # self.logger = clogger(loggerName,'landchina').get_logger()
        # self.logger.info('single_crawler %s start ' % loggerName)

    def init_session(self):
        self.session = requests.session()
        headers = {
                    'Accept': 'application/json',
                    'Accept-Encoding': 'gzip, deflate',
                    'Accept-Language': 'zh-CN,zh;q=0.9',
                    'Connection': 'keep-alive',
                    'Host': 'hz.meituan.com',
                    'Referer':'http://hz.meituan.com/meishi/c11/pn2/',
                    # 'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
                    'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:59.0) Gecko/20100101 Firefox/59.0'
                }
        self.session.headers.update(headers)

    def single_crawler(self, q):
        while True:
            if q.empty():
                break
            else:
                suffix = q.get()
                if suffix:
                    url = self.domain+'/'+suffix
                    text = self.crawl(url)
                    self.writePage(suffix,text)

    # crawl one page
    def crawl(self,url):
        # retry times
        retry = 0
        statusCode_count = 5
        while 1:
            try:
                retry += 1
                response = self.session.get(url, proxies=self.proxy,timeout = 10)
                if response.status_code == 200:
                    # self.logger.info('request '+url+" success")
                    print('request '+url+" success")
                    break
                else:
                    # self.logger.warn("status_code:%s,  url:%s" % (response.status_code,url))
                    print("status_code:%s,  url:%s" % (response.status_code,url))
                    if statusCode_count > 0:
                        old_proxy = self.proxy
                        self.proxy = self.ProxyPool.getproxy()
                        # self.logger.info('change proxy %s to %s' % (old_proxy, self.proxy))
                        statusCode_count -= 1
                    else:
                        # # self.logger.warn('this url:%s is broken' % url)
                        # suffix = url.replace('http://www.landchina.com/','')
                        # if redis1.srem(redisSetName, suffix):
                        #     # self.logger.info("delete broken url %s from Set success" % suffix)
                        #     # redis1.sadd(redisBrokenSetName,suffix)
                        # else:
                        #     self.logger.warn('delete broken url %s from Set failed' % suffix)
                        break
            except Exception as e:
                # self.logger.exception(e)
                print(e)
                # self.logger.warn("======================重试:" + str(retry) + "次")
                print('************重试',str(retry),'次')
                if retry <= 3:
                    pass
                else:
                    old_proxy = self.proxy
                    self.proxy = self.ProxyPool.getproxy()
                    # self.logger.info('change proxy %s to %s' % (old_proxy,self.proxy))
                    retry = 0

        return  response.text

    #write page to file
    def writePage(self,suffix,text):
        filename = re.search(r'recorderguid=.+&sitePath=', suffix).group().replace('recorderguid=', '').replace(
            '&sitePath=', '')
        path = os.path.join(html_path,filename)
        with open(path, 'w', encoding='utf-8') as f:
            f.write(text)
        if redis1.srem(redisSetName, suffix):
            self.logger.info("delete url %s from Set success" % suffix)
        else:
            self.logger.warn('delete url %s from Set failed' % suffix)

#multi threads
def multiThreads(q):
    threads = []
    for i in range(20):
        t = threading.Thread(target=single_crawler,args=(q,))
        threads.append(t)
        t.start()

    for thread in threads:
        thread.join()

def single_crawler(q):
    spider = Landchinadetail_spider()
    spider.single_crawler(q)

# assign tasks to multi process
def assignTasks():
    #all url suffix
    suffixList = redis1.smembers(redisSetName)
    suffixList = [url.decode('utf-8') for url in suffixList]
    print('%d url total' % len(suffixList))
    if len(suffixList)<1:
        return
    # Process Queue
    q = Queue()
    for url in suffixList:
        q.put(url)
    processes = []
    for i in range(cpu_count()):
        process = Process(target=multiThreads, args=(q,))
        processes.append(process)
        process.start()
    for process in processes:
        process.join()


def main():
    #URL = r'http://hz.meituan.com/meishi/api/poi/getPoiList?platform=1&partner=126&originUrl=http%3A%2F%2Fhz.meituan.com%2Fmeishi%2Fc11%2Fpn2%2F&riskLevel=1&optimusCode=1&cityName=%E6%9D%AD%E5%B7%9E&cateId=11&areaId=0&sort=&dinnerCountAttrId=&page=2&userId=0'
    URL =  'http://hz.meituan.com/meishi/api/poi/getPoiList?cityName=杭州&cateId=20004&page=2'
    URL_1 = r'http://hz.meituan.com/meishi/api/poi/getPoiList?uuid=8f79ec4f-da41-4940-8590-2dc14c61274b&platform=1&partner=126&originUrl=http%3A%2F%2Fhz.meituan.com%2Fmeishi%2Fc11%2Fpn2%2F&riskLevel=1&optimusCode=1&cityName=%E6%9D%AD%E5%B7%9E&cateId=11&areaId=0&sort=&dinnerCountAttrId=&page=2&userId=0'
    down = Landchinadetail_spider()
    html = down.crawl(URL_1)
    print(html)


if __name__ == '__main__':
    main()

