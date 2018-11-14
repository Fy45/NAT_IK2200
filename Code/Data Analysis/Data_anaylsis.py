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
import seaborn as sns
import pandas as pd


# Define all the names and title
Feature_nam_total=4
flow_id=3
protocol_name = "udp"
pps = "500k"
flow_num_str=['1','2','4','8','10','15','25','50','75','100']
flow_num=[1,2,4,5,5,5,5,5,5,5]



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
    alt_1=alt.values
    rp_p_1=rp_p.values
    tp_p_1=tp_p.values
    tps_p_1=tps_p.values
    dps_p_1=dps_p.values
    alt_1p=alt_1.flatten()
    rp_1p=rp_p_1.flatten()
    tp_1p=tp_p_1.flatten()
    tps_1p=tps_p_1.flatten()
    dps_1p=dps_p_1.flatten()

    return rp_1p, tp_1p,tps_1p,dps_1p, alt_1p

 



def CDF(list1,list2,txt,txt1):
    #print list1[row]
    hist, bin_edges = np.histogram(list1,1000)
    #print hist
    cdf = np.cumsum(hist/sum(hist))
    #print cdf
    for i in range(len(cdf)):
        if cdf[i]>=0.5:
            x1=(bin_edges[i]+bin_edges[i+1])/2.0
            print x1
            break
    for i in range(len(cdf)):
        if cdf[i]>=0.9:
            x2=(bin_edges[i]+bin_edges[i+1])/2.0
            print x2
            break

    plt.plot(bin_edges[1:],cdf,label="With NAT",color="blue")
    plt.scatter([x1], [0.5], s=20, color="blue")
    plt.rc('xtick', labelsize = 18)
    plt.rc('ytick', labelsize = 18)
    plt.annotate("("+str(int(x1))+" , 0.5)",
                 xy=(x1, 0.5),
                 xytext=(x1+100, 0.45),
                 fontsize=18,          
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    
    plt.scatter([x2], [0.9], s=20, color="blue")
    plt.annotate("("+str(int(x2))+" , 0.9)",
                 xy=(x2, 0.9), 
                 xytext=(x2-100, 0.8),           
                 fontsize=18,          
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))   


    plt.plot([0,x1],[0.50,0.50],'--',color='grey')

    #plt.text(x1, 0.25, round(x1,2),
         #fontdict={'size': 8, 'color': 'g'})

    plt.plot([0,x2],[0.90,0.90],'--',color='grey')
    #plt.text(x2, 0.45, round(x2,2),
        # fontdict={'size': 8, 'color': 'g'})
         
    hist1, bin_edges1 = np.histogram(list2,1000)
    cdf1 = np.cumsum(hist1/sum(hist1))
    for i in range(len(cdf)):
        if cdf1[i]>=0.5:
            x1=(bin_edges1[i]+bin_edges1[i+1])/2.0
            print x1
            break
    for i in range(len(cdf1)):
        if cdf1[i]>=0.9:
            x2=(bin_edges1[i]+bin_edges1[i+1])/2.0
            print x2
            break

    plt.plot(bin_edges1[1:],cdf1,label="Without NAT ",color="orange")
    plt.scatter([x1], [0.5], s=20, color="orange")
    plt.annotate("("+str(int(x1))+" , 0.5)",
                 xy=(x1, 0.5),
                 xytext=(x1+200, 0.55),            
                 fontsize=18,          
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    
    plt.scatter([x2], [0.9], s=20, color="orange")
    plt.annotate("("+str(int(x2))+" , 0.9)",
                 xy=(x2, 0.9),
                 xytext=(x2-400, 0.95),            
                 fontsize=18,          
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    

    
    plt.plot([0,x1],[0.50,0.50],'--',color='grey')

    #plt.text(x1, 0.15, round(x1,2),
         #fontdict={'size': 8, 'color': 'g'})

    plt.plot([0,x2],[0.90,0.90],'--',color='grey')
    
    #plt.text(x2, 0.35, round(x2,2),
         #fontdict={'size': 8, 'color': 'g'})

    plt.title(txt,fontsize = 16)
    plt.yticks([0,0.1,0.2,0.3,0.4,0.5,0.6,0.7,0.8,0.9, 1.0])
    plt.ylabel("CDF",fontsize = 18)
    plt.xlabel(txt1,fontsize = 18)
    plt.xlim(min(bin_edges[0],bin_edges1[0]),)
    plt.ylim(0,1)
    plt.legend(loc=4,fontsize = 16)
    
    

def PDF(list1,row,txt,txt1):
    plt.figure('Desity_nat')
    sns.distplot(list1[row],hist=True,kde=True,bins=30)
    plt.title(txt)
    plt.xlabel('Latency(us)')
    plt.ylabel('Percentage')
    plt.ylabel("Percent")
    plt.xlabel(txt1)
    plt.show()
    plt.close()   
    
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
alt_for_aver=[]
alt_for_50=[]
alt_for_div=[]
alt_nat_aver=[]
alt_nat_div=[] 
alt_nat_50=[]
rx_for_aver=[]
rx_nat_aver=[] 
rx_for_div=[] 
rx_nat_div=[]   
for i in range(len(flow_num_str)):        
    rp_for,tp_for,tps_for,dps_for,alt_for=read_files(fileName_for[i],flow_num[i])
    rp_nat,tp_nat,tps_nat,dps_nat,alt_nat=read_files(fileName_nat[i],flow_num[i])   
    rps_for, rps_nat = get_throughput_speed(fileName_for[i], fileName_nat[i]) 
    alt_for_aver.append(np.mean(alt_for))
    alt_nat_aver.append(np.mean(alt_nat))
    rx_for_aver.append(np.mean(rps_for))
    rx_nat_aver.append(np.mean(rps_nat))
    alt_for_50.append(np.percentile(alt_for, 50))
    alt_for_div.append(np.std(alt_for))
    alt_nat_div.append(np.std(alt_nat))
    rx_for_div.append(np.std(rps_for))
    rx_nat_div.append(np.std(rps_nat))
    alt_nat_50.append(np.percentile(alt_nat, 50))
    
    rp_for_.append(rp_for)
    rps_for_.append(rps_for)
    tp_for_.append(tp_for)
    tps_for_.append(tps_for)
    dps_for_.append(dps_for)
    alt_for_.append(alt_for)
    rp_nat_.append(rp_nat)
    rps_nat_.append(rps_nat)
    tp_nat_.append(tp_nat)
    tps_nat_.append(tps_nat)
    dps_nat_.append(dps_nat)
    alt_nat_.append(alt_nat)
    
plt.rc('xtick', labelsize = 18)
plt.rc('ytick', labelsize = 18)
plt.figure(figsize=(20,8))
plt.subplot(1,3,1)
CDF(alt_nat_[0],alt_for_[0],"CDF of latency in 500k pps with "+flow_num_str[0]+" flows","latency (us) ")
plt.subplot(1,3,2)
CDF(alt_nat_[4],alt_for_[4],"CDF of latency in 500k pps with "+flow_num_str[4]+" flows","latency (us) ")
plt.subplot(1,3,3)
CDF(alt_nat_[6],alt_for_[6],"CDF of latency in 500k pps with "+flow_num_str[6]+" flows","latency (us) ")
plt.savefig("/Users/user/Desktop/cdf_udp1.png", dpi=200)
plt.show()
plt.close()
plt.figure(figsize=(20,8))
plt.subplot(1,3,1)
CDF(alt_nat_[7],alt_for_[7],"CDF of latency in 500k pps with "+flow_num_str[7]+" flows","latency (us) ")
plt.subplot(1,3,2)
CDF(alt_nat_[8],alt_for_[8],"CDF of latency in 500k pps with "+flow_num_str[8]+" flows","latency (us) ")
plt.subplot(1,3,3)
CDF(alt_nat_[9],alt_for_[9],"CDF of latency in 500k pps with "+flow_num_str[9]+" flows","latency (us) ")
plt.savefig("/Users/user/Desktop/cdf_udp2.png", dpi=200)
plt.show()
plt.close()




    
#print np.array(alt_nat['0'])
x=range(0,len(flow_num_str))
plt.rc('xtick', labelsize = 12)
plt.rc('ytick', labelsize = 12)
plt.errorbar(x,alt_for_aver, alt_for_div,label="Error bars plot without NAT",fmt="rs-",linewidth=1,elinewidth=3,capsize=4)
plt.ylim(0,4000)
plt.xticks(x, flow_num_str)


plt.errorbar(x,alt_nat_aver, alt_nat_div,label="Error bars plot with NAT",fmt="bs--",linewidth=1,elinewidth=1,capsize=4)
plt.ylim(0,4000)
plt.xticks(x, flow_num_str)
plt.legend(loc=2)
plt.title("Error bar of UDP")
plt.xlabel("flow number")
plt.ylabel("us")
plt.savefig("/Users/user/Desktop/errorbar_udp.png", dpi=200)
plt.show()
plt.close()

plt.figure(figsize=(10,10))
x=range(0,len(flow_num_str))
plt.rc('xtick', labelsize = 12)
plt.rc('ytick', labelsize = 12)
plt.errorbar(x,rx_for_aver, rx_for_div,label="Error bars plot without NAT",fmt="rs-",linewidth=1,elinewidth=3,capsize=4)
#plt.ylim(0,4000)
plt.xticks(x, flow_num_str)

plt.errorbar(x,rx_nat_aver, rx_nat_div,label="Error bars plot with NAT",fmt="bs--",linewidth=1,elinewidth=1,capsize=4)
plt.ylim(0,300)
plt.xticks(x, flow_num_str)
plt.legend(loc=2)
plt.title("Error bar of UDP")
plt.xlabel("flow number")
plt.ylabel("Mb/s")
plt.savefig("/Users/user/Desktop/errorbar_throughput_udp.png", dpi=200)
plt.show()
plt.close()
