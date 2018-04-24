a = '''{"html":"<table cellpadding='0' cellspacing='0' border='0' width='100%' align='centert' style='margin: 0px auto;'><thead><tr style='background: white;'><th style='width: 52%'>公告名称</th><th style='width: 35%;text-align: left;'><span style='margin-left:110px;'>法院</span></th><th>发布日期</th></tr></thead><tbody><tr><td colspan='3'>暂无数据</td></tr></tbody></table>","page":"","page1":""}'''
print(len(a))

# import pymysql
# from datetime import datetime, timedelta
# import time

# a = "afasdf %d, %s" % (123, '1232')
# print('12321')
# print(a)

# data['resource_id'] = int(source_id)
# data['resource_type'] = 5
# data['name'] = address
# data['province'] = meta_data[2]
# data['address'] = address
# data['land_type'] = land_type
# data['deal_status'] = 0
# data['source_url'] = 'www.rmfysszc.gov.cn'
# data['declaration_time'] = meta_data[1]
# data['start_price'] = start_price
# data['min_raise_price'] = min_raise_price
# data['cash_deposit'] = cash_deposit
# data['trading_place'] = trading_place
# data['announce_num'] = int(source_id)
# data['subject_type'] = 1
# data['housing_area'] = housing_area
# data['land_area'] = land_area
# data['evaluate_price'] = evaluate_price
# data['auction_stage'] = auction_stage
# data['is_deleted'] = 0
# data['city'] = city
# data['district'] = district

# data = {
# 	'address': '张根社位于晋州市朝阳sss街南的商铺', 
# 	'housing_area': '137.5平方米', 
# 	'announce_num': 831169, 
# 	'auction_stage': 1, 
# 	'min_raise_price': 500000, 
# 	'declaration_time': '2018-03-21 21:10:20', 
# 	'is_deleted': 0, 
# 	'cash_deposit': 15000000, 
# 	'resource_id': 831169, 
# 	'start_price': 945760000000, 
# 	'subject_type': 1, 
# 	'source_url': 'www.rmfysszc.gov.cn', 
# 	'province': '河北省', 
# 	'land_area': '0平方米', 
# 	'evaluate_price': 20184271700, 
# 	'resource_type': 5, 
# 	'deal_status': 0, 
# 	'name': '张根社位于晋州市朝阳街南的商铺', 
# 	'trading_place': "晋州市朝阳街南的商铺", 
# 	'city': '晋州市',
# 	'district': '张根社',
# 	'land_type': 2}
# t = datetime.now()
# t = str(t)
# t = t.split('.')[0]
# conn = pymysql.connect(host='122.144.217.112',port=13306,user='pc_user4',
# 	passwd='lldfd9937JJye',db='crawler',charset='utf8')
# cursor = conn.cursor()
# #effect_row = cursor.execute("select * from fixed_asset_new")

# sql = "INSERT INTO fixed_asset_new (resource_id,resource_type,name,address,sell_type,land_type,is_bid,deal_status,source_url,province,city,district,declaration_time,start_price,min_raise_price,cash_deposit,trading_place,announce_num,subject_type,housing_area,land_area,evaluate_price,auction_stage,is_deleted,gmt_created,gmt_modified) VALUES (%d,%d,'%s','%s',%d,%d,%d,%d,'%s','%s','%s','%s','%s',%d,%d,%d,'%s',%d,%d,'%s','%s',%d,%d,%d,'%s','%s')" % (data['resource_id'],data['resource_type'],data['name'],data['address'],2,data['land_type'],0,data['deal_status'],data['source_url'],data['province'],data['city'],data['district'],data['declartion_time'],data['start_price'],data['min_raise_price'],data['cash_deposit'],data['trading_place'],data['announce_num'],data['subject_type'],data['housing_area'],data['land_area'],data['evaluate_price'],data['auction_stage'],data['is_deleted'],t,t)

# print(sql)
# try:
# 	cursor.execute(sql)
# 	conn.commit()
# 	print('successful')
# except Exception as e:
# 	print(e)
# 	conn.rollback()
# conn.close()

# # print(effect_row)
# # row_1 = cursor.fetchone()
# # print(row_1)
# #cursor.execute(lect * from fixed_asset_new"
#  # data['resource_id'] = source_id d
#  # data['resource_type'] = 5 d 
#  # data['name'] = address s
#  # data['area'] = meta_data[2] s
#  # data['address'] = address s
#  # data['land_type'] = land_type d
#  # data['deal_status'] = 0 d
#  # data['source_url'] = 'www.rmfysszc.gov.cn' s
#  # data['declartion_time'] = meta_data[1] s
#  # data['start_price'] = start_price d
#  # data['min_raise_price'] = min_raise_price d
#  # data['cash_deposit'] = cash_deposit d
#  # data['trading_place'] = trading_place s
#  # data['announce_num'] = source_id d
#  # data['subject_type'] = 1 d
#  # data['housing_area'] = housing_area s
#  # data['land_area'] = land_area s
#  # data['evaluate_price'] = evaluate_price d
#  # data['auction_stage'] = auction_stage d
#  # data['is_deleted'] = 0 d

# '''
# sql = "INSERT INTO trade (name, account, saving) VALUES ( '%s', '%s', %.2f )"
# data = ('雷军', '13512345678', 10000)
# cursor.execute(sql % data)
# connect.commit()
# print('成功插入', cursor.rowcount, '条数据')
# '''



# '''
# a = 'aaaabbbcccddd'
# a = a.replace('aa', 'vv').replace('dd', 'tt') \
# .replace('cc', 'pp')
# print(a)

# c = r'vcdfere' \
# 'cddf'
# print(c)


# def changePrice(a):
# 	b = ''
# 	for i in a:
# 		if i in ['0','1','2','3','4','5','6','7','8','9','万','元','.']:
# 			b = b + i
# 	return b

# a = changePrice('@@1$$242.3234万元')
# print(a)
# '''