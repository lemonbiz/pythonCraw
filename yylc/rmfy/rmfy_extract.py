# -*- coding:utf-8 -*-
from pyquery import PyQuery as pq
from lxml import etree
import os
import re
#from src.rmfysszc.params import extract_path

'''
参数:
source_id:网站文件唯一id,
text:html 文本
meta_data: dict类型, 网页url,省份,发布日期等
'''

count = 0
all_file = 0
file_find_id = []
def extract(source_id,text,meta_data=[]):
    html = etree.HTML(text)
    d = pq(html)
    data = {}
    '''字段名 同 crawler.fixed_asset 表字段'''
    #传入数据
    if meta_data:
        data['province'] = meta_data['province']
        data['url'] = meta_data['url']
        data['declaration_time'] = meta_data['url'] #发布日期

    title = d('#Title > h1').text()
    if title:
        data['name'] = title
    print('source_id:%s' % source_id)
    content = d('#Content').text()
    if content:
        global count
        file_find_id.append(source_id)
        count = count + 1
    else:
        content = d('.xmxx_titlemaincontent').text()
        if content:
            global count
            file_find_id.append(source_id)
            count = count + 1
    print(content)

    #print('content:%s'% content)
    #评估价
    evaluate_price= get_search(re.search(r'(?<=评估价：)[\d,\.]+?(元|万元)',content))
    print('评估价：%s' % evaluate_price)
    #起拍价
    start_price= get_search(re.search(r'(?<=起拍价：)[\d,\.]+?(元|万元)',content))
    print('起拍价:%s' % start_price)
    #保证金
    cash_deposit= get_search(re.search(r'(?<=保证金：)[\d,\.]+?(元|万元)',content))
    print('保证金:%s' % cash_deposit)
    #增价幅度
    min_raise_price = get_search(re.search(r'(?<=增(加|价)幅度：)[\d,\.]+?(元|万元)',content))
    print('增价幅度:%s' % min_raise_price)
    #建筑面积
    construction_area = get_search(re.search(r'((?<=建筑面积)|(?<=建筑面积(：|为|是)))[\d,\.]+?(平方米|㎡|公顷)',content))
    print('建筑面积:%s' % construction_area)

    #城市
    city   = get_search(re.search(r'\w+?市',content))
    print(city)
    #区
    district    = get_search(re.search(r'\w+?区',content))
    print(district)

    #日期区间
    date = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?\w{1,20}?\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    print('日期区间:%s' % date)

    #address  从标题title里面提取地址
    address_search = get_search(re.search(r'(关于.+的公告)|(位于.+)',title))
    if address_search:
        address = address_search.replace('关于','').replace('的公告','')
        print('address:%s' % address)
    else:
        print('address__title:%s' % title)
    print(data)

    #日期
    date1 = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    print('日期:%s' % date1)
    print('***********************************')
    print('***********************************')

def get_search(search):
    if search:
        return search.group()
    return None



if __name__ == '__main__':
    id = 39450
    extract_path = 'cache/www.rmfysszc.gov.cn/statichtml/rm_xmdetail/'
    #path = path + str(id)+'.shtml'
    #with open(path, 'r', encoding='utf-8') as fp:
    #    text = fp.read()
    #source_id = str(id)
    #extract(source_id, text)

    
    files = [os.path.join(extract_path,file) for root,dirs,files in os.walk(extract_path) for file in files]
    print(files)
    for file in files:
        with open(file,'r',encoding = 'utf-8') as f:
            text = f.read()
        source_id = os.path.basename(file).split('.')[0]
        extract(source_id,text)
        all_file = all_file + 1
    print(count)
    print(all_file)
    print(count/all_file)
    print(file_find_id)
    
