#-*- coding:utf-8 -*-
'''
created by yangyinglong at 20180507
从数据库中读取各个商铺的id然后爬取具体的营业时间WiFi评价等
'''

from datetime import timedelta,datetime

import json
import re
import time

from download import Downloader
from download import Database



headers = {
	'Accept': 'application/json',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-US,en;q=0.5',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'www.meituan.com',
	'Referer': 'http://www.meituan.com/meishi/5253775/',
	'User-Agent': 'Mozilla/5.0 (X11; Linux ppc64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.3359.117 Safari/537.36'
}

headers_home = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'en-US,en;q=0.5',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'www.meituan.com',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (X11; Linux ppc64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/33.0.3359.117 Safari/537.36'
}

HOMEURL = 'http://www.meituan.com/meishi/'

db = Database()
down = Downloader(headers=headers_home)


def get_ten_limit_id():
	try:
		sql = "SELECT SHOP_ID FROM crawler.mt_meishi where 'LABEL_IS_CCRAWLED' = 0 LIMIT 10;"
		id_list = db.select_from(sql)
		return id_list
	except Exception as e:
		print('in get_ten_limit_id error: ', e)
		return None


def get_uuid_phone_openTime_wifi(url):
	html = down(url)
	is_wifi = 0
	if 'wifi' in html or '无线' in html or 'WIFI' in html or 'Wifi' in html:
		is_wifi = 1
	re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
	re_phone = re.compile(r'"phone":"(.*?)"',re.IGNORECASE)
	re_openTime = re.compile(r'"openTime":"(.*?)"')
	try:
		uuid = re_uuid.findall(html)[0]	
	except Exception as e:
		print('get uuid error: ', e)
		uuid = None
	try:
		phone = re_phone.findall(html)[0]
	except Exception as e:
		print('get phone error: ', e)
		phone = None
	try:
		open_time = re_openTime.findall(html)[0]
	except Exception as e:
		print('get open_time error: ', e)
		open_time = None
	return uuid, phone, open_time


def extract(evalution):
	one_limit = ''
	if evalution['commentTime']:
		one_limit = one_limit + ' 点评时间: ' + evalution['commentTime'] + ';'
	if evalution['userName']:
		one_limit = one_limit + ' 网友昵称: ' + evalution['userName'] + ';'
	if evalution['star']:
		one_limit = one_limit + ' 综合评分: ' + str(evalution['star']) + ';'
	if evalution['comment']:
		one_limit = one_limit + ' 评价内容: '  + evalution['comment'] + ';'
	if evalution['userUrl']:
		one_limit = one_limit + ' 网友头像: ' + evalution['userUrl'] + ';'
	if evalution['picUrls']:
		one_limit = one_limit + '评论图片:{'
		index = 1
		for pic in evalution['picUrls']:
			one_limit = one_limit + 'pic' + str(index) + ': ' + pic['url'] + ' '
			index = index + 1
		one_limit = one_limit + '};'
	if evalution['merchantComment']:
		one_limit = one_limit + '商家回复: ' + evalution['merchantComment'] + ';'
	if evalution['dealEndtime']:
		one_limit = one_limit + '商家回复时间: ' + evalution['dealEndtime'] + ';'
	try:
		highpoints = re.compile(u'[\U00010000-\U0010ffff]')  
	except re.error:
		highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')  
	   
	one_limit = highpoints.sub(u'??', one_limit)
	return one_limit + '   '


def get_review(uuid, id, url):
	num = 0
	count = 0
	index = 0
	url_review = r'http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid='+uuid+'&platform=1&partner=126&originUrl=http://www.meituan.com/meishi/'+id+'/&riskLevel=1&optimusCode=1&id='+id+'&userId=&offset='+str(num)+'&pageSize=10&sortType=1'
	down.headers['Referer'] = url
	html = down(url_review)
	review_label_list = None
	try:
		review_label_list = json.loads(html)['data']['tags']
	except Exception as e:
		print('in get_review review_label_list error: ',e)
	REVIEW_COUNT = ''
	for label in review_label_list:
		REVIEW_COUNT = REVIEW_COUNT + label['tag'] + ':' + str(label['count']) + '; '
	# print(REVIEW_COUNT)
	try:
		metizen_evalution_list = json.loads(html)['data']['comments']
	except Exception as e:
		print('in get_review metizen_evalution_list error: ',e)
	NETIZEN_EVALUTION = ''
	count = count + len(metizen_evalution_list)
	for evalution in metizen_evalution_list:
		one_limit = extract(evalution)
		index += 1
		NETIZEN_EVALUTION = NETIZEN_EVALUTION + 'No.'+ str(index) + ':' + one_limit
	while True:
		num = num + 10
		url_review = r'http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid='+uuid+'&platform=1&partner=126&originUrl=http://www.meituan.com/meishi/'+id+'/&riskLevel=1&optimusCode=1&id='+id+'&userId=&offset='+str(num)+'&pageSize=10&sortType=1'
		html = down(url_review)
		try:
			metizen_evalution_list = json.loads(html)['data']['comments']
		except Exception as e:
			print('in get_review metizen_evalution_list error: ',e)
			break
		try:
			count = count + len(metizen_evalution_list)
		except:
			break
		for evalution in metizen_evalution_list:
			one_limit = extract(evalution)
			index += 1
			NETIZEN_EVALUTION = NETIZEN_EVALUTION + 'No.'+ str(index) + ':' + one_limit
	return REVIEW_COUNT, NETIZEN_EVALUTION


def down_info_by_id(one_id=None):
	if not one_id:
		return None
	data = {}
	id = one_id['SHOP_ID']
	url = HOMEURL + id + '/'
	uuid, data['TELEPHONE'], data['BUSINESS_TIME'] = get_uuid_phone_openTime_wifi(url)
	if uuid:
		data['REVIEW_COUNT'], data['NETIZEN_EVALUTION'] = get_review(uuid, id, url)
	else:
		print('uuid is None')
		return	
	limit = ''
	sql = ''
	now_time = datetime.now()
	now_time = str(now_time)
	now_time = now_time.split('.')[0]
	data['UPDATE_TIME'] = now_time
	data['LABEL_IS_CCRAWLED'] = 1
	try:
		for key, value in data.items():
			if data[key] != None:
				if type(data[key]) == int:
					limit = limit + str(key) + "=" + str(data[key]) + ","
				else:
					limit = limit + str(key) + "=" + "'" + data[key] + "'" + ","
		limit = limit[:-1]
		sql = 'update crawler.mt_meishi set ' + limit + ' where SHOP_ID = ' + id
		db.update_data(sql)
	except Exception as e:
		print(e)
		pass
	

def main():
	while True:
		id_list = get_ten_limit_id()
		if not id_list:
			break
		for id in id_list:
			down_info_by_id(id)
			


if __name__ == '__main__':
	main()

