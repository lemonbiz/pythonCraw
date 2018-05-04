'''
created by yangyinglong at 20180503 
从数据库中读取美食各个类别，然后具体下载各个店铺的信息
'''

from multiprocessing import Process
from multiprocessing import Pool

import json
import pymysql
import re
import threading
import time

from download import Downloader
from download import Database

class_code = {
	'11': '蛋糕甜点',
	'17': '火锅',
	'40': '自助餐',
	'36': '小吃快餐',
	'28': '日韩料理',
	'35': '西餐',
	'395': '聚餐宴请',
	'54': '烧烤烤肉',
	'20003': '东北菜',
	'55': '川湘菜',
	'56': '江浙菜',
	'20004': '香锅烤鱼',
	'57': '粤菜',
	'400': '中式烧烤/烤串',
	'58': '西北菜',
	'41': '咖啡酒吧',
	'59': '京菜鲁菜',
	'60': '云贵菜',
	'62': '东南亚菜',
	'63': '海鲜',
	'217': '素食',
	'227': '台湾/客家菜',
	'228': '创意菜',
	'229': '汤/粥/炖菜',
	'232': '蒙餐',
	'233': '新疆菜',
	'24': '其他美食'
}

request_headers = {
	'Accept': 'application/json',
	'Accept-Encoding': 'gzip, deflate',
	'Accept-Language': 'zh-CN,zh;q=0.9',
	'Connection': 'keep-alive',
	'Host': 'hz.meituan.com',
	'Referer': 'http://hz.meituan.com/meishi/c11/pn2/',
	'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/66.0.3359.117 Safari/537.36'
}


def read_shop_class_from_db():
	shop_class = []
	db = Database()
	shop_class = db.select_from('SELECT * FROM crawler.mt_directory')
	db.close()
	return shop_class


def extrace(html,type_code):
	# all_shop_info = re.compile(r'"poiInfos":(.*?)}}', re.IGNORECASE)
	# classes_data = all_shop_info.findall(html)[0][1:-1]
	# shops_list = classes_data.split(']}')
	# for shop_info in shops_list:
	# 	print(shops_list)
	shop_lists = json.loads(html)['data']['poiInfos']
	shop_info_list = []
	for shop_info in shop_lists:
		data = {}
		data['FIRST_LEVEL_DIRECTORY'] = '美食'
		data['SECOND_LEVEL_DIRECTORY'] = class_code[type_code]
		data['SHOP_ID'] = shop_info['poiId']
		data['SHOP_NAME'] = shop_info['title']
		data['RANK_STARS'] = shop_info['avgScore']
		data['AVG_PRICE_TITLE'] = shop_info['avgPrice']
		data['ADDRESS'] = shop_info['address']
		data['SHOP_PHOTOS'] = shop_info['frontImg']
		shop_info_list.append(data)
	return shop_info_list	



def down_shop_name(one_class=None):
	down = Downloader(headers=request_headers)
	# http://hz.meituan.com/meishi/api/poi/getPoiList?cityName=%E6%9D%AD%E5%B7%9E&cateId=20004&page=2
	page = 0

	def get_uuid(url):
		text_uuid = down(url)
		re_uuid = re.compile(r'"uuid":"(.*?)",', re.IGNORECASE)
		try:
			uuid = re_uuid.findall(text_uuid)[0]
		except Exception as e:
			print('get uuid error: ', e)
			return None
		return uuid

	while True:
		html = ''
		page += 1
		print('*****in*****down_shop_name*****')
		# print(one_class)
		# print('*****one class*****')
		type_code = one_class['DIRECTORY_CODE']
		url_uuid = 'http://hz.meituan.com/meishi/%s/pn%d/' % (type_code, page)
		down.headers['Referer'] = url_uuid
		uuid = get_uuid(url_uuid)
		if not uuid:
			break
		type_code = type_code.replace('c','')
		url = r'http://hz.meituan.com/meishi/api/poi/getPoiList?uuid='+uuid+r'&platform=1&partner=126&originUrl=http%3A%2F%2Fhz.meituan.com%2Fmeishi%2Fc11%2Fpn2%2F&riskLevel=1&optimusCode=1&cityName=%E6%9D%AD%E5%B7%9E&'+'cateId=%s&areaId=0&sort=&dinnerCountAttrId=&page=%d&userId=0' % (type_code, page)
		# print(url)
		html = down(url)
		# json_html = json.loads(html)
		# print(json_html['status'])
		# print(type(html))
		# if len(html) < 100:
		# 	print(url)
		# 	break
		# print(html[:100])
		
		shop_info_list = extrace(html, type_code)
		threads = []

		def write_data_to_db():
			data = shop_info_list.pop()
			db = Database()
			db.insert_into(data)

		while shop_info_list or threads:
			for thread in threads:
				if not thread.is_alive():
					threads.remove(thread)
			while len(threads) < 5 and shop_info_list:
				thread = threading.Thread(target=write_data_to_db)
				thread.setDaemon(True)
				thread.start()
				threads.append(thread)
			# time.sleep(0)
		# print(type_code)
	# print('over')


def down_proc_pool(num=27, list_=None):
	'''进程池的使用'''
	pool = Pool(processes=int(num)) 

	# for i in range(1,10):
	# 	pool.apply_async(run_proc, args=(i, ))
	# print(list_)
	print(len(list_))
	pool.map(down_shop_name, list_)
	print('Waiting for all subprocesses done...')
	pool.close()
	pool.join()
	print('All subprocesses done')


def main():
	shop_class = read_shop_class_from_db()
	# print(len(shop_class))
	down_proc_pool(list_=shop_class)

if __name__ == '__main__':
	main()