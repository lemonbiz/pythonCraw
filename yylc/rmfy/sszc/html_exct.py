'''
created by yangyinglong at 20180425
提取文本中的字段并写入数据库
'''

from datetime import datetime, timedelta
from lxml import etree
from pyquery import PyQuery as pq
import pymysql
import re
import time


def write_to_db(data):
    #print('in write_to_db')
    #print(data)
    t = datetime.now()
    t = str(t)
    t = t.split('.')[0]
    sql = "INSERT INTO fixed_asset_new (resource_id,resource_type,name,address,sell_type,land_type,is_bid,deal_status,source_url,province,city,district,declaration_time,start_price,min_raise_price,cash_deposit,trading_place,announce_num,subject_type,housing_area,land_area,evaluate_price,auction_stage,is_deleted,gmt_created,gmt_modified) VALUES (%d,%d,'%s','%s',%d,%d,%d,%d,'%s','%s','%s','%s','%s',%d,%d,%d,'%s',%d,%d,'%s','%s',%d,%d,%d,'%s','%s')" % (data['resource_id'],data['resource_type'],data['name'],data['address'],2,data['land_type'],0,data['deal_status'],data['source_url'],data['province'],data['city'],data['district'],data['declaration_time'],data['start_price'],data['min_raise_price'],data['cash_deposit'],data['trading_place'],data['announce_num'],data['subject_type'],data['housing_area'],data['land_area'],data['evaluate_price'],data['auction_stage'],data['is_deleted'],t,t)
    #print(sql)
    conn = pymysql.connect(host='122.144.217.112',port=13306,user='pc_user4',
                           passwd='lldfd9937JJye',db='crawler',charset='utf8')
    cursor = conn.cursor()
    try:
        cursor.execute(sql)
        conn.commit()
        a = time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
        print(a + ' successful')
    except Exception as e:
        print(e)
        conn.rollback()
    conn.close()


def change_to_price(a):
    if not a:
        return 0
    b = ''
    c = 0
    for i in a:
        if i in ['0','1','2','3','4','5','6','7','8','9','万','元','.']:
            b = b + i
    if (b == '万元' or b == '元' or len(b) > 20) and b.count('.') > 1:
        return 0
    if '万' in b:
        try:
            c = int(float(b.replace('万','').replace('元',''))*10000*100)
        except:
            pass
        else:
            return 0
    else:
        try:
            c = int(float(b.replace('万','').replace('元',''))*100)
        except:
            pass
        else:
            return 0
    return c


def change_to_area(a):
	b = '0'
	for i in a:
		if i in ['0','1','2','3','4','5','6','7','8','9','.']:
			b = b + i
	if b.count('.') > 1:
		return '0'
	return b

