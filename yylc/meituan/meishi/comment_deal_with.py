'''
created by yangyinglong at 20180523
'''

from download import Database

db = Database()
no_comment_id_list = []
sql_update_no_comment_id = "update crawler.mt_meishi set LABEL_IS_CCRAWLED = 0 where SHOP_ID = '"

# 从数据库中读取评论字段为空的商铺id
def get_shop_id():
	sql_slect_id = "select SHOP_ID from crawler.mt_meishi where FIRST_LEVEL_DIRECTORY = '美食' \
		and LABEL_IS_CCRAWLED != 5 and NETIZEN_EVALUTION is null limit 20;"
	id_dict = db.select_from(sql_slect_id)
	id_list = [id['SHOP_ID'] for id in id_dict]
	return id_list

# 从数据库中根据id读取评论信息并合成一条语句返回
def get_shop_command(id):
	sql_slect_comment = "select NETIZEN_EVALUTION from crawler.mt_shop_comments where SHOP_ID = \
		'"+str(id)+"';"
	comment_dict = db.select_from(sql_slect_comment)
	if not comment_dict:
		# no_comment_id_list.append(id)
		print('no this id')
		return None
	comment_str = ''
	for comment in comment_dict:
		comment_str = comment_str + comment['NETIZEN_EVALUTION']
	return comment_str

# 把评论信息更新到最终的表中
def update_comment_by_id(id,comment):
	sql_update_comment = '''update crawler.mt_meishi set NETIZEN_EVALUTION = "''' + comment + '''\
		" , LABEL_IS_CCRAWLED = 4 where SHOP_ID = "'''+ str(id) + '''";'''
	try:
		db.update_data(sql_update_comment)
	except:
		update_label_by_id(id)

# 如果没有评论信息，更新label字段为5
def update_label_by_id(id):
	sql_update_label = "update crawler.mt_meishi set LABEL_IS_CCRAWLED = 5 where SHOP_ID = '" \
		+ str(id) + "';"
	db.update_data(sql_update_label)

def update_no_comment_id():
	while no_comment_id_list:
		no_comment_id = no_comment_id_list.pop()
		sql = sql_update_no_comment_id + str(no_comment_id) + "';"
		db.update_data(sql)

# 主函数
def main():
	# id = '42207262'
	# comment = get_shop_command(id)
	# update_comment_by_id(id, comment)
	id_list = get_shop_id()
	while id_list:
		print("***again****")	
		for id in id_list:
			comment = get_shop_command(id)
			if comment:
				update_comment_by_id(id, comment)
			else:
				update_label_by_id(id)
		id_list = get_shop_id()
		# update_no_comment_id()

if __name__ == '__main__':
	main()
