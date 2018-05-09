'''
created by yangyinglong at 20180508 
爬取美团丽人
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
	'c76': '美容美体',
	'c74': '美发',
	'c75': '美甲美瞳',
	'c20423': '医学美容',
	'c220': '瑜伽舞蹈',
	'c20422': '瘦身纤体',
	'c20419': '韩式定妆',
	'c20421': '祛痘',
	'c20420': '纹身',
	'c20418': '化妆品'
}

area = {
	'b59': '西湖区',
	'b57': '拱墅区',
	'b5225': '萧山区',
	'b58': '江干区',
	'b60': '滨江区',
	'b2779': '余杭区',
	'b55': '上城区',
	'b2780': '临安市',
	'b2781': '富阳区',
	'b56': '下城区',
	'b2783': '桐庐县',
	'b2782': '建德市',
	'b2784': '淳安县'
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
	'Referer': 'http://hz.meituan.com/jiankangliren/c74b59/pn10/',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}

# url = 'http://hz.meituan.com/jiankangliren/c74b59/'
# html = prequest(url=url, headers=headers_home)
# html = html.text
# re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
# try:
# 	uuid = re_uuid.findall(html)[0]	
# except Exception as e:
# 	print('get uuid error: ', e)
# 	uuid = None
# num = 9*32
# url_get = 'http://apimobile.meituan.com/group/v4/poi/pcsearch/50?uuid='+uuid+'&userid=-1&limit=32&offset='+str(num)+'&cateId=74&areaId=59'
# html = prequest(url=url_get, headers=headers_get).text
# print(html)


# down = Downloader(headers=headers_home)
db = Database()


def compose_url():
	url_dict = {}
	url_ = 'http://hz.meituan.com/jiankangliren/'
	for key_c in class_:
		url_dict[class_[key_c]] = []
		for key_a in area:
			url = url_ + key_c + key_a + '/'
			url_dict[class_[key_c]].append(url)
	return url_dict


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
	down = Downloader(headers=headers_home)
	path = 'cache/hz.meituan.com/index.html'
	if os.path.exists(path):
		os.remove(path)
	uuid = get_uuid('http://hz.meituan.com/', down)
	if not uuid:
		return
	data = {}
	type_ = 'c' + url.split('/c')[-1].split('b')[0]
	cateId = type_[1:]
	areaId = url.split(cateId)[-1][1:-1]
	print(cateId, areaId)
	data['FIRST_LEVEL_DIRECTORY'] = '丽人'
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
	url_dict = compose_url()
	while url_dict:
		dic = url_dict.popitem()[-1]
		down_proc_pool(list_=dic)

	


if __name__ == '__main__':
	main()
	# pass