import requests
import re
import urllib.request as urllib2
import urllib.parse as urlparse
import builtwith
import random
import whois
from datetime import datetime, timedelta
import time
import csv
import lxml.html
import socket
import os
import pickle
import threading
import sys
from selenium import webdriver
import json
import calendar
import traceback
import copy
from pyquery import PyQuery as pq
from lxml import etree
import pymysql

URL = 'http://www1.rmfysszc.gov.cn/News/handler.aspx'
SLEEP_TIME = 1
ERROR_RESPONSE = 0
ERROR_DOWNLOAD = 0
DEFAULT_AGENT = 'wswp'
DEFAULT_DELAY = 5
DEFAULT_RETRIES = 1
DEFAULT_TIMEOUT = 60
SLEEP_TIME = 1

count = 0
all_file = 0
file_find_id = []

provinceInformain = {
	90:'北京市', 
	91:'天津市', 
	92:'河北省',
	93:'山西省', 
	2589:'内蒙古',
	95:'辽宁省', 
	3584:'吉林省', 
	97:'黑龙江省', 
	98:'上海市', 
	99:'江苏省', 
	100:'浙江省', 
	101:'安徽省', 
	102:'福建省',
	103:'江西省',
	104:'山东省', 
	105:'河南省', 
	106:'湖北省', 
	107:'湖南省', 
	108:'广东省', 
	9863:'广西省',
	110:'海南省', 
	111:'重庆市', 
	112:'四川省', 
	113:'贵州省', 
	114:'云南省', 
	12449:'西藏', 
	116:'陕西省', 
	117:'甘肃省', 
	118:'青海省', 
	14003:'新疆', 
	13921:'宁夏', 
	14625:'新疆建设兵团'
}

formData = {
	'search': '',
	'fid1': '90',
	'fid2': '',
	'fid3': '',
	'time': '',
	'time1': '',
	'page': '2',
	'include': '0'
}

requestHeaders = {
	'Accept':'application/json, text/javascript, */*; q=0.01',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.9',
	'Connection':'keep-alive',
	'Content-Length':'57',
	'Content-Type':'application/x-www-form-urlencoded; charset=UTF-8',
	'Host':'www1.rmfysszc.gov.cn',
	'Origin':'http://www1.rmfysszc.gov.cn',
	'Referer':'http://www1.rmfysszc.gov.cn/News/Pmgg.shtml?fid=90&dh=3&st=0',
	'User-Agent':'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.186 Safari/537.36',
	'X-Requested-With':'XMLHttpRequest'
}

class DiskCache(object):
	"""docstring for DiskCache"""
	def __init__(self, cache_dir='cache',expires=timedelta(days=1)):
		self.cache_dir = cache_dir
		self.expires = expires


	def url_to_path(self, url):
		components = urlparse.urlsplit(url)
		path = components.path
		if not path:
			path = '/index.html'
		elif path.endswith('/'):
			path = path + '/index.html'
		filename = components.netloc + path + components.query
		filename = re.sub('[^/0-9a-zA-Z\-.,;_]', '_', filename)
		filename = '/'.join(segment[:255] for segment in filename.split('/'))
		return os.path.join(self.cache_dir, filename)

	def __getitem__(self, url):
		path = self.url_to_path(url)
		if os.path.exists(path):
			with open(path, 'rb') as fp:
				result= fp.read()
				return result
		else:
			raise KeyError(url + ' does not exist')

	def __setitem__(self, url, result):
		path = self.url_to_path(url)
		folder = os.path.dirname(path)
		timestamp = datetime.utcnow()
		#data = pickle.dumps((result, timestamp))
		if not os.path.exists(folder):
			os.makedirs(folder)
		with open(path, 'w', encoding='utf-8') as fp:
			fp.write(result)

	def has_expired(self, timestamp):
		return datetime.utcnow() > timestamp + self.expires

