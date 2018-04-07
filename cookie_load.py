#create by yangyinglong at 201808408 for learn local cookie load to Firefox

import os, glob
import cookielib
import json
import sys
import urllib, urllib2
import lxml.html
import time

def load_ff_sessions(session_filename):
	cj = cookielib.CookieJar()
	if os.path.exists(session_filename):
		json_data = json.loads(open(session_filename, 'rb').read())
		#print json_data
		for window in json_data.get('windows', []):
			for cookie in window.get('cookies', []):
				print cookie
				c = cookielib.Cookie(0,
					cookie.get('name', ''),
					cookie.get('value', ''),None, False,
					cookie.get('host', ''), 
					cookie.get('host', '').startswith('.'),
					cookie.get('host', '').startswith('.'),
					cookie.get('path', ''), False, False,
					str(int(time.time()) + 3600 * 24 * 7),
					False, None, None, {})
				cj.set_cookie(c)

	else:
		print 'Session filename does not exist: ', session_filename
	return cj




def find_ff_sessions():
	paths = [
		'~/.mozilla/firefox/*.default',
		'~/Library/Application Support/Firefox/Profiles/*.default',
		r'%APPDATA%/Roaming/Mozilla/Firefox/Profiles/*.default'
	]
	for path in paths:
		filename = os.path.join(path, 'sessionstore.js')
		matches = glob.glob(os.path.expanduser(filename))
		if matches:
			return matches[0]

session_filename = find_ff_sessions()
print session_filename

cj = load_ff_sessions(session_filename)
print cj
print len(cj)

processor = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(processor)
url = 'http://example.webscraping.com/places/default'
html = opener.open(url).read()
tree = lxml.html.fromstring(html)
result = tree.cssselect('ul#navbar li a')[0].text_content()
print result


