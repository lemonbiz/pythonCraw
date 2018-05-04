# -*- coding: utf-8 -*-
"""
Created on Tue Aug  8 09:51:09 2017
@author: caojie
"""
import requests, random
from lxml import etree

def get_proxy_abuyun():
    # 代理服务器
    proxyHost = "http-pro.abuyun.com"
    proxyPort = "9010"

    # 代理隧道验证信息
    proxyUser = "H39A0HL50PCCB02P"
    # proxyUser = "H39A0HL50PCCB02"
    proxyPass = "29148984E07D9E97"

    service_args = [
        "--proxy-type=http",
        "--proxy=%(host)s:%(port)s" % {
            "host": proxyHost,
            "port": proxyPort,
        },
        "--proxy-auth=%(user)s:%(pass)s" % {
            "user": proxyUser,
            "pass": proxyPass,
        },
    ]

    proxyMeta = "%(user)s:%(pass)s@%(host)s:%(port)s" % {
        "host": proxyHost,
        "port": proxyPort,
        "user": proxyUser,
        "pass": proxyPass,
    }
    proxies = {
        "http": proxyMeta,
        "https": proxyMeta,
    }
    #return proxies
    return [proxyMeta]

# get https proxy from https://www.sslproxies.org/
def get_proxy1():
    while True:
        try:
            r = requests.get("https://www.sslproxies.org/",proxies = get_proxy_abuyun(),timeout=10)
            if r.status_code == 200:
                break
            else:
                print('status_code : %s'% r.status_code)
        except Exception as e:
            print(e)
    tree = etree.HTML(r.content)
    ip = tree.xpath("//table[@id='proxylisttable']/tbody/tr/td[1]/text()")
    port = tree.xpath("//table[@id='proxylisttable']/tbody/tr/td[2]/text()")
    urls = []
    for i in range(len(ip)):
        url = ip[i] + ":" + port[i]
        # print(url)
        urls.append(url)
    return urls

def get_proxy2():
    proxies = get_proxy_abuyun()
    print(proxies)
    return proxies

def get_proxy():
    api_url = "http://svip.kuaidaili.com/api/getproxy/?orderid=921444927844924&num=100&b_pcchrome=1&b_pcie=1&b_pcff=1&b_android=1&b_iphone=1&b_ipad=1&protocol=2&method=1&an_an=1&an_ha=1&sp1=1&sp2=1&sort=1&format=json&sep=1"
    r = requests.get(api_url)
    print(r.json())
    ip_list = r.json()['data']['proxy_list']
    return ip_list

# proxy pool
class ProxyPool(object):
    '''A proxypool class to obtain proxy'''

    def __init__(self,domain='https://www.baidu.com'):
        self.pool = set()
        self.domain = domain

    def updateGatherProxy(self):
        '''Use GatherProxy to update proxy pool '''
        self.pool.update(get_proxy())

    def removeproxy(self, proxy):
        '''remove a proxy from pool'''
        if (proxy in self.pool):
            self.pool.remove(proxy)

    def randomchoose(self):
        '''Random Get a proxy from pool'''
        if (self.pool):
            return random.sample(self.pool, 1)[0]
        else:
            self.updateGatherProxy()
            return random.sample(self.pool, 1)[0]

    def getproxy(self):
        '''get a dict format proxy randomly'''
        test_url = self.domain
        proxy = self.randomchoose()
        proxies = {'http': 'http://' + proxy, 'https': 'http://' + proxy}
        print("test:" + str(proxies) + "by request "+ str(test_url))
        # proxies={'https':'http://'+proxy}
        try:
            r = requests.get(test_url , proxies=proxies, timeout=8)
            if (r.status_code == 200):
                print("get new useful proxies" + str(proxies))
                #remove from proxy pool
                self.removeproxy(proxy)
                return proxies
            else:
                self.removeproxy(proxy)
                return self.getproxy()
        except:
            self.removeproxy(proxy)
            return self.getproxy()

    def getallproxies(self):
        '''get all useful proxies'''
        test_url = self.domain
        self.updateGatherProxy()
        usefulProxies = set()
        for proxy in self.pool:
            pass


if __name__ == '__main__':
    proxypool = ProxyPool()
    print("get proxy:" + str(proxypool.getproxy()))