def write_to_db(data):
    print('in write_to_db')
    print(data)
    t = datetime.now()
    t = str(t)
    t = t.split('.')[0]
    sql = "INSERT INTO fixed_asset_new (resource_id,resource_type,name,address,sell_type,land_type,is_bid,deal_status,source_url,province,city,district,declaration_time,start_price,min_raise_price,cash_deposit,trading_place,announce_num,subject_type,housing_area,land_area,evaluate_price,auction_stage,is_deleted,gmt_created,gmt_modified) VALUES (%d,%d,'%s','%s',%d,%d,%d,%d,'%s','%s','%s','%s','%s',%d,%d,%d,'%s',%d,%d,'%s','%s',%d,%d,%d,'%s','%s')" % (data['resource_id'],data['resource_type'],data['name'],data['address'],2,data['land_type'],0,data['deal_status'],data['source_url'],data['province'],data['city'],data['district'],data['declaration_time'],data['start_price'],data['min_raise_price'],data['cash_deposit'],data['trading_place'],data['announce_num'],data['subject_type'],data['housing_area'],data['land_area'],data['evaluate_price'],data['auction_stage'],data['is_deleted'],t,t)
    print(sql)
    conn = pymysql.connect(host='122.144.217.112',port=13306,user='pc_user4',
    passwd='lldfd9937JJye',db='crawler',charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
        print('successful')
    except Exception as e:
        print(e)
        conn.rollback()
    conn.close()




def change_to_price(a):
    b = ''
    for i in a:
        if i in ['0','1','2','3','4','5','6','7','8','9','万','元','.']:
            b = b + i
    if b == '万元' or b == '元' or len(b) > 20:
        return '0'
    return b


def change_to_area(a):
	b = '0'
	for i in a:
		if i in ['0','1','2','3','4','5','6','7','8','9','.']:
			b = b + i
	return b


count = 0
all_file = 0
file_find_id = []
#scrape_callback(0, html, [title, time_put, province_name])
def extract(source_id,text,meta_data=[]):
    html = etree.HTML(text)
    d = pq(html)
    data = {}
    '''字段名 同 crawler.fixed_asset 表字段'''
    #传入数据
    if meta_data:
    	title = meta_data[0]
        #data['name'] = meta_data[2]
        #data['url'] = meta_data['url']
        #data['declaration_time'] = meta_data[1] #发布日期

    #title = d('#Title > h1').text()
    
    #if title:
        #data['name'] = title
    auction_stage = 0
    if '第一次拍卖' in title:
    	auction_stage = 1
    if '第二次拍卖' in title:
    	auction_stage = 2
    if '第三次拍卖' in title:
    	auction_stage = 3
    if '变卖' in title:
    	auction_stage = 4


    #print('***********************************')
    #print('source_id:%s' % source_id)
    content = d('#Content').text()
    if content:
        global count
        file_find_id.append(source_id)
        count = count + 1
    else:
        content = d('.xmxx_titlemaincontent').text()
    title_content = d('table.xmxx_titlemain').text()
    content = content.replace(' ','').replace('：', '').replace('\n', '').replace('￥','').replace(' ','').replace(':','')

    #print('content:%s'% content)
    #评估价
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    price = re.compile(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价)|(?<=参考))(.*?)(元|万元|万)', re.IGNORECASE)
    ep = price.findall(content)
    evaluate_price = 0
    if len(ep) != 0:
    	for i in ep:
            a = i[1]+i[2]
            a = change_to_price(a)
            if '万' in a:
                a = int(float(a.replace('万','').replace('元',''))*10000*100)
            else:
                a = int(float(a.replace('万','').replace('元',''))*100)
            evaluate_price = evaluate_price + a
    if title_content:
    	content = content + title_content
    	if evaluate_price == 0:
	    	price = re.compile(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价)|(?<=参考))(.*?)(元|万元|万)', re.IGNORECASE)
	    	ep = price.findall(content)
	    	if len(ep) != 0:
	    		for i in ep:
	    			a = i[1]+i[2]
	    			#a = a.replace('价','').replace('（','').replace('标的一','').replace('人民币','').replace('为','').replace('\'','').replace(':','').replace('：','')
	    			a = change_to_price(a)
	    			if '万' in a:
	    				a = int(float(a.replace('万','').replace('元',''))*10000*100)
	    			else:
	    				a = int(float(a.replace('万','').replace('元',''))*100)
	    			evaluate_price = evaluate_price + a
    #print(content)
    #print('评估价:', end=' ')
    #print(evaluate_price)
    #evaluate_price= get_search(re.search(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价))(.*?)(元|万元)',content))
    #print('评估价：%s' % evaluate_price)

    #起拍价
    start_price= get_search(re.search(r'(?<=起拍价)[\d,\.]+?(元|万元)',content))
    if start_price and '万' in start_price:
    	start_price = change_to_price(start_price)
    	start_price = int(float(start_price.replace('万','').replace('元',''))*10000*100)
    elif start_price:
    	start_price = change_to_price(start_price)
    	start_price = int(float(start_price.replace('元',''))*100)
    #print('起拍价:%s' % start_price)

    #保证金
    cash_deposit= get_search(re.search(r'((?<=保证金)|(?<=保证金为))(.*?)(元|万元)',content))
    if cash_deposit != None and len(cash_deposit) > 20:
    	cash_deposit = get_search(re.search(r'(?<=保证金)(.*?)(元|万元)',cash_deposit))
    if cash_deposit and len(cash_deposit) > 10:
    	cash_deposit = None
    if cash_deposit and '万' in cash_deposit:
    	cash_deposit = change_to_price(cash_deposit)
    	cash_deposit = int(float(cash_deposit.replace('万','').replace('元',''))*10000*100)
    elif cash_deposit:
    	cash_deposit = change_to_price(cash_deposit)
    	cash_deposit = int(float(cash_deposit.replace('元',''))*100)
    #print('保证金:%s' % cash_deposit)

    #增价幅度
    min_raise_price = get_search(re.search(r'(?<=增(加|价)幅度)[\d,\.]+?(元|万元)',content))
    if min_raise_price and '万' in min_raise_price:
    	min_raise_price = change_to_price(min_raise_price)
    	min_raise_price = int(float(min_raise_price.replace('万','').replace('元',''))*10000*100)
    elif min_raise_price:
    	min_raise_price = change_to_price(min_raise_price)
    	min_raise_price = int(float(min_raise_price.replace('元',''))*100)
    #print('增价幅度:%s' % min_raise_price)

    #建筑面积
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    area =re.compile(r'((?<=建筑面积约)|(?<=建筑总面积)|(?<=建筑面积)|(?<=建面)|(?<=建筑面积为)|(?<=建筑面积是)|(?<=建筑面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    ha = area.findall(content)
    housing_area = 0
    if len(ha) != 0:
    	for i in ha:
    		a = i[1]+i[2]
    		a = change_to_area(a)
    		housing_area = housing_area + float(a)
    housing_area = str(housing_area) + '平方米'
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))

    #土地面积
    area =re.compile(r'((?<=土地面积约)|(?<=土地面积)|(?<=土地分摊面积)|(?<=宗地面积)|(?<=土地使用权面积)|(?<=土地证载面积)|(?<=土地面积为)|(?<=土地面积是)|(?<=土地面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    la = area.findall(content)
    land_area = 0
    if len(la) != 0:
    	for i in la:
    		b = i[1]+i[2]
    		b = change_to_area(b)
    		land_area = str(land_area) + b
    land_area = str(land_area) + '平方米'
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))
    #print('土地面积:', end=' ')
    #print(land_area)

    #如果土地面积和建筑面积都为0，则查找面积
    if land_area == '0平方米' and housing_area == '0平方米':
        area =re.compile(r'((?<=面积约)|(?<=总面积)|(?<=面积)|(?<=建面)|(?<=面积为)|(?<=面积是)|(?<=面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
        ha = area.findall(content)
        housing_area = 0
        if len(ha) != 0:
            for i in ha:
                a = i[1]+i[2]
                a = change_to_area(a)
                housing_area = housing_area + float(a)
        housing_area = str(housing_area) + '平方米'
    #print('建筑面积:', end=' ')
    #print(housing_area)


    #拍卖地点
    trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)(、)', content))
    if trading_place:
    	trading_place = trading_place[:-2]
    else:
    	trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)((。)|(;))', content))
    	if trading_place != None:
    		trading_place = trading_place[:-1]
    #print('交易地点:%s' % trading_place)

    #建筑性质
    if '营业' in content or '商业' in content or '商铺' in content or '门面房' in content:
    	land_type = 2
    elif '工业' in content or '厂房' in content or '库房' in content or '厂' in content:
    	land_type = 1
    elif '仓库' in content:
    	land_type = 5
    elif '商用' in content:
    	land_type = 4
    elif '商品房' in content or '商服用房' in content:
    	land_type = 7
    elif '住宅' in content:
    	land_type = 3
    elif '别墅' in content:
    	land_type = 8
    elif '办公' in content or '写字' in content:
    	land_type = 6
    else:
    	land_type = 0
    #print('建筑性质:%s' % land_type)


    #城市
    city = get_search(re.search(r'\w+?市',content))
    if city != None:
    	if '受' in city:
    		city = city.split('受')[-1]
    	if '于' in city:
    		city = city.split('于')[-1]
    	if len(city) > 6:
    		city = city[-3:]
    	city = city.replace('在', '')
    	city = city.replace('拍卖标的', '')
    #print('城市:%s' % city)

    #区
    district = get_search(re.search(r'\w+?((区)|(县)|(镇))',content))
    
    if district != None:
	    if '受' in district:
	    	district = district.split('受')[-1]
	    if '于' in district:
	    	district = district.split('于')[-1]
	    if len(district) > 10:
	    	district = district[-8:]
	    district = district.replace('在', '')
	    district = district.replace('拍卖标的', '')
    #print('地区:%s' % district)

    #日期区间
    date = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?\w{1,20}?\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    #print('日期区间:%s' % date)

    #address  从标题title里面提取地址
    address_search = get_search(re.search(r'(关于.+的公告)|(位于.+)',title))
    if address_search:
        address = address_search.replace('关于','').replace('的公告','') \
        .replace('（第二次拍卖）','').replace('（第一次拍卖）','').replace('司法变卖','')
    else:
    	address = title.replace('司法拍卖','').replace('司法变卖','').replace('公告','') \
    	.replace('拍卖','') \
    	.replace('(第三次)','').replace('(第一次)','').replace('(第二次)','')

    address_1 = get_search(re.search(r'((?<=拍卖标的)|(?<=以下标的))(.*?)((室)|(号)|(。)|(，))',content))
    #print(address_1)
    if address_1 and len(address_1) < 10:
    	address_1 = None
    if not address_1:
    	address_1 = get_search(re.search(r'(?<=位于)(.*?)((，)|(。)|(进行))',content))
    if not address_1:
    	address_1 = get_search(re.search(r'(?<=对)(.*?)((，)|(。)|(进行))',content))
    if address_1 and '（' in address_1:
    	address_1 = address_1.split('（')[0]
    if address_1 and '位于' in address_1:
    	address_1 = address_1.split('位于')[1]
    if address_1 and '进行' in address_1:
    	address_1 = address_1.split('进行')[0]
    if address_1:
    	address_1 = address_1.replace('，','').replace('。','').replace('进行','').replace('"','').replace('“','').replace('”','').replace('公开','')
    #print(address_1)
    if address_1 != None and len(address_1) > len(address):
        address_1 = address_1.replace('：','').replace('。','').replace('，','')
        address = address_1
        address = address.replace('进行','').replace('公开','')
    #print('详细地址:%s' % address)

    #data write
    #for i in range(min(len(evaluate_price), len(housing_area))):
    data['resource_id'] = int(source_id)
    data['resource_type'] = 5
    data['name'] = address
    data['province'] = meta_data[2]
    data['address'] = address
    data['land_type'] = land_type
    data['deal_status'] = 0
    data['source_url'] = 'www.rmfysszc.gov.cn'
    data['declaration_time'] = str(meta_data[1]) + ' 00:00:00'
    if start_price == None:
        start_price = 0
    data['start_price'] = start_price
    if min_raise_price == None:
        min_raise_price = 0
    data['min_raise_price'] = min_raise_price
    if cash_deposit == None:
        cash_deposit = 0
    data['cash_deposit'] = cash_deposit
    if trading_place == None:
        trading_place = 0
    data['trading_place'] = trading_place
    data['announce_num'] = int(source_id)
    data['subject_type'] = 1
    data['housing_area'] = housing_area
    data['land_area'] = land_area
    if evaluate_price == None:
        evaluate_price = 0
    data['evaluate_price'] = evaluate_price
    data['auction_stage'] = auction_stage
    data['is_deleted'] = 0
    data['city'] = city
    data['district'] = district
    print('***********************************')
    print(data)
    write_to_db(data)

    #日期
    #date1 = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    #print('日期:%s' % date1)
    
    print('***********************************')

