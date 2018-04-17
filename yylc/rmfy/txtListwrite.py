#coding=utf-8 
import sys
import json
reload(sys)
sys.setdefaultencoding( "utf-8" )

a = ['你好', '合理hhhh', 'helloworld']
with open('aaa.json', 'wb') as fp:
	json.dump(a, fp, ensure_ascii=False)