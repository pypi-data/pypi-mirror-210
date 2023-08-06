# /usr/bin/python

from idoit_scaleup import createApiCalls, consts, conditional_read
import json

config_file = 'idoit_live.json'

f = open(config_file)
cfg = json.load(f)
f.close()

search = conditional_read(cfg)
search.add_search_param(consts.C__CATG__LOCATION, 'latitude', 0.0)
search.add_search_param(consts.C__CATG__LOCATION, 'longitude', 0.0, 'AND')
search_result = search.search()
print('---------------------------------------------')
print(len(search_result))
print('---------------------------------------------')
# for ele in search_result:
