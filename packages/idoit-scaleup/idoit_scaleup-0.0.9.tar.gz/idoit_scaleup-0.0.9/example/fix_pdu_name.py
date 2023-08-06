# /usr/bin/python

from idoit_scaleup import createApiCall, consts
import json
from pprint import pprint
import sys
config_file = 'idoit_live.json'

f = open(config_file)
cfg = json.load(f)
f.close()


#fix_lat(OBJ_ID, idoit_apis[consts.C__CATG__LOCATION])
api=createApiCall(cfg, consts.C__OBJTYPE__PDU)
data=api.get_all([consts.C__CATG__LOCATION])
change=[
]
orig=[]
for pdu in data:
    rack_name=pdu['categories'][consts.C__CATG__LOCATION][0]['parent']['title']
    name=pdu['title']
    orig.append(name)
    new_name=""
    if not name.startswith(rack_name):
        if name.startswith('DUS1-S1-3F13'):
            pass
        elif name.startswith('SH7'):
            pass
        elif name.startswith('HAM1.S8.'):
            pass
        print(pdu['id'],name, rack_name)

