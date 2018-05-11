'''
created by yangyinglong at 20180510
爬取美团生活服务
'''

from multiprocessing import Process
from multiprocessing import Pool

import os
import re
import json

from download import Downloader
from download import prequest
from download import Database


class_ = {
	'c21171': '丧葬',
	'c20112': '洗涤护理',
	'c20113': '家政服务',
	'c20196': '证件照',
	'c221': '照片冲洗',
	'c20128': '汽车服务',
	'c20454': '搬家',
	'c20110': '宠物服务',
	'c32': '体检/齿科',
	'c20453': '送水站',
	'c20456': '管道疏通',
	'c20474': '居家维修',
	'c20458': '电脑维修',
	'c20460': '手机维修',
	'c20283': '健康服务',
	'c65': '鲜花',
	'c68': '配镜',
	'c67': '母婴亲子',
	'c19': '培训课程',
	'c20057': '服饰鞋包',
	'c20457': '开锁',
	'c235': '商场购物卡',
	'c20093': '婚庆',
	'c21006': '商务服务',
	'c21113': '成人用品',
	'c396': '婚纱摄影'
}


headers_home = {
	'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8',
	'Accept-Encoding': 'gzip, deflate',
	'Cache-Control': 'max-age=0',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Connection': 'keep-alive',
	'Host': 'hz.meituan.com',
	'Upgrade-Insecure-Requests': '1',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

headers_get = {
	'Accept': '*/*',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Connection': 'keep-alive',
	'Host': 'apimobile.meituan.com',
	'Origin': 'http://hz.meituan.com',
	'Referer': 'http://hz.meituan.com/shenghuo/c74b59/pn10/',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}


db = Database()

def compose_url():
	url_list = []
	url_ = 'http://hz.meituan.com/shenghuo/'
	for key_c in class_:
		url = url_ + key_c + '/'
		url_list.append(url)
	return url_list


def get_uuid(url, down):
	html = down(url)
	html = str(down.cookies)
	re_uuid = re.compile(r'uuid=(.*?) ', re.IGNORECASE)
	try:
		uuid = re_uuid.findall(html)[0]	
	except Exception as e:
		print('get uuid error: ', e)
		uuid = None
	return uuid


def get_data(url):
	print(url)
	down = Downloader(headers=headers_home)
	path = 'cache/hz.meituan.com/index.html'
	if os.path.exists(path):
		os.remove(path)
	uuid = get_uuid('http://hz.meituan.com/', down)
	if not uuid:
		return
	data = {}
	type_ = 'c' + url.split('/c')[-1][:-1]
	print(type_)
	cateId = type_[1:]
	areaId = '-1'
	# print(cateId, areaId)
	data['FIRST_LEVEL_DIRECTORY'] = '生活服务'
	data['SECOND_LEVEL_DIRECTORY'] = class_[type_]
	down.headers = headers_get
	index = 0
	while True:
		index = index + 1
		down.headers['Referer'] = url + '/' + 'pn' + str(index) + '/'
		url_get = 'http://apimobile.meituan.com/group/v4/poi/pcsearch/50?uuid='+uuid+'&userid=-1&limit=32&offset='+str((index-1)*32)+'&cateId='+cateId+'&areaId='+areaId
		html = down(url_get)
		try:
			search_result = json.loads(html)['data']['searchResult']
		except Exception as e:
			print('in get_data error ',e)
		if search_result == []:
			print('search_result is None')
			break
		# print(search_result)
		for one_item in search_result:
			data['SHOP_ID'] = one_item['id']
			data['SHOP_PHOTOS'] = one_item['imageUrl']
			data['SHOP_NAME'] = one_item['title']
			data['ADDRESS'] = one_item['address']
			data['RANK_STARS'] = one_item['avgscore']
			data['AVG_PRICE_TITLE'] = one_item['avgprice']
			tuangou = one_item['deals']
			if not tuangou:
				data['GROUP_BUYING_NUMBER'] = 0
				data['GROUP_BUYING'] = None
			else:
				data['GROUP_BUYING_NUMBER'] = len(tuangou)
				taocan = ''
				for one in tuangou:
					taocan = taocan + '价格' + str(one['price']) + ' 门市价' + str(one['value']) + ' 出售' + str(one['sales'])
				data['GROUP_BUYING'] = taocan
			db.insert_into(data)


def down_proc_pool(num=1, list_=None):
	'''进程池的使用'''
	pool = Pool(processes=int(num)) 

	# for i in range(1,10):
	# 	pool.apply_async(run_proc, args=(i, ))
	# print(list_)
	print(len(list_))
	pool.map(get_data, list_)
	print('Waiting for all subprocesses done...')
	pool.close()
	pool.join()
	print('All subprocesses done')



def main():
	url_list = compose_url()
	# print(url_list)
	# while url_dict:
	# 	dic = url_dict.popitem()[-1]
	# 	print(dic)
	down_proc_pool(list_=url_list)


if __name__ == '__main__':
	main()