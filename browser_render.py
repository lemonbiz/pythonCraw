# -*- coding:utf-
#create by yangyinglong at 20180406 for learn browser render 
#浏览器渲染
import time
import sys
try:
	from PySide.QtGui import *
	from PySide.QtCore import *
	from PySide.QtWebKit import *
except ImportError:
	from PyQt4.QtGui import *
	from PyQt4.QtCore import *
	from PyQt4.QtWebKit import *


class BrowserRender(QWebView):
	def __init__(self, show=True):
		self.app = QApplication(sys.argv)
		QWebView.__init__(self)
		if show:
			self.show() 

	def download(self, url, timeout=60):
		'''Wait for download to complete and return result'''
		loop = QEventLoop()
		timer = QTimer()
		timer.setSingleShot(True)
		timer.timeout.connect(loop.quit)
		self.loadFinished.connect(loop.quit)
		self.load(QUrl(url))
		timer.start(timeout * 1000)

		loop.exec_()
		if timer.isActive():
			# downloaded successfully
			timer.stop()
			return self.html()
		else:
			#timed out
			print 'Request timed out: ' + url

	def html(self):
		''' Shortcut to return the current HTML'''
		return self.page().mainFrame().toHtml()

	def find(self, pattern):
		'''Find all elements that match the pattern'''
		return self.page().mainFrame().findAllElements(pattern)

	def attr(self, pattern, name, value):
		'''set attribute for matching elements'''
		for e in self.find(pattern):
			e.setAttribute(name, value)

	def text(self, pattern, value):
		'''set attribute for matching elements'''
		for e in self.find(pattern):
			e.setPlainText(value)

	def click(self, pattern):
		'''click matching elements'''
		for e in self.find(pattern):
			e.evaluateJavaScript('this.click()')

	def wait_load(self, pattern, timeout=60):
		'''wait until pattern is found and return matches'''
		deadline = time.time() + timeout
		while time.time() < deadline:
			self.app.processEvents()
			matches = self.find(pattern)
			if matches:
				return matches
		print 'wait load timed out'


br = BrowserRender()
br.download('http://example.webscraping.com/places/default/search')
br.attr('#search_term', 'value', '.')
br.text('#page_size option:checked', '1000')
br.click('#search')
elements = br.wait_load('#results a')
countries = [e.toPlainText().strip() for e in elements]
print countries
