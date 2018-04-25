'''
created by yangyinglong at 20180425
'''

from datetime import datetime, timedelta
import json
import time

from down_class import DiskCache
from down_noce_inon import threaded_download
from html_exct import extract

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
		json.dump(information, fp, ensure_ascii=False)