def get_search(search):
    if search:
        return search.group()
    return None


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


class Downloader:
	def __init__(self, delay=DEFAULT_DELAY, user_agent=DEFAULT_AGENT, proxies=None, num_retries=DEFAULT_RETRIES, timeout=DEFAULT_TIMEOUT, opener=None, cache=None):
		socket.setdefaulttimeout(timeout)
		self.throttle = Throttle(delay)
		self.user_agent = user_agent
		self.proxies = proxies
		self.num_retries = num_retries
		self.opener = opener
		self.cache = cache


	def __call__(self, url):
		result = None
		if self.cache:
			try:
				result = self.cache[url]
			except KeyError:
				pass
			else:
				#if self.num_retries > 0 and 500 <= result['code'] < 600:
				result = None
		if result is None:
			self.throttle.wait(url)
			proxy = random.choice(self.proxies) if self.proxies else None
			headers = {'User-agent': self.user_agent}
			result = self.download(url, headers, proxy, self.num_retries)
			if self.cache:
				self.cache[url] = result
		return result

	def download(self, url, headers, proxy, num_retrie, data = None):
		#print ('Download:', url)
		request = urllib2.Request(url, data, headers or {})
		opener = self.opener or urllib2.build_opener()
		if proxy:
			proxy_params = {urlparse.urlparse(url).scheme: proxy}
			opener.add_handler(urllib2.ProxyHandler(proxy_params))
		try:
			response = opener.open(request)
			html = response.read().decode('utf-8')
			code = response.code
		except Exception as e:
			print ('Download error', str(e))
			html = ''
			if hasattr(e, 'code'):
				code = e.code
				if num_retrie > 0 and 500 <= code < 600:
					return _get(url, headers, proxy, num_retrie-1,data)
			else:
				code = None
		return html

