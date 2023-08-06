# -*- coding: utf-8 -*-
"""
Created on Fri Sep 23 21:41:10 2022

@author: ScottStation
"""

import qesdk
import pandas as pd
qesdk.auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.')
#qesdk.auth('qestratmarket','$1$$BbR4MSZT9isFx3PBepvxd/')
#qesdk.auth('Scott_1665208401','$1$$oaWXYSWPp1jpTQmndXJcK/')
#print(qesdk.check_auth())

#for p in ["AG",'ME',"RO","TC","WS","ER"]:
#    con = qesdk.get_valid_instID(p+"9999")
#    print(con,qesdk.get_price(con,'2023-05-03','2023-05-05'))
print(qesdk.get_price('SI2308.GFE','2023-04-27','2023-05-26','daily'))
print(qesdk.get_price('SI2308.GFE','2023-04-27','2023-05-26','minute'))
print(qesdk.get_ticks('IF2306.CCF','2023-05-21','2023-05-26'))
print(qesdk.get_prod_open_time('AU2312.SFE'))
print(qesdk.get_prod_open_time('IC2306.CCF'))
#print(qesdk.get_dominant_instID("IC",'2023-05-08','9999'))
#print(qesdk.get_dominant_instIDs(['IC','AG','SI'], '2023-05-01', "2023-05-09"))
#print(qesdk.get_instrument_setting('T2305.CCF'))
inst = "AG2312.SFE"
ddict = qesdk.get_bar_data([inst], "2023-05-23")
print(ddict)
df = ddict[inst]
#print(type(df.index[0]))
#df['runtime']= pd.to_datetime(df.index, format='%Y%m%d%H%M%S',errors='ignore')
#df.set_index(["runtime"], inplace=True)
print(df)
#print(ddict[inst].columns)

#print(qesdk.update_public_ip('180.161.73.253'))

qesdk.login('scott','12345678')

stratlist=(qesdk.sm_get_clone_strat_list())
print('strats',stratlist)
'''
if stratlist and isinstance(stratlist,list) and len(stratlist) > 0:
    print(qesdk.sm_get_clone_strat_position(stratlist))

#df = qesdk.get_instrument_broker_pnl('东证期货','AU2306.SFE','2023-02-24','2023-02-28')
#df = qesdk.get_product_invent_orders('CU', '2023-02-01','2023-02-14')
inst = 'AU2312.SFE'
data = qesdk.get_bar_data([inst], '',5,freq=5)
#df = qesdk.get_realtime_minute_prices(['AU2312.SFE','AG2401.SFE'])
print(data[inst])'''
#print(df['510300.SSE'].columns)
    
#qesdk.auth('quantease','$1$$k7yjPQKv8AJuZERDA.eQX.')
#
#print(df)
#print(qesdk2.get_price('AG2212.SFE','2022-09-01','2022-09-22'))口红  



