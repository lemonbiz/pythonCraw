import json
for i in range(1):
	#path = 'provinceName/'+str(i)+'/'+str(i)+'.json'
	with open('1.gson', 'r') as fp:
		dict_load = json.load(fp)
		print type(dict_load)
		print dict_load['1']['urlList']['2018-01-01'][0:5]