def add_one_day(data):
	'get a data as \'2018-08-08\' return a data add one day than it'
	oldTime = datetime.strptime(data,'%Y-%m-%d')
	_,all_2 = calendar.monthrange(int(oldTime.year), int(oldTime.month))
	newTime = oldTime + timedelta(days=1)
	return str(newTime).split(' ')[0]

def add_three_months(data):
	'get a data as \'2018-08-08\' return a data add three months than it'
	oldTime = datetime.strptime(data,'%Y-%m-%d')
	if int(oldTime.day) != 1:
		oldTime = oldTime + timedelta(days=30)
		year = oldTime.year
		month = oldTime.month
		oldTime = str(year) + '-' + str(month) + '-' + str(1)
		oldTime = datetime.strptime(oldTime,'%Y-%m-%d')
	#print oldTime
	for i in range(3):
		_,all_2 = calendar.monthrange(int(oldTime.year), int(oldTime.month))
		#print oldTime.year, oldTime.month
		#print all_2
		newTime = oldTime + timedelta(days=all_2)
		oldTime = newTime
		#print oldTime
	oldTime = oldTime + timedelta(days=-1)
	#print oldTime
	return str(oldTime).split(' ')[0]

def write_log(form_data, id):
	path = "province/"+str(id)+"/log.json"
	with open(path, 'w', encoding='utf-8') as fp:
		log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
		json.dump(log, fp)
		#print('log write success')


