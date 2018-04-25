'''
create by yangyinglong at 20180425
根据日志文件爬取具体省份具体时间段的公告url,name,time,title
打包成元组放入列表
作为参数传递给write_result()函数
最后更新日志文件
'''

from datetime import datetime, timedelta
import time

from io_log import write_log
from io_result import write_result
from rese_get_reou import get_response
from rese_get_reou import resolution

ERROR_RESPONSE = 0

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