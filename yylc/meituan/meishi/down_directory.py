'''
create by yangyinglong at 20180503 
爬取美团美食首页http://hz.meituan.com/meishi/
并解析出各个类别的名称、代码、url，并入库
'''

from datetime import datetime, timedelta

import pymysql
import re
import time

from download import Downloader
from download import Database


meishi_url = 'http://hz.meituan.com/meishi/'

def down_meishi_home(url):
	D = Downloader()
	html = D(url)
	return html


def extract_meishi_class(html):
	classes = re.compile(r'<a class="" href="(.*?)/c(.*?)" data-reactid.*?>(.*?)</a></li>', re.IGNORECASE)
	classes_data = classes.findall(html)
	classes_data.pop(0)
	print(classes_data)
	db = Database()
	for one in classes_data:
		data = {}
		now_time = datetime.now()
		now_time = str(now_time)
		now_time = now_time.split('.')[0]
		data['FIRST_LEVEL_DIRECTORY'] = '美食'
		data['SECOND_LEVEL_DIRECTORY'] = one[2]
		data['URL'] = one[0] + '/c' + one[1]
		data['DIRECTORY_CODE'] = 'c' + one[1].replace('/','')
		data['INBASE_TIME'] = now_time
		data['UPDATE_TIME'] = now_time
		data['IS_DELETE'] = 0
		db.insert_into(data)


def write_data_in_db(data):
	sql_1 = 'INSERT INTO mt_directory ('
	sql_2 = ') VALUES ('
	for key, value in data.items():
		if data[key] != None:
			sql_1 = sql_1 + key
			# keys.append(key)
			# values.append("'"+str(data[key])+"'")
			if type(data[key]) == str:
				sql_2 = sql_2 + "'" + data[key] + "'"
			else:
				sql_2 = sql_2 + str(data[key])
			sql_1 = sql_1 + ','
			sql_2 = sql_2 + ','
	sql_1 = sql_1[:-1]
	sql_2 = sql_2[:-1]
	sql = sql_1 + sql_2 +')'
	print(sql)

	# keys_str = ''.join(keys)
	# values_str = ''.join(values)
	# sql = '''insert into mt_directory(%s) values(%s)''' % (keys_str, values_str)
	conn = pymysql.connect(host='122.144.217.112',port=13306,user='pc_user4',
	                       passwd='lldfd9937JJye',db='crawler',charset='utf8')
	cursor = conn.cursor()
	try:
		cursor.execute(sql)
		conn.commit()
		a = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
		print(a + ' write successful')
	except Exception as e:
		print(e)
		conn.rollback()
	conn.close()


def main():
	# html = down_meishi_home(meishi_url)
	# extract_meishi_class(html)
	db = Database()
	now_time = datetime.now()
	now_time = str(now_time)
	now_time = now_time.split('.')[0]
	select_sql = 'SELECT * FROM crawler.mt_directory'
	update_sql = "update crawler.mt_directory set IS_DELETE = 1, UPDATE_TIME = '%s' where IS_DELETE = 0" % now_time
	# select_result = db.select_from(sql)
	print(update_sql)
	# print(select_result)
	db.update_data(update_sql)
	db.close()


if __name__ == '__main__':
	main()