#create by yangyinglong at 20180406 for learn Qt crawl web
'''
#install Qt(PySide or PyQt)
sudo sudo add-apt-repository ppa:pyside
sudo sudo apt-get update
sudo apt-get install python-pyside or python3-pyside
'''
from downloader import Downloader
import lxml.html
import sys
try:
	from PySide.QtGui import *
	from PySide.QtCore import *
	from PySide.QtWebKit import *
except ImportError:
	from PyQt4.QtGui import *
	from PyQt4.QtCore import *
	from PyQt4.QtWebKit import *

#url = 'http://example.webscraping.com/places/default/dynamic'
#url = 'http://www.baidu.com'
url = 'http://example.webscraping.com/places/default/search'
app = QApplication(sys.argv)
webview = QWebView()
loop = QEventLoop()
webview.loadFinished.connect(loop.quit)
webview.load(QUrl(url))
loop.exec_()
webview.show()

frame = webview.page().mainFrame()
frame.findFirstElement('#search_term').setAttribute('value', '.')
frame.findFirstElement('#page_size option:checked').setPlainText('1000')
frame.findFirstElement('#search').evaluateJavaScript('this.click()')

elements = None
while not elements:
	app.processEvents()
	elements = frame.findAllElements('#results a')S

countries = [e.toPlainText().strip() for e in elements]
print countries





app.exec_()





'''
frame = webview.page().mainFrame()
html = frame.toHtml()
frame.findFirstElement('#kw').setAttribute('value', 'hello world')
frame.findFirstElement('#su').evaluateJavaScript('this.click()')
print html
print "########"
tree = lxml.html.fromstring(html)
print tree.text_content()
print '########'
#result = tree.cssselect('#result')[0].text_content()
#print result
app.exec_()
sys.exit()
'''


'''
D = Downloader()
html = D(url)
print html
tree = lxml.html.fromstring(html)
result = tree.cssselect('#result')[0].text_content()
print result
print tree.text_content()
'''