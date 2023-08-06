# /usr/bin/python

from idoit_scaleup import createApiCall, consts
import json
from pprint import pprint
import sys
config_file = 'idoit_live.json'

f = open(config_file)
cfg = json.load(f)
f.close()

f = open('whmcs.json')
whmcs_json = json.load(f)
f.close()

cust_id_dict={}
f = open('kunden_racks.txt')
for line in f.readlines():
    arr=line.split('\t')
    old_name=arr[3]
    cust_id_dict[old_name]=arr[0]
f.close()
racks={}
rack_order=[]
for dc in whmcs_json['datacenter']:
    dc_name=dc['name']
    for cage in dc['cages']:
        cage_name=cage['name']
        for rack in cage['racks']:
            rack_name=rack['name']
            old_rack_name='%s-%s-%s' % (dc_name, cage_name, rack_name)
            if rack_name.endswith('-LH') :
                rack_name=rack_name.replace('-LH','.1')
            elif rack_name.endswith('-UH'):
                rack_name=rack_name.replace('-UH','.2')
            elif rack_name.endswith('-1'):
                rack_name=rack_name.replace('-1','.1')
            elif rack_name.endswith('-2'):
                rack_name=rack_name.replace('-2','.2')
            elif rack_name.endswith('-3'):
                rack_name=rack_name.replace('-3','.3')
            elif rack_name.endswith('-4'):
                rack_name=rack_name.replace('-4','.4')
            else:
                rack_name=rack_name+'.1'
            parts=rack_name.split('.')
            if len(parts[1])==1:
                parts[1]='0%s' % parts[1]
            rack_name=".".join(parts)
            new_rack_name='%s.%s.%s' % (dc_name, cage_name, rack_name)
            if new_rack_name.startswith('BER2.E1-2.'):
                new_rack_name=new_rack_name.replace('BER2.E1-2.','BER2.E1-2_')
                new_rack_name=new_rack_name.replace('.C.','.C')
            if new_rack_name.startswith('HAM2.HE-31.G'):
                new_rack_name=new_rack_name.replace('HAM2.HE-31.G','HAM2.HE31.G.').replace('.01','.1')
            # Dieser Racks gibt es gar nicht:
            if new_rack_name not in ['BER3.H1.B.10.3', 'BER3.H1.B.10.4']:
                rack_order.append(new_rack_name)
                racks[new_rack_name]={
                    'old_name': old_rack_name,
                    'name': new_rack_name,
                    'kwh_meters': 0,
                    'auto_meters': 0,
                    'a_meters':0,
                    'pdus':[]
                }
                if old_rack_name in cust_id_dict.keys():
                    racks[new_rack_name]['customer']=cust_id_dict[old_rack_name]
                else:
                    racks[new_rack_name]['customer']=''
                if 'number_of_pdu_kwh' in rack.keys():
                    racks[new_rack_name]['kwh_meters']=rack['number_of_pdu_kwh']
                if 'auto_meter' in rack.keys():
                    racks[new_rack_name]['auto_meters']=rack['number_of_pdu']
                else:
                    racks[new_rack_name]['a_meters']=rack['number_of_pdu']
#fix_lat(OBJ_ID, idoit_apis[consts.C__CATG__LOCATION])
api=createApiCall(cfg, consts.C__OBJTYPE__PDU)
data=api.get_all([consts.C__CATG__LOCATION])

whmcs_api=createApiCall(cfg, 'C__OBJTYPE__WHMCS_CUSTOMER')
idoit_whmcs_data=whmcs_api.get_all([])
#pprint(idoit_whmcs_data)
idoit_whmcs_objid={}
for ele in idoit_whmcs_data:
    whmcs_id=ele['title'][:5]
    idoit_whmcs_objid[whmcs_id]=ele['id']
change=[]
orig=[]
for pdu in data:
    rack_name=pdu['categories'][consts.C__CATG__LOCATION][0]['parent']['title']
    if  pdu['categories'][consts.C__CATG__LOCATION][0]['pos'] is not None:
        he=pdu['categories'][consts.C__CATG__LOCATION][0]['pos']['title']
    else:
        he='?'
    name=pdu['title']
    rack_id=pdu['categories'][consts.C__CATG__LOCATION][0]['parent']['id']
    if rack_name in racks.keys():
        racks[rack_name]['oid']=rack_id
        t=13
        if racks[rack_name]['a_meters']>0:
            t=15
        if racks[rack_name]['kwh_meters']>0:
            t=16
        if racks[rack_name]['auto_meters']>0:
            t=14
        c=None
        if 'customer' in racks[rack_name].keys():
            c=racks[rack_name]['customer']
        else:
            c=None
        racks[rack_name]['pdus'].append({
            'oid': pdu['id'],
            'name': pdu['title'],
            'rack_unit': he,
            'ablesung': t,
            'customer': c

        })
racks['BER1.C2.A.07.2']['pdus']=[
    {'name':'BER1.C2.A.07.1.A.1','oid':1077,'rack_unit':1, 'ablesung':15, 'customer':'70800'},
    {'name':'BER1.C2.A.07.1.B.1','oid':1075,'rack_unit':2, 'ablesung':15, 'customer':'70800'},
]
racks['BER2.E1-2_4.C13.15.2']['pdus']=[
    {'name':'BER2.E1-2_4.C13.15.1.B.1','oid':1393,'rack_unit':2, 'ablesung':15, 'customer':'70759'},
    {'name':'BER2.E1-2_4.C13.15.1.A.1','oid':1395,'rack_unit':1, 'ablesung':15, 'customer':'70759'},
]

for rack_name in sorted(racks.keys()):
    rack=racks[rack_name]
    if rack['a_meters']!=0 and rack['kwh_meters']!=0:
        print('FIXME keine Zuordnung wegen kwh+A meters')
        pprint(racks[rack_name])
    okay=False
    if len(rack['pdus'])==(rack['a_meters']+rack['kwh_meters']+rack['auto_meters']):
        okay=True
    else:
        if (rack['a_meters']+rack['kwh_meters']+rack['auto_meters'])==2:
            count=0
            new_pdus=[]
            for pdu in rack['pdus']:
                if (pdu['name'].endswith('.A') or pdu['name'].endswith('.B')):
                    count=count+1
                    new_pdus.append(pdu)
            if count==2:
                okay=True
                rack['pdus']=new_pdus
    if not(okay):
        print('FIXME: Anzahl PDUs stimmt nicht')
        pprint(racks[rack_name])

# FIXME Was mit den Extra Meter Werten in BER1.C2

# FIXME Virtuelles geteiltes Rack, zum Schluß kontrollieren.
# BER1.C2.A.07.2
# BER2.E1-2_4.C13.15.2

# select c.id,c.companyname,h.id,h.domain,p.name,h.regdate,h.lastupdate from tblhosting h, tblclients c, tblproducts p WHERE h.packageid=p.id AND c.id=h.userid and domainstatus='Active' and configoption1='on' and servertype='rack_scaleup';
# echo "select c.id,c.companyname,h.id,h.domain,p.name,h.regdate,h.lastupdate from
#   tblhosting h, tblclients c, tblproducts p WHERE h.packageid=p.id AND c.id=h.userid and
#   domainstatus='Active' and configoption1='on' and servertype='rack_scaleup';" |mysql whmcs > kunden_racks.txt
old_cage=None

api_calls={}
for rack_name in rack_order:
    cage=".".join(rack_name.split('.')[:2])
    if old_cage != cage:
        prev = None
        old_cage=cage
    next_idx=rack_order.index(rack_name)+1
    if len(rack_order)>next_idx:
        next= racks[rack_order[next_idx]]
    rack=racks[rack_name]
    he_dict={}
    idx=0
    for pdu in rack['pdus']:
        ru=pdu['rack_unit']
        if ru in he_dict.keys():
            idx=idx+1
            ru="%s%d" % (ru,idx)
        he_dict[ru]=pdu
    for ru in sorted(he_dict.keys()):
        pdu=he_dict[ru]
        print('Setze https://idoit.int.yco.de/index.php?objID=%d' % pdu['oid'])
        print('Ablesung %d' % pdu['ablesung'])
        if pdu['customer']=='':
            c=None
        else:
            c=idoit_whmcs_objid[pdu['customer']]
        api_calls[pdu['oid']]={'ablesung':pdu['ablesung'],'prev':prev,'customer':c}
        if prev:
            api_calls[prev]['next']=pdu['oid']
        prev=pdu['oid']

#pprint(api_calls)
api_stromablesung=createApiCall(cfg,'C__CATG__CUSTOM_FIELDS_STROMABLESUNG')
api_cust_assign=createApiCall(cfg,'C__CATG__CUSTOM_FIELDS_WMCS_CUSTOMER_ASSIGNMENT')
#for oid in api_calls.keys():
#    #print(oid)
#    data=api_calls[oid]
#    fields=[]
#    if data['prev'] is not None:
#        fields.append(data['prev'])
#    if 'next' in data.keys() and data['next'] is not None:
#        fields.append(data['next'])
#    r=api_stromablesung.save_category(oid,{
#        'f_popup_c_stromablesung':data['ablesung'],
#        'f_popup_c_next_field': fields,
#    })
#    pprint(r)
#    if data['customer'] is not None:
#        r=api_cust_assign.save_category(oid,{
#            'f_popup_c_whms_ref': data['customer'],
#            'f_popup_c_start': '2023-04-01',
#        })

for rack_name in racks.keys():
     if 'oid' in racks[rack_name]:
        oid=int(racks[rack_name]['oid'])
        cust=racks[rack_name]['customer']
        if cust != '':
            c=idoit_whmcs_objid[cust]
            r=api_cust_assign.save_category(oid,{
                'f_popup_c_whms_ref': c,
                'f_popup_c_start': '2023-04-01',
            })
            pprint(r)