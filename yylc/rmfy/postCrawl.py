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
        data['province'] = meta_data[2]
        #data['url'] = meta_data['url']
        data['declaration_time'] = meta_data[1] #发布日期

    #title = d('#Title > h1').text()
    title = meta_data[0]
    if title:
        data['name'] = title
    print('***********************************')
    print('source_id:%s' % source_id)
    content = d('#Content').text()
    if content:
        global count
        file_find_id.append(source_id)
        count = count + 1
    else:
        content = d('.xmxx_titlemaincontent').text()
        title_content = d('table.xmxx_titlemain').text()
        if title_content:
        	content = content + title_content
    content = content.replace(' ','').replace('：', '').replace('\n', '').replace('￥','')
    print(content)

    #print('content:%s'% content)
    #评估价
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    price = re.compile(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价)|(?<=参考))(.*?)(元|万元|万)', re.IGNORECASE)
    ep = price.findall(content)
    evaluate_price = []
    if len(ep) != 0:
    	for i in ep:
    		a = i[1]+i[2]
    		a = a.replace('价','').replace('（','').replace('标的一','').replace('人民币','').replace('为','')
    		if a != '万元' and a != '元' and a not in evaluate_price:
    			evaluate_price.append(a)

    print('评估价:', end=' ')
    print(evaluate_price)
    #evaluate_price= get_search(re.search(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价))(.*?)(元|万元)',content))
    #print('评估价：%s' % evaluate_price)

    #起拍价
    start_price= get_search(re.search(r'(?<=起拍价)[\d,\.]+?(元|万元)',content))
    print('起拍价:%s' % start_price)

    #保证金
    cash_deposit= get_search(re.search(r'((?<=保证金)|(?<=保证金为))(.*?)(元|万元)',content))
    if cash_deposit != None and len(cash_deposit) > 20:
    	cash_deposit = ash_deposit= get_search(re.search(r'(?<=保证金)(.*?)(元|万元)',cash_deposit))
    if cash_deposit:
    	cash_deposit = cash_deposit.replace('为','').replace('人民币','')
    print('保证金:%s' % cash_deposit)

    #增价幅度
    min_raise_price = get_search(re.search(r'(?<=增(加|价)幅度)[\d,\.]+?(元|万元)',content))
    print('增价幅度:%s' % min_raise_price)

    #建筑面积
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    area =re.compile(r'((?<=建筑面积约)|(?<=建筑面积)|(?<=建面)|(?<=建筑面积为)|(?<=建筑面积是)|(?<=建筑面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    ha = area.findall(content)
    housing_area = []
    if len(ha) != 0:
    	for i in ha:
    		a = i[1]+i[2]
    		a = a.replace('约','').replace('为','').replace('是','').replace('共计','')
    		if a not in housing_area:
    			housing_area.append(a)
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))
    print('建筑面积:', end=' ')
    print(housing_area)
    #土地面积
    area =re.compile(r'((?<=土地面积约)|(?<=土地面积)|(?<=土地证载面积)|(?<=土地面积为)|(?<=土地面积是)|(?<=土地面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    la = area.findall(content)
    land_area = []
    if len(la) != 0:
    	for i in ca:
    		a = i[1]+i[2]
    		a = a.replace('约','').replace('为','').replace('是','').replace('共计','')
    		if a not in land_area:
    			land_area.append(a)
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))
    print('土地面积:', end=' ')
    print(land_area)


    #拍卖地点
    trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)(、)', content))
    if trading_place:
    	trading_place = trading_place[:-2]
    else:
    	trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)((。)|(;))', content))
    	if trading_place != None:
    		trading_place = trading_place[:-1]
    print('交易地点:%s' % trading_place)

    #建筑性质
    if '营业' in content or '商业' in content or '商铺' in content or '门面房' in content:
    	land_type = '商铺'
    elif '工业' in content or '厂房' in content or '库房' in content or '厂' in content:
    	land_type = '厂房'
    elif '仓库' in content:
    	land_type = '仓库'
    elif '商用' in content:
    	land_type = '商业'
    elif '商品房' in content or '商服用房' in content:
    	land_type = '商住房'
    elif '住宅' in content:
    	land_type = '住宅'
    elif '别墅' in content:
    	land_type = '别墅'
    else:
    	land_type = '未知'
    print('建筑性质:%s' % land_type)


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
    print('城市:%s' % city)

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
    print('地区:%s' % district)

    #日期区间
    date = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?\w{1,20}?\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    print('日期区间:%s' % date)

    #address  从标题title里面提取地址
    address_search = get_search(re.search(r'(关于.+的公告)|(位于.+)',title))
    if address_search:
        address = address_search.replace('关于','').replace('的公告','') \
        .replace('（第二次拍卖）','').replace('（第一次拍卖）','').replace('司法变卖','')
    else:
    	address = title.replace('司法拍卖','').replace('司法变卖','').replace('公告','') \
    	.replace('拍卖','') \
    	.replace('(第三次)','').replace('(第一次)','').replace('(第二次)','')
    	if len(address) < 8:
    		address = get_search(re.search(r'((?<=拍卖标的)|(?<=以下标的))[\d,\.]+?(室|号)',content))
    		if address is None:
    			address = get_search(re.search(r'((?<=拍卖标的)|(?<=以下标的))[\d,\.]+?(，|。)',content))
    		else:
    			address = get_search(re.search(r'((?<=对)|(?<=以下标的))[\d,\.]+?(进行)',content))
    if address:
    	address = address.replace('：','').replace('。','').replace('，','')
    print('详细地址:%s' % address)
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
		#print(data)
		#print('111')
		response = requests.post(URL, data=data, headers=requestHeaders, timeout=30)
		response.raise_for_status()
		#print('222')
		response.encoding = response.apparent_encoding
		#print(response.encoding)
		content = response.text
		#print(type(content))
		#print(len(content))
		#print(content)
		#print('response success')
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
					print('*************************************')
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
		time.sleep(random.uniform(0,3))
		if content != ERROR_RESPONSE:
			results = resolution(content, id)
			if results != []:
				for result in results:
					information.append(result)
				#print(information)
				page = page + 1
				form_data['page'] = str(page)
			else:
				#print(str(id) + 'write_result')
				write_result(form_data, information, id)
				break
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
		#print(id)
		while True:
			form_data = read_log(id)
			if form_data['time'] == time.strftime('%Y-%m-%d', time.localtime()):
				break
			else:
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
	main()
	time.sleep(60*60*24)
