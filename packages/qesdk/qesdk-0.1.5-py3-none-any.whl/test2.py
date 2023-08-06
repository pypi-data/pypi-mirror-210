# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 21:41:10 2022

@author: ScottStation
"""


import qesdk2
import sys
import platform

from datetime import datetime,timedelta

def get_mac_address():
    import uuid
    mac = uuid.UUID(int=uuid.getnode()).hex[-12:].upper()
    return '%s:%s:%s:%s:%s:%s' % (mac[0:2], mac[2:4], mac[4:6], mac[6:8],mac[8:10], mac[10:])

def get_ver():
    vers= sys.version.split('.')
    return '_'.join(vers[:2])

def get_plat():
    return platform.system().lower()

qesdk2.auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.')

print(qesdk2.get_price('SI2308.GFE','2023-04-27','2023-05-28','daily'))
#print(qesdk2.get_price('SI2308.GFE','2023-04-27','2023-05-28','minute'))
#print(qesdk2.get_ticks('IF2305.CCF','2023-04-28','2023-05-26'))
print(qesdk2.get_prod_open_time('AU2312.SFE'))
print(qesdk2.get_prod_open_time('IC2306.CCF'))
#print(qesdk.get_dominant_instID("IC",'2023-05-08','9999'))
#print(qesdk.get_dominant_instIDs(['IC','AG','SI'], '2023-05-01', "2023-05-09"))
#print(qesdk.get_instrument_setting('T2305.CCF'))
inst = "AG2312.SFE"
ddict = qesdk2.get_bar_data([inst], "2023-05-26")
print(ddict)
#qesdk2.update_public_ip('1.1.1.1')
'''
qesdk2.login('scott','12345678')

stratlist=(qesdk2.sm_get_clone_strat_list())
print('strats',stratlist)

#df = qesdk2.get_product_invent_orders('CU', '2023-02-01','2023-02-14')
#print(df)
#msg = qesdk2.get_package_address('algoex', get_plat(), get_ver(), get_mac_address())
#print(msg)
#print(qesdk2.get_plugin_permission('algoex','windows','3_8',get_mac_address(),'test','quantease'))
#df = qesdk.get_price('AG2212.SFE','2022-10-01','2022-11-01','daily')
#print(df)
#qesdk2.auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.')

#print(qesdk2.get_broker_info('cjqh3'))
#print(qesdk2.get_valid_instID('si9w'))#
#print(qesdk2.is_valid_instID('IC2309.SFE'))
#print(qesdk2.is_valid_trade_time('IC2306.SFE',datetime.now()+timedelta(hours=5)))
#df = qesdk.get_realtime_minute_prices(['AU2212_SFE','AG2301.SFE'])
#print(df)


for i in testdf['AU2212.SFE'].index:
    print(testdf['AU2212.SFE'].loc[i,'time'],testdf['AU2212.SFE'].loc[i, 'close'])
testdf['AU2212.SFE']['close'].plot()    
'''