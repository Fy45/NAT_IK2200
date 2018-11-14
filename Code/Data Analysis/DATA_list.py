# -*- coding: utf-8 -*-
"""
Created on Fri Oct  5 09:10:10 2018

@author: Lida
"""
from __future__ import division
import linecache
import re
import numpy as np
import os
import pylab as plt
#import matplotlib as plt
import seaborn as sns
import pandas as pd
from pandas.core.frame import DataFrame


# Define all the names and title
Feature_nam_total=4
flow_id=3
protocol_name = "udp"
pps = "200k"
flow_num_str=['1','100','200','300','400','500','600','700','800','900','1000','1100','1200','1300',\
'1400','1500','1600','1700','1800','1900','2000','2100','2200','2300','2400','2500']

flow_num=[]

for i in range(26):
    flow_num.append(1)


fileName_for=[]
fileName_nat=[]
for i in range(len(flow_num_str)):
    fileName_for.append(protocol_name + "_" + pps + "pps_"+flow_num_str[i]+"flow_for.log")
    fileName_nat.append(protocol_name + "_" + pps + "pps_"+flow_num_str[i]+"flow_nat.log")
save_name = protocol_name + "-" + pps + "/CDF_of_latency_(" + pps + "pps).png"
save_name_drop = protocol_name + "-" + pps + "/Time_serie_Drop_packets_(" + pps + "pps).png"
save_name_rpps = protocol_name + "-" + pps + "/Time_serie_rpps_(" + pps + "pps).png"
save_name_tpps = protocol_name + "-" + pps + "/Time_serie_tpps_(" + pps + "pps).png"
save_name_cdf_rpps = protocol_name + "-" + pps + "/cdf_rpps_(" + pps + "pps).png"
save_name_cdf_tpps = protocol_name + "-" + pps + "/cdf_tpps_(" + pps + "pps).png"
save_name_cdf_drop = protocol_name + "-" + pps + "/cdf_drop_(" + pps + "pps).png"
title_drop = "Numbers of Drop Packets (" + pps + "pps)"
title = "CDF of latency with NAT (" + pps + "pps)"

def get_throughput_speed(fileName_for, fileName_nat):
    fileName_list = [fileName_for,fileName_nat]
    result_list = []
    for fileName in fileName_list:
        throughput_list = []
        file = open(fileName)
        i=0
        pat = re.compile('[a-z]')
    
        for line in file.xreadlines():
            i+=1
            line=(linecache.getline(fileName,i)).strip()
            #print line
            symbol=pat.findall(line)
            #print type(symbol)
            if(len(symbol)>2):
                #print symbol
                if(symbol[0]=="c" and symbol[1]=="p" and symbol[2]=="u"):
                    #print linecache.getline(fileName,i)
                    
                    throughput_line=linecache.getline(fileName,i)
                    
                    if "Mb/sec" in throughput_line:
                        throughput = float(throughput_line.split('total_rx     : ')[1].split(' Mb/sec')[0])
                        
                        
                        throughput_list.append(throughput)
                    
        
        index = len(throughput_list)-1
        while index > 0:
            if throughput_list[index] < (throughput_list[0]-40):
                throughput_list.pop()
            else:
                break
            index = index - 1
        
        result_list.append(throughput_list)
    
    fileName_for = result_list[0]
    fileName_nat = result_list[1]
    
    return fileName_for, fileName_nat
    

def mkdir(path):
    
    isExists=os.path.exists(path)
    
    if not isExists:
        os.makedirs(path) 
 
def organize_data(list_in):
    count = 0
    lenth= len(list_in)
    for i in reversed(list_in):
        if int(i) == int(list_in[len(list_in)-1]):
            count = count + 1  
        else:
            break
    
    
    return count,lenth
    
    
def read_files(fileName,fl_nm):
    file = open(fileName)
    PG_ID_p=[]
    flowlist=range(0,fl_nm)
    flow_list= [str(x) for x in flowlist]
    alt=pd.DataFrame(columns=flow_list)
    rp_p=pd.DataFrame(columns=flow_list)
    rps_p=pd.DataFrame(columns=flow_list)
    tp_p=pd.DataFrame(columns=flow_list)
    tps_p=pd.DataFrame(columns=flow_list)
    dps_p=pd.DataFrame(columns=flow_list)
     
    i=0
    pat = re.compile('[A-Z]')

    for line in file.xreadlines():
        i+=1
        line=(linecache.getline(fileName,i)).strip()
        #print line
        symbol=pat.findall(line)
        #print type(symbol)
        if(len(symbol)>2):
            #print symbol
            if(symbol[0]=="P" and symbol[1]=="G" and symbol[2]=="I" and symbol[3]=="D"):
                #print linecache.getline(fileName,i)
                
                PG_ID_p.append(i)
            
            
                
    

    for i in range(len(PG_ID_p)):
        rp=[]
        tp=[]
        lat=[]
        rps=[]
        tps=[]
        dps=[]
        
        tp_line=re.findall(r"\d+\.?\d*",linecache.getline(fileName,PG_ID_p[i]+2))
        #print linecache.getline(fileName,PG_ID_p[i])
        rp_line=re.findall(r"\d+\.?\d*",linecache.getline(fileName,PG_ID_p[i]+3))
        #print rp_line
        lat_line=re.findall(r"\d+\.?\d*",linecache.getline(fileName,PG_ID_p[i]+5))
        
        
        if(len(rp_line)>0 and len(lat_line)>0 and len(tp_line)>0):
            for j in range(fl_nm):
                #print j
                #print j
                rp.append(float(rp_line[j]))
                tp.append(float(tp_line[j]))
                lat.append(float(lat_line[j]))
                if(i==0):
                    rps.append(float(rp_line[j]))
                    tps.append(float(tp_line[j]))
                    
                else:
                    rps.append(float(rp_line[j])-(rp_p.loc[i-1])[j])
                    #print float(rp_line[j])-(rp_p.loc[i-1])[j]
                    tps.append(float(tp_line[j])-(tp_p.loc[i-1])[j])
                dps.append(tps[j]-rps[j])
                    
                
            
            alt.loc[i]=lat
            rp_p.loc[i]=rp
            tp_p.loc[i]=tp
            rps_p.loc[i]=rps
            tps_p.loc[i]=tps
            dps_p.loc[i]=dps
    #print alt
    m,l=organize_data((np.array(alt['0'])).tolist())
    alt=alt.ix[:l-m]
    rp_p=rp_p.ix[:l-m]
    tp_p=tp_p.ix[:l-m]
    rps_p=rps_p.ix[:l-m]
    tps_p=tps_p.ix[:l-m]
    dps_p=dps_p.ix[:l-m]

    return rp_p, tp_p,tps_p,dps_p, alt
   
rp_for_=[] 
rps_for_=[] 
tp_for_=[] 
tps_for_=[]
dps_for_=[] 
alt_for_=[] 
rp_nat_=[]
rps_nat_=[]
tp_nat_=[]
tps_nat_=[]
dps_nat_=[]
alt_nat_=[]
  
for i in range(len(flow_num_str)):
    savename_for= "/Users/user/Desktop/plot/latency_for_"+flow_num_str[i]+".csv" 
    savename_nat= "/Users/user/Desktop/plot/latency_nat_"+flow_num_str[i]+".csv"
    savename_for_rp= "/Users/user/Desktop/plot/throughput_for_"+flow_num_str[i]+".csv" 
    savename_nat_rp= "/Users/user/Desktop/plot/throughput_nat_"+flow_num_str[i]+".csv"       
    rp_for,tp_for,tps_for,dps_for,alt_for=read_files(fileName_for[i],flow_num[i])
    alt_for.to_csv(savename_for)
    rp_nat,tp_nat,tps_nat,dps_nat,alt_nat=read_files(fileName_nat[i],flow_num[i])
    rps_for, rps_nat = get_throughput_speed(fileName_for[i], fileName_nat[i])
    a={'0':rps_for}
    b={'0':rps_nat}
    rp_df_for=DataFrame(a)
    rp_df_nat=DataFrame(b)
    rp_df_for.to_csv(savename_for_rp)
    rp_df_nat.to_csv(savename_nat_rp)
    
    alt_nat.to_csv(savename_nat)