def read_log(id):
	'read log as the start of a task'
	path = "province"
	if not os.path.exists(path):
		os.mkdir(path)
	path = "province/"+str(id)
	if not os.path.exists(path):
		os.mkdir(path)
	path = path + '/log.json'
	if not os.path.exists(path):
		with open(path, 'w', encoding='utf-8') as fp:
			form_data = copy.deepcopy(formData)
			form_data['fid1'] = str(id)
			form_data['time'] = '2013-01-01'
			form_data['time1'] = '2013-03-31'
			form_data['page'] = '1'
			log = json.dumps(form_data, sort_keys=True, ensure_ascii=False, indent=4, separators=(',', ': '))
			json.dump(log, fp)
	with open(path, 'r', encoding='utf-8') as fp:
		log = json.load(fp)
		#print(log)
		#print(type(log))
	form_data = json.loads(log)
	return form_data

def get_response(data=formData):
    'post requests to the server with form data and headers, return response, str'
    try:
        response = requests.post(URL, data=data, headers=requestHeaders, timeout=30)
        response.raise_for_status()
        response.encoding = response.apparent_encoding
        content = response.text
        if len(content) < 500:
            return ERROR_DOWNLOAD
        return content
    except:
        return ERROR_RESPONSE

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
				if '挖掘机' not in title:
					url = inf[0]
					source_id = url.split('/')[-1].split('.')[0]
					time_put = inf[2]
					province_name = inf[3]
					html = D(url)
					#print('*************************************')
					#print(html[:100])				
					if scrape_callback:
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

def resolution(content, id=0):
	'resolution response return url, notice title, court name, Release time'
	notice_regex = re.compile(r'<a href=\'(.*?)\' title=\'(.*?)\' target=\'_blank\'>.*?class=\'n_c_l\' title=\'(.*?)\'.*?color: #313131;\'>(.*?)</span>', re.IGNORECASE)
	notice = notice_regex.findall(content)
	return notice

def write_result(form_data, results, id):
	data = form_data['time']
	js = {}
	index = 0
	url_list = []
	for result in results:
		index = index + 1
		#print(result)
		js[index] = {}
		js[index]["爬取时间'"]=time.strftime('%Y-%m-%d', time.localtime())
		js[index]["公告标题"]=result[1]
		js[index]['法院名称']=result[2]
		js[index]['连接地址']=result[0]
		js[index]['发布时间']=result[3]
		js[index]['发布省份']=provinceInformain[id]
		#print(str(result[0]), 'aaaaaaaaaaaa')
		url_list.append([result[0],result[1],result[3],provinceInformain[id]])
	information = json.dumps(js, sort_keys=True, ensure_ascii=False)
	path = 'province/'+str(id)+'/'+form_data['time']+'.json'
	#print(information)
	#print('jijiang threead_download')
	threaded_download(urlList=url_list, cache=DiskCache(), scrape_callback=extract)
	with open(path, 'w', encoding='utf-8') as fp:
		#print('open successed')
		json.dump(information, fp, ensure_ascii=False)
		#print('write successed')

def downloader(form_data=None, id=0):
    page = int(form_data['page'])
    information = []
    while True:
        content = get_response(form_data)
        #time.sleep(random.uniform(0,3))
        if content != ERROR_RESPONSE:
            results = resolution(content, id)
            if results != [] and page < 300:
                for result in results:
                    information.append(result)
                #print(information)
                page = page + 1
                print(page)
                form_data['page'] = str(page)
            else:                
                break
    write_result(form_data, information, id)
    form_data['time'] = add_one_day(form_data['time1'])
    time_add_three_months = add_three_months(form_data['time'])
    if time_add_three_months > time.strftime('%Y-%m-%d', time.localtime()):
        form_data['time1'] = form_data['time']
    else:
        form_data['time1'] = time_add_three_months
    form_data['page'] = str(1)
    write_log(form_data, id)

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
                print(str(id) + ' had crawled')
                break
            else:
                print(str(id) + 'is crawling')
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

def main():
	now_time = time.strftime('%Y-%m-%d', time.localtime())
	old_time = datetime.strptime(now_time,'%Y-%m-%d')
	old_time = old_time + timedelta(days=-1)
	old_time=str(old_time).split(' ')[0]
	#print(old_time, now_time)
	#threaded_crawler()
	
	#r = get_response()
	#n = resolution(r)
	#print(n)
	
	threaded_crawler()



if __name__ == '__main__':
    path = "province"
    if not os.path.exists(path):
        os.mkdir(path)
    main()
	#time.sleep(60*60*24)
