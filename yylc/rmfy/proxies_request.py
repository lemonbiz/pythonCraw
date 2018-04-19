import requests
import time

# 代理服务器
def prequest(url= "http://ip.chinaz.com/getip.aspx", headers=None, cookies=None, use_proxies=True):

    time.sleep(2)

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


    if use_proxies == True:
        proxy_handler = {
            "http": proxyMeta,
            "https": proxyMeta,
        }
        resp = requests.get(url, headers=headers, cookies=cookies, proxies=proxy_handler)
    else:
        resp = requests.get(url, headers=headers, cookies=cookies)
    return resp


# print(prequest().text)