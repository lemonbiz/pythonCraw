from selenium import webdriver
import os
import re
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )

driver = webdriver.Chrome()
driver.get('http://www1.rmfysszc.gov.cn/News/Pmgg.shtml?fid=3584&dh=3&st=0')
fp = open('zcssList.txt','wb')
for i in range(4):
	driver.implicitly_wait(30)
	results = driver.find_elements_by_css_selector('tr.listtr > td > span > a')
	hrefs = [result.get_attribute('href') for result in results]
	'''
	for href in hrefs:
		fp.write(href+'\n')
	'''
	nextPages = driver.find_elements_by_css_selector('a.next')
	print len(nextPages)
	if i == 0:
		nextPage = nextPages[0]
	else:
		nextPage = nextPages[2]
	nextPage.click()

'''
titles = [result.http for result in results]
with open('title.txt', 'wb') as fp:
	for title in titles:
		fp.write(title+'\n')
'''