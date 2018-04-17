from selenium import webdriver
import os
import re
import sys

reload(sys)
sys.setdefaultencoding( "utf-8" )


class Selenium(object):
	"""docstring for Selenium"""
	def __init__(self, arg):
		super(Selenium, self).__init__()
		self.arg = arg

	def __call__(self, url):
		result = None
		if self.cache:

	def driver(self, url, page):
		driver.implicitly_wait(30)
		results = driver.find_elements_by_css_selector('tr.listtr > td > span > a')
		hrefs = [result.get_attribute('href') for result in results]
		nextPages = driver.find_elements_by_css_selector('a.next')
		print len(nextPages)
		if page == 0:
			nextPage = nextPages[0]
		else:
			nextPage = nextPages[2]
		nextPage.click()

