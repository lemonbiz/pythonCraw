# -*- coding:utf-
#create at 20180407 by yangyinglong for learn post from to web
#表单交互

import urllib, urllib2
import lxml.html
import pprint
import cookielib


LOGIN_URL = 'http://example.webscraping.com/places/default/user/login'
LOGIN_EMAIL = '1106875923@qq.com'
LoGIN_PASSWORD = 'Hdu1100837'

def parse_form(html):
	tree = lxml.html.fromstring(html)
	data = {}
	for e in tree.cssselect('form input'):
		if e.get('name'):
			data[e.get('name')] = e.get('value')
	return data


'''
html = urllib2.urlopen(LOGIN_URL).read()
form = parse_form(html)
pprint.pprint(form)
'''


'''
#_formkey:服务器端使用唯一的ID来避免表单多次提交，
#每次加载网页时都会产生不同的ID，
#然后服务器端就可以通过这个给定的ID来判断表单是否已经提交过
{'_formkey': 'f0bf7f93-378b-4023-8810-27147cf93d17',  
 '_formname': 'login',
 '_next': '/places/default/index',
 'email': '',
 'password': '',
 'remember_me': 'on'}

'''

'''
当普通用户加载表单数据时，_formkey的值将会保存在cookie中，
然后该值会与提交的登录表单数据中的_formkey值进行对比
'''

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
html = opener.open(LOGIN_URL).read()
data = parse_form(html)
data['email'] = LOGIN_EMAIL
data['password'] = LoGIN_PASSWORD
#在from标签中，enctype用来设置数据提交的编码，method属性被设置为post，表示通过请求体向服务器端提交表单数据
#<form action="#" enctype="application/x-www-form-urlencoded" method="post">
#<table><tbody><tr id="auth_user_email__row"><td class="w2p_fl"><label class="" for="auth_user_email" id="auth_user_email__label">电子邮件: </label></td><td class="w2p_fw"><input class="string" id="auth_user_email" name="email" type="text" value=""></td><td class="w2p_fc"></td></tr><tr id="auth_user_password__row"><td class="w2p_fl"><label class="" for="auth_user_password" id="auth_user_password__label">密码: </label></td><td class="w2p_fw"><input class="password" id="auth_user_password" name="password" type="password" value=""></td><td class="w2p_fc"></td></tr><tr id="auth_user_remember_me__row"><td class="w2p_fl"><label class="" for="auth_user_remember_me" id="auth_user_remember_me__label">记住我(30 天): </label></td><td class="w2p_fw"><input class="boolean" id="auth_user_remember_me" name="remember_me" type="checkbox" value="on"></td><td class="w2p_fc"></td></tr><tr id="submit_record__row"><td class="w2p_fl"></td><td class="w2p_fw"><input type="submit" value="Log In" class="btn"><button class="btn w2p-form-button" onclick="window.location='/places/default/user/register?_next=%2Fplaces%2Fdefault%2Findex';return false">注册</button></td><td class="w2p_fc"></td></tr></tbody></table><div style="display:none;"><input name="_next" type="hidden" value="/places/default/index"><input name="_formkey" type="hidden" value="46bb55d1-8cce-48aa-bb80-5e495629d96d"><input name="_formname" type="hidden" value="login"></div></form>
encoded_data = urllib.urlencode(data)
request = urllib2.Request(LOGIN_URL, encoded_data)
response = opener.open(request)
url = response.geturl()
print url