def extract(source_id,text,meta_data=[]):
    html = etree.HTML(text)
    d = pq(html)
    data = {}
    '''字段名 同 crawler.fixed_asset 表字段'''
    #传入数据
    if meta_data:
    	title = meta_data[0]
        #data['name'] = meta_data[2]
        #data['url'] = meta_data['url']
        #data['declaration_time'] = meta_data[1] #发布日期

    #title = d('#Title > h1').text()
    
    #if title:
        #data['name'] = title
    auction_stage = 0
    if '第一次拍卖' in title:
    	auction_stage = 1
    if '第二次拍卖' in title:
    	auction_stage = 2
    if '第三次拍卖' in title:
    	auction_stage = 3
    if '变卖' in title:
    	auction_stage = 4


    #print('***********************************')
    #print('source_id:%s' % source_id)
    content = d('#Content').text()
    if content:
        global count
        file_find_id.append(source_id)
        count = count + 1
    else:
        content = d('.xmxx_titlemaincontent').text()
    title_content = d('table.xmxx_titlemain').text()
    content = content.replace(' ','').replace('：', '').replace('\n', '').replace('￥','').replace(' ','').replace(':','')

    #print('content:%s'% content)
    #评估价
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    price = re.compile(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价)|(?<=参考))(.*?)(元|万元|万)', re.IGNORECASE)
    ep = price.findall(content)
    evaluate_price = 0
    if len(ep) != 0:
    	for i in ep:
            a = i[1]+i[2]
            a = change_to_price(a)
            evaluate_price = evaluate_price + a
    if title_content:
    	content = content + title_content
    	if evaluate_price == 0:
	    	price = re.compile(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价)|(?<=参考))(.*?)(元|万元|万)', re.IGNORECASE)
	    	ep = price.findall(content)
	    	if len(ep) != 0:
	    		for i in ep:
	    			a = i[1]+i[2]
	    			#a = a.replace('价','').replace('（','').replace('标的一','').replace('人民币','').replace('为','').replace('\'','').replace(':','').replace('：','')
	    			a = change_to_price(a)
	    			evaluate_price = evaluate_price + a
    #print(content)
    #print('评估价:', end=' ')
    #print(evaluate_price)
    #evaluate_price= get_search(re.search(r'((?<=评估价)|(?<=保留价)|(?<=保留底价)|(?<=参考价))(.*?)(元|万元)',content))
    #print('评估价：%s' % evaluate_price)

    #起拍价
    start_price= get_search(re.search(r'(?<=起拍价)[\d,\.]+?(元|万元)',content))
    start_price = change_to_price(start_price)

    #print('起拍价:%s' % start_price)

    #保证金
    cash_deposit= get_search(re.search(r'((?<=保证金)|(?<=保证金为))(.*?)(元|万元)',content))
    if cash_deposit != None and len(cash_deposit) > 20:
    	cash_deposit = get_search(re.search(r'(?<=保证金)(.*?)(元|万元)',cash_deposit))
    if cash_deposit and len(cash_deposit) > 10:
    	cash_deposit = None
    cash_deposit = change_to_price(cash_deposit)
    #print('保证金:%s' % cash_deposit)

    #增价幅度
    min_raise_price = get_search(re.search(r'(?<=增(加|价)幅度)[\d,\.]+?(元|万元)',content))
    min_raise_price = change_to_price(min_raise_price)
    #print('增价幅度:%s' % min_raise_price)

    #建筑面积
    '''
    webpage_regex = re.compile(r'<a href="(.*?)"', re.IGNORECASE)
	urls = webpage_regex.findall(html)
    '''
    area =re.compile(r'((?<=建筑面积约)|(?<=建筑总面积)|(?<=建筑面积)|(?<=建面)|(?<=建筑面积为)|(?<=建筑面积是)|(?<=建筑面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    ha = area.findall(content)
    housing_area = 0
    if len(ha) != 0:
    	for i in ha:
    		a = i[1]+i[2]
    		a = change_to_area(a)
    		housing_area = housing_area + float(a)
    housing_area = str(housing_area) + '平方米'
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))

    #土地面积
    area =re.compile(r'((?<=土地面积约)|(?<=土地面积)|(?<=土地分摊面积)|(?<=宗地面积)|(?<=土地使用权面积)|(?<=土地证载面积)|(?<=土地面积为)|(?<=土地面积是)|(?<=土地面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
    la = area.findall(content)
    land_area = 0
    if len(la) != 0:
    	for i in la:
    		b = i[1]+i[2]
    		b = change_to_area(b)
    		land_area = str(land_area) + b
    land_area = str(land_area) + '平方米'
    #construction_area = get_search(re.search(r'((?<=面积约)|(?<=面积)|(?<=面积为)|(?<=面积是)|(?<=面积共计))[\d,\.]+?(平方米|㎡|公顷|M2)',content))
    #print('土地面积:', end=' ')
    #print(land_area)

    #如果土地面积和建筑面积都为0，则查找面积
    if land_area == '0平方米' and housing_area == '0平方米':
        area =re.compile(r'((?<=面积约)|(?<=总面积)|(?<=面积)|(?<=建面)|(?<=面积为)|(?<=面积是)|(?<=面积共计))(.*?)(平方米|㎡|公顷|M2|m2)',re.IGNORECASE)
        ha = area.findall(content)
        housing_area = 0
        if len(ha) != 0:
            for i in ha:
                a = i[1]+i[2]
                a = change_to_area(a)
                housing_area = housing_area + float(a)
        housing_area = str(housing_area) + '平方米'
    #print('建筑面积:', end=' ')
    #print(housing_area)


    #拍卖地点
    trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)(、)', content))
    if trading_place:
    	trading_place = trading_place[:-2]
    else:
    	trading_place = get_search(re.search(r'((?<=拍卖地点)|(?<=变卖电子竞价地点))(.*?)((。)|(;))', content))
    	if trading_place != None:
    		trading_place = trading_place[:-1]
    #print('交易地点:%s' % trading_place)

    #建筑性质
    if '营业' in content or '商业' in content or '商铺' in content or '门面房' in content:
    	land_type = 2
    elif '工业' in content or '厂房' in content or '库房' in content or '厂' in content:
    	land_type = 1
    elif '仓库' in content:
    	land_type = 5
    elif '商用' in content:
    	land_type = 4
    elif '商品房' in content or '商服用房' in content:
    	land_type = 7
    elif '住宅' in content:
    	land_type = 3
    elif '别墅' in content:
    	land_type = 8
    elif '办公' in content or '写字' in content:
    	land_type = 6
    else:
    	land_type = 0
    #print('建筑性质:%s' % land_type)


    #城市
    city = get_search(re.search(r'\w+?市',content))
    if city != None:
    	if '受' in city:
    		city = city.split('受')[-1]
    	if '于' in city:
    		city = city.split('于')[-1]
    	if len(city) > 6:
    		city = city[-3:]
    	city = city.replace('在', '')
    	city = city.replace('拍卖标的', '')

    #print('城市:%s' % city)

    #区
    district = get_search(re.search(r'\w+?((区)|(县)|(镇))',content))
    
    if district != None:
	    if '受' in district:
	    	district = district.split('受')[-1]
	    if '于' in district:
	    	district = district.split('于')[-1]
	    if len(district) > 10:
	    	district = district[-8:]
	    district = district.replace('在', '')
	    district = district.replace('拍卖标的', '')
    if district and '市' in district:
        district = district.split('市')[1]
    if district and '时' in district:
        district = district.split('时')[1]
    if district and '点' in district:
        district = district.split('点')[1]
    if district and '对' in district:
        district = district.split('对')[1]

    #print('地区:%s' % district)

    #日期区间
    date = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?\w{1,20}?\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    #print('日期区间:%s' % date)

    #address  从标题title里面提取地址
    address_search = get_search(re.search(r'(关于.+的公告)|(位于.+)',title))
    if address_search:
        address = address_search.replace('关于','').replace('的公告','') \
        .replace('（第二次拍卖）','').replace('（第一次拍卖）','').replace('司法变卖','')
    else:
    	address = title.replace('司法拍卖','').replace('司法变卖','').replace('公告','') \
    	.replace('拍卖','') \
    	.replace('(第三次)','').replace('(第一次)','').replace('(第二次)','')

    address_1 = get_search(re.search(r'((?<=拍卖标的)|(?<=以下标的))(.*?)((室)|(号)|(。)|(，))',content))
    #print(address_1)
    if address_1 and len(address_1) < 10:
    	address_1 = None
    if not address_1:
    	address_1 = get_search(re.search(r'(?<=位于)(.*?)((，)|(。)|(进行))',content))
    if not address_1:
    	address_1 = get_search(re.search(r'(?<=对)(.*?)((，)|(。)|(进行))',content))
    if address_1 and '（' in address_1:
    	address_1 = address_1.split('（')[0]
    if address_1 and '位于' in address_1:
    	address_1 = address_1.split('位于')[1]
    if address_1 and '进行' in address_1:
    	address_1 = address_1.split('进行')[0]
    if address_1:
    	address_1 = address_1.replace('，','').replace('。','').replace('进行','').replace('"','').replace('“','').replace('”','').replace('公开','')
    #print(address_1)
    if address_1 != None and len(address_1) > len(address):
        address_1 = address_1.replace('：','').replace('。','').replace('，','')
        address = address_1
        address = address.replace('进行','').replace('公开','')
    #print('详细地址:%s' % address)

    #data write
    #for i in range(min(len(evaluate_price), len(housing_area))):
    data['resource_id'] = int(source_id)
    data['resource_type'] = 5
    data['name'] = address
    data['province'] = meta_data[2]
    data['address'] = address
    data['land_type'] = land_type
    data['deal_status'] = 0
    data['source_url'] = 'http://www.rmfysszc.gov.cn/statichtml/rm_xmdetail/'+source_id+'.shtml'
    data['declaration_time'] = str(meta_data[1]) + ' 00:00:00'
    if start_price == None:
        start_price = 0
    data['start_price'] = start_price
    if min_raise_price == None:
        min_raise_price = 0
    data['min_raise_price'] = min_raise_price
    if cash_deposit == None:
        cash_deposit = 0
    data['cash_deposit'] = cash_deposit
    data['trading_place'] = trading_place
    data['announce_num'] = int(source_id)
    data['subject_type'] = 1
    data['housing_area'] = housing_area
    data['land_area'] = land_area
    if evaluate_price == None:
        evaluate_price = 0
    data['evaluate_price'] = evaluate_price
    data['auction_stage'] = auction_stage
    data['is_deleted'] = 0
    data['city'] = city
    data['district'] = district
    #print('***********************************')
    #print(data)
    write_to_db(data)

    #日期
    #date1 = get_search(re.search(r'\d{2,4}[年\-]\d{1,2}[月\-](\d{1,2}[日\-])?(\d{1,2}[时：:])?',content))
    #print('日期:%s' % date1)
    
    #print('***********************************')

def get_search(search):
    if search:
        return search.group()
    return None