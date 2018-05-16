'''
created by yangyinglong at 20180509
crawl shop comment by request.get(shop_url)
'''

from multiprocessing import Process
from multiprocessing import Pool
from datetime import timedelta,datetime

import json
import random
import re
import requests
import time

from download import prequest
from download import Database
from download import Downloader


# GETUUIDFAIL = 'get_uuid_fail'

headers_shop = {
	'Accept':'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding':'gzip, deflate',
	'Accept-Language':'zh-CN,zh;q=0.9',
	'Cache-Control':'max-age=0',
	'Connection':'keep-alive',
	'Host':'www.meituan.com',
	# 'Referer':'http://hz.meituan.com/meishi/c11/',
	'Upgrade-Insecure-Requests':'1',
	'User-Agent': 'Mozilla/5.0 () AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.139 Safari/537.36'
}

headers_comment = {
	'Accept': 'application/json',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Cache-Control': 'max-age=0',
	'Connection': 'keep-alive',
	'Host': 'www.meituan.com',
	'Referer': 'http://www.meituan.com/meishi/5253775/',
	'User-Agent': 'Mozilla/5.0 () AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

# cookies = {
# 	'uuid': 'd355162228ba46039e5e.1525937334.1.0.0',
# 	'_lxsdk_cuid': '16348f3e84fc8-06dde2674665a5-3b700558-100200-16348f3e84fc8',
# 	'__mta': '43365018.1525937334365.1526007001475.1526007028595.63',
# 	'client-id': 'a823eaef-a480-4069-8c33-e434edbfefc8',
# 	'lat': '30.05025',
# 	'lng':'120.247605',
# 	'_lxsdk':'16348f3e84fc8-06dde2674665a5-3b700558-100200-16348f3e84fc8',
# 	'webloc_geo':'30.3007%2C120.167638%2Cwgs84',
# 	'ci':'50',
# 	' _lxsdk_s': '1634d0b9358-04-0ab-c9c%7C%7C30'
# }

# user_agent_list = [
# 	'Mozilla/5.0(Macintosh;U;IntelMacOSX10_6_8;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
# 	'Mozilla/5.0(Windows;U;WindowsNT6.1;en-us)AppleWebKit/534.50(KHTML,likeGecko)Version/5.1Safari/534.50',
# 	'Mozilla/5.0(compatible;MSIE9.0;WindowsNT6.1;Trident/5.0',
# 	'Mozilla/4.0(compatible;MSIE8.0;WindowsNT6.0;Trident/4.0)',
# 	'Mozilla/5.0(Macintosh;IntelMacOSX10.6;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
# 	'Mozilla/5.0(WindowsNT6.1;rv:2.0.1)Gecko/20100101Firefox/4.0.1',
# 	'Opera/9.80(Macintosh;IntelMacOSX10.6.8;U;en)Presto/2.8.131Version/11.11'
# ]


db = Database()
down = Downloader(headers=headers_shop,cache=None)
sql = "SELECT SHOP_ID, SECOND_LEVEL_DIRECTORY FROM crawler.mt_meishi where LABEL_IS_CCRAWLED = 0 and FIRST_LEVEL_DIRECTORY = '美食' limit 50;"


def update_shop_by_id(data):
	sql_hand = 'update crawler.mt_meishi set '
	sql_end = ' where SHOP_ID = ' + str(data['SHOP_ID']) + ';'
	sql_body = ''
	for key, value in data.items():
		if data[key] == None:
			continue
		elif type(data[key]) == int:
			sql_body = sql_body + key + ' = ' + str(data[key]) + ', '
		else:
			sql_body = sql_body + key + ' = ' + "'" + str(data[key]) + "'" + ', '
	sql_final = sql_hand + sql_body[:-2] + sql_end
	db.update_data(sql_final)


def insert_shop_comments(NETIZEN_EVALUTION_list, id):
	if NETIZEN_EVALUTION_list:
		for one_evalution in NETIZEN_EVALUTION_list:
			now_time = datetime.now()
			now_time = str(now_time)
			now_time = now_time.split('.')[0]
			sql_insert = "insert into mt_shop_comments (SHOP_ID, NETIZEN_EVALUTION, INBASE_TIME) value ('%s', '%s', '%s')" % (id, one_evalution, now_time)
			db.insert_data(sql_insert)

def extrace_label_list(review_labels_list):
	REVIEW_COUNT = ''
	try:
		for label in review_labels_list:
			REVIEW_COUNT = REVIEW_COUNT + label['tag'] + ':' + str(label['count']) + '; '
		return REVIEW_COUNT
	except Exception as e:
		return 'extrace_label_list error: ' + str(e)


def extrace_comments_list(comments_list, num):
	# NETIZEN_EVALUTION = ''
	limit = int(num) + 1
	return_list = []
	for comment in comments_list:
		one_limit = 'No.' + str(limit) + '{'
		limit += 1
		try:
			if comment['commentTime']:
				one_limit = one_limit + ' 点评时间: ' + comment['commentTime'] + ';'
			if comment['userName']:
				one_limit = one_limit + ' 网友昵称: ' + comment['userName'] + ';'
			if comment['star']:
				one_limit = one_limit + ' 综合评分: ' + str(comment['star']) + ';'
			if comment['comment']:
				one_limit = one_limit + ' 评价内容: '  + comment['comment'].replace("'",'') + ';'
			if comment['userUrl']:
				one_limit = one_limit + ' 网友头像: ' + comment['userUrl'] + ';'
			if comment['picUrls']:
				one_limit = one_limit + '评论图片:{'
				index = 1
				for pic in comment['picUrls']:
					one_limit = one_limit + 'pic' + str(index) + ': ' + pic['url'] + ' '
					index = index + 1
				one_limit = one_limit + '};'
			if comment['merchantComment']:
				one_limit = one_limit + '商家回复: ' + comment['merchantComment'] + ';'
			if comment['dealEndtime']:
				one_limit = one_limit + '商家回复时间: ' + comment['dealEndtime'] + ';'
			highpoints = re.compile(u'[\U00010000-\U0010ffff]')  
			highpoints = re.compile(u'[\uD800-\uDBFF][\uDC00-\uDFFF]')
			one_limit = highpoints.sub(u'??', one_limit)
			one_limit = one_limit + '} '
			return_list.append(one_limit)
			# NETIZEN_EVALUTION = NETIZEN_EVALUTION + one_limit
		except Exception as e:
			print('extrace_comments_list error: ', e)
	return return_list

def get_shop_information(url_shop):
	'''return shop uuid, phone, openTime, isWifi'''
	down.headers = headers_shop
	html_shop = down(url_shop)
	# print(html[100:200])
	is_wifi = 0
	if 'wifi' in html_shop or '无线' in html_shop or 'WIFI' in html_shop or 'Wifi' in html_shop:
		is_wifi = 1
	re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
	re_phone = re.compile(r'"phone":"(.*?)"',re.IGNORECASE)
	re_openTime = re.compile(r'"openTime":"(.*?)"')
	try:
		uuid = re_uuid.findall(html_shop)[0]	
	except Exception as e:
		print('get uuid error: ', e)
		return None, None, None, None
	try:
		phone = re_phone.findall(html_shop)[0]
	except Exception as e:
		print('get phone error: ', e)
		phone = None
	try:
		open_time = re_openTime.findall(html_shop)[0]
	except Exception as e:
		print('get open_time error: ', e)
		open_time = None
	return uuid, phone, open_time, is_wifi


def get_shop_comment(uuid, id):
	down.headers = headers_comment
	down.headers['Referer'] = 'http://www.meituan.com/meishi/' + str(id) + '/'
	num = 0
	REVIEW_COUNT = ''  #评论标签和数量
	NETIZEN_EVALUTION_list = [] #网友点评
	url_comment = r'http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid='+uuid+'&platform=1&partner=126&originUrl=http%3A%2F%2Fwww.meituan.com%2Fmeishi%2F93999737%2F&riskLevel=1&optimusCode=1&id='+str(id)+'&userId=&offset='+str(num)+'&pageSize=10&sortType=1'
	time.sleep(random.randint(1,5) + random.uniform(10, 20)/4)
	html_comment = down(url_comment)
	#解析第一页的标签
	try:
		review_labels_list = []
		review_labels_list = json.loads(html_comment)['data']['tags']
	except Exception as e:
		print('in get_shop_comment review_labels_list error: ',e)
		return None,None
	if review_labels_list:
		REVIEW_COUNT = extrace_label_list(review_labels_list)
	#解析第一页的网友评论
	try:
		comments_list = []
		comments_list = json.loads(html_comment)['data']['comments']
	except Exception as e:
		print('in get_shop_comment comments_list error: ',e)
		return REVIEW_COUNT,None
	if not comments_list:
		return REVIEW_COUNT, None
	NETIZEN_EVALUTION_list_1 = extrace_comments_list(comments_list, num)
	if NETIZEN_EVALUTION_list_1:
		for one_evalution in NETIZEN_EVALUTION_list_1:
			NETIZEN_EVALUTION_list.append(one_evalution)
	while True:
		num += 10
		url_comment = r'http://www.meituan.com/meishi/api/poi/getMerchantComment?uuid='+uuid+'&platform=1&partner=126&originUrl=http%3A%2F%2Fwww.meituan.com%2Fmeishi%2F93999737%2F&riskLevel=1&optimusCode=1&id='+str(id)+'&userId=&offset='+str(num)+'&pageSize=10&sortType=1'
		print('it is ' + str(num) + 'st pages')
		time.sleep(random.randint(1,3) + random.uniform(10, 20)/4)
		html_comment = down(url_comment)
		try:
			comments_list = []
			comments_list = json.loads(html_comment)['data']['comments']
		except Exception as e:
			print('in json.loads(html_comment) ' + str(num) + ' error', e)
			break
		if num > 300:
			break
		if not comments_list:
			break
		NETIZEN_EVALUTION_list_2 = extrace_comments_list(comments_list, num)
		if NETIZEN_EVALUTION_list_2:
			for one_evalution in NETIZEN_EVALUTION_list_2:
				NETIZEN_EVALUTION_list.append(one_evalution)
	return REVIEW_COUNT, NETIZEN_EVALUTION_list


def down_comment(id):
	url_source = 'http://www.meituan.com/meishi/'
	data = {}
	data['SHOP_ID'] = id
	url_shop = url_source + str(id) + '/'
	# uuid, phone, open_time, is_wifi
	data['LABEL_IS_CCRAWLED'] = 2
	update_shop_by_id(data)
	uuid, data['TELEPHONE'], data['BUSINESS_TIME'], data['WIFI'] = get_shop_information(url_shop)
	if uuid:
		data['LABEL_IS_CCRAWLED'] = 3
		update_shop_by_id(data)
		data['REVIEW_COUNT'], NETIZEN_EVALUTION_list = get_shop_comment(uuid, id)
		print(data)
	else:
		print('****down_comment_by_id_main****in sleep****')
		time.sleep(random.randint(100,500) + random.uniform(10, 20)/4)
		return
	now_time = datetime.now()
	now_time = str(now_time)
	now_time = now_time.split('.')[0]
	data['UPDATE_TIME'] = now_time
	update_shop_by_id(data)
	insert_shop_comments(NETIZEN_EVALUTION_list, id)
	time.sleep(random.randint(3000, 6000)/99)


def down_proc_pool(num=10, list_=None):
	'''进程池的使用'''
	pool = Pool(processes=int(num)) 

	# for i in range(1,10):
	# 	pool.apply_async(run_proc, args=(i, ))
	# print(list_)
	print(len(list_))
	pool.map(down_comment, list_)
	print('Waiting for all subprocesses done...')
	pool.close()
	pool.join()
	print('All subprocesses done')


def down_comment_by_id_main():
	id_list = ['']
	# print(id_list)
	index = 0
	while True:
		NETIZEN_EVALUTION_list = []
		try:
			id_dict = db.select_from(sql)
			if id_dict == [] and index < 100:
				print('all shop had been ergodiced')
				db.update_data("update crawler.mt_meishi set LABEL_IS_CCRAWLED = 0 where LABEL_IS_CCRAWLED = 2;")
				index += 1
				continue
			elif index > 100:
				break
			for id in id_dict:
				id_list.append(id['SHOP_ID'])
		except Exception as e:
			print('select error ', e)
			time.sleep(60)
			continue
		down_proc_pool(10,id_list)
		# data = {}
		# id = id_list.pop()
		# data['SHOP_ID'] = id
		# url_shop = url_source + str(id) + '/'
		# # uuid, phone, open_time, is_wifi
		# data['LABEL_IS_CCRAWLED'] = 2
		# update_shop_by_id(data)
		# uuid, data['TELEPHONE'], data['BUSINESS_TIME'], data['WIFI'] = get_shop_information(url_shop)
		# if uuid:
		# 	data['LABEL_IS_CCRAWLED'] = 3
		# 	update_shop_by_id(data)
		# 	data['REVIEW_COUNT'], NETIZEN_EVALUTION_list = get_shop_comment(uuid, id)
		# 	print(data)
		# else:
		# 	print('****down_comment_by_id_main****in sleep****')
		# 	time.sleep(random.randint(100,500) + random.uniform(10, 20)/4)
		# 	continue
		# now_time = datetime.now()
		# now_time = str(now_time)
		# now_time = now_time.split('.')[0]
		# data['UPDATE_TIME'] = now_time
		# update_shop_by_id(data)
		# insert_shop_comments(NETIZEN_EVALUTION_list, id)
		# time.sleep(random.randint(3000, 6000)/99)



if __name__ == '__main__':
	down_comment_by_id_main()





'''
try:
	id_list = ['5253775']
	# id_dict = db.select_from(sql)
	# for id in id_dict:
	# 	id_list.append(id['SHOP_ID'])
except Exception as e:
	print('select error ', e)
url_source = 'http://www.meituan.com/meishi/'
re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
index = 0
while id_list and index < 2:
	index += 1
	# id = id_list.pop(random.randint(0,9))
	id = '1693422'
	# print(id)
	print('***'+ str(id)+ '***crawl****', end='')
	url_shop = url_source + str(id) + '/'
	# request = prequest(url=url_shop,headers=headers).text
	time.sleep(random.uniform(30,40)/5.1)
	request = down(url_shop)
	if 'uuid' in request:
		try:
			uuid = re_uuid.findall(request)[0]	
		except Exception as e:
			print('get uuid error: ', e)
			uuid = 'None'
		print('right***uuid=\t'+uuid)
	else:
		print('error')
		# time.sleep(random.uniform(100,200)/50)

'''