# -*- coding:utf-8 -*-


import sys
reload(sys)
sys.setdefaultencoding( "utf-8" )

path = 'cache/www.rmfysszc.gov.cn/statichtml/rm_xmdetail/720212.shtml'
with open(path, 'r') as fp:
	html = fp.readlines()
	for line in html:
		print line.encode('gb18030')

'''


# -*- coding: utf-8 -*-  
  
import urllib2  
import re  
import requests  
import sys  
  
import urllib  
#设置编码  
reload(sys)  
sys.setdefaultencoding('utf-8')  
#获得系统编码格式  
type = sys.getfilesystemencoding()  
r = urllib.urlopen("http://www.baidu.com")  
#将网页以utf-8格式解析然后转换为系统默认格式  
a = r.read().decode('utf-8').encode(type)  
print a 
'''