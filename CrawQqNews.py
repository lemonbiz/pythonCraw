import requests
import os
import time
from lxml import etree
import traceback


def get_url_text(url):
    try:
        kw = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; WOW64)'}
        r = requests.get(url, timeout=30, headers=kw)
        r.raise_for_status()
        r.encoding = r.apparent_encoding
        return r.text
    except:
        return 'wrong!!'

def get_new_html(url):
    text = get_url_text(url)
    selector = etree.HTML(text)
    content = selector.xpath('//div[@class="Q-tpWrap"]/a[@target="_blank"]/@href')
    print(len(content))
    return content

def get_html_content(html):
    text = get_url_text(html)
    selector = etree.HTML(text)    
    root = '//home//work//news//'
    try:
        title = selector.xpath('//head/title/text()')[0].replace("-腾讯网","").replace("_腾讯网","").replace("_新闻","")
        content = selector.xpath('//p[@class="one-p"]/text()')
        if len(content) == 0:
            content = selector.xpath('//p[@class="text"]/text()')
        print(title)
        path = root + title + '.txt'
        if not os.path.exists(root):
            os.mkdir(root)
        if not os.path.exists(path):
            with open(path, 'w') as f:
                f.write(title + '\n')
                for i in content:
                    f.write(i + '\n')
                f.close()
                print("write success")
    except:
        traceback.print_exc()

    
def get_new_content(url):
    i = 1
    for html in get_new_html(url):
        time.sleep(2)
        print('News ' + str(i))
        i = i + 1
        print(html)
        get_html_content(html)
        
        
        
        
    
    
    


def main():
    url = 'https://news.qq.com'
    get_new_content(url)
    
    


main()
