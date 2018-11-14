# -*- coding: utf-8 -*-
"""
Created on Thu Oct 18 13:25:37 2018

@author: Lida
"""
from __future__ import division
import numpy as np
import pylab as plt
#import matplotlib as plt
import seaborn as sns
import pandas as pd


protocol_name = "tcp"
data_type = "latency"
flow_num_str=['1','100','200','300','400','500','600','700','800','900','1000','1100','1200','1300',\
'1400','1500','1600','1700','1800','1900','2000','2100','2200','2300','2400','2500']

flow_num=[]

for i in range(26):
    flow_num.append(1)
    
fileName_for=[]
fileName_nat=[]
for i in range(len(flow_num_str)):
    fileName_for.append(data_type + "_nat_" +flow_num_str[i]+".csv")
    fileName_nat.append(data_type + "_for_" +flow_num_str[i]+".csv")


def Readfile(Filename):
    data_df=pd.read_csv(Filename,usecols=['0'])
    
    latency=np.array(data_df)
    data_lst=latency.tolist()
    data_aver=np.mean(latency)
    data_std=np.std(latency)
    data_25=np.percentile(latency,25)
    data_75=np.percentile(latency,75) 
    data_adjust=[]
    for i in range(len(data_lst)):
        if data_lst[i]<(data_75+1.5*(data_75-data_25))and data_lst[i]>(data_25-1.5*(data_75-data_25)):
            data_adjust.append(data_lst[i])
        
    data_ad_avr=np.mean(data_adjust)
    data_ad_std=np.std(data_adjust)
    
    
    return data_lst, data_aver, data_std,data_adjust,data_ad_avr,data_ad_std
    

    

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
    plt.rc('xtick', labelsize = 18)
    plt.rc('ytick', labelsize = 18)
    plt.plot(bin_edges[1:],cdf,label="With NAT",color="blue")
    plt.scatter([x1], [0.5], s=20, color="blue")
    plt.annotate("("+str(int(x1))+" , 0.5)",
                 xy=(x1, 0.5),
                 xytext=(x1+100, 0.45),# 在(3.3, 0)上做标注
                 fontsize=18,          # 设置字体大小为 16
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    # xycoords='data' 是说基于数据的值来选位置
    plt.scatter([x2], [0.9], s=20, color="blue")
    plt.annotate("("+str(int(x2))+" , 0.9)",
                 xy=(x2, 0.9), 
                 xytext=(x2-100, 0.8),           # 在(3.3, 0)上做标注
                 fontsize=18,          # 设置字体大小为 16
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    # xycoords='data' 是说基于数据的值来选位置



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
                 xytext=(x1+200, 0.55),            # 在(3.3, 0)上做标注
                 fontsize=18,          # 设置字体大小为 16
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    # xycoords='data' 是说基于数据的值来选位置
    plt.scatter([x2], [0.9], s=20, color="orange")
    plt.annotate("("+str(int(x2))+" , 0.9)",
                 xy=(x2, 0.9),
                 xytext=(x2-400, 0.95),            # 在(3.3, 0)上做标注
                 fontsize=18,          # 设置字体大小为 16
                 xycoords='data',
                 arrowprops=dict(arrowstyle="->"))    # xycoords='data' 是说基于数据的值来选位置

    
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

Laten_list_nat=[]
laten_avr_nat=[]
laten_std_nat=[] 
Laten_list_for=[]
laten_avr_for=[]
laten_std_for=[] 
Laten_list_ad_nat=[]
laten_avr_ad_nat=[]
laten_std_ad_nat=[] 
Laten_list_ad_for=[]
laten_avr_ad_for=[]
laten_std_ad_for=[]  
for i in range(len(flow_num_str)):
    lat_lst_nat,lat_avr_nat,lat_std_nat,lat_lst_ad_nat,lat_avr_ad_nat,lat_std_ad_nat=Readfile(fileName_nat[i])
    Laten_list_nat.append(lat_lst_nat)
    laten_avr_nat.append(lat_avr_nat)
    laten_std_nat.append(lat_std_nat)
    Laten_list_ad_nat.append(lat_lst_ad_nat)
    laten_avr_ad_nat.append(lat_avr_ad_nat)
    laten_std_ad_nat.append(lat_std_ad_nat)
    lat_lst_for,lat_avr_for,lat_std_for,lat_lst_ad_for,lat_avr_ad_for,lat_std_ad_for=Readfile(fileName_for[i])
    Laten_list_for.append(lat_lst_for)
    laten_avr_for.append(lat_avr_for)
    laten_std_for.append(lat_std_for)
    Laten_list_ad_for.append(lat_lst_ad_for)
    laten_avr_ad_for.append(lat_avr_ad_for)
    laten_std_ad_for.append(lat_std_for)

  
plt.rc('xtick', labelsize = 18)
plt.rc('ytick', labelsize = 18)
plt.figure(figsize=(20,8))
plt.subplot(1,3,1)
CDF(Laten_list_nat[0],Laten_list_for[0],"CDF of latency in 200k pps with "+flow_num_str[0]+" flows","latency (us) ")
plt.subplot(1,3,2)
CDF(Laten_list_nat[1],Laten_list_for[1],"CDF of latency in 200k pps with "+flow_num_str[1]+" flows","latency (us) ")
plt.subplot(1,3,3)
CDF(Laten_list_nat[2],Laten_list_for[2],"CDF of latency in 200k pps with "+flow_num_str[2]+" flows","latency (us) ")
plt.savefig("/Users/user/Desktop/plot/cdf_udp.png", dpi=200)
plt.show()
plt.close()
plt.figure(figsize=(20,8))
plt.subplot(1,3,1)
CDF(Laten_list_nat[3],Laten_list_for[3],"CDF of latency in 200k pps with "+flow_num_str[3]+" flows","latency (us) ")
plt.subplot(1,3,2)
CDF(Laten_list_nat[4],Laten_list_for[4],"CDF of latency in 200k pps with "+flow_num_str[4]+" flows","latency (us) ")
plt.subplot(1,3,3)
CDF(Laten_list_nat[5],Laten_list_for[5],"CDF of latency in 200k pps with "+flow_num_str[5]+" flows","latency (us) ")
plt.savefig("/Users/user/Desktop/plot/cdf_udp_1.png", dpi=200)
plt.show()
plt.close()


plt.figure(figsize=(20,6))
x=range(0,len(flow_num_str))
plt.rc('xtick', labelsize = 12)
plt.rc('ytick', labelsize = 12)
plt.plot(x,laten_avr_nat,label="Error bars plot without NAT",color="r",linewidth=1,)
plt.xticks(x, flow_num_str)


plt.plot(x,laten_avr_for,label="Error bars plot with NAT",color="b",linewidth=1)
plt.xticks(x, flow_num_str)
plt.legend(loc=2)
plt.title("initial latency of UDP")
plt.xlabel("flow number")
plt.ylabel("us")
plt.savefig("/Users/user/Desktop/plot/initial_latency_udp.png", dpi=200)
plt.show()
plt.close()

plt.figure(figsize=(20,6))
x=range(0,len(flow_num_str))
plt.rc('xtick', labelsize = 12)
plt.rc('ytick', labelsize = 12)
plt.plot(x,laten_avr_ad_nat,label="Error bars plot without NAT",color="r",linewidth=1)
plt.xticks(x, flow_num_str)


plt.plot(x,laten_avr_ad_for,label="Error bars plot with NAT",color="b",linewidth=1)
plt.xticks(x, flow_num_str)
plt.legend(loc=2)
plt.title("initial latency of UDP")
plt.xlabel("flow number")
plt.ylabel("us")
plt.savefig("/Users/user/Desktop/plot/initial_latency_udp.png", dpi=200)
plt.show()
plt.close()

plt.figure(figsize=(20,6))
x=range(0,len(flow_num_str))
plt.rc('xtick', labelsize = 12)
plt.rc('ytick', labelsize = 12)
plt.errorbar(x,laten_avr_ad_nat,laten_std_ad_nat,label="Error bars plot without NAT",fmt="rs-",linewidth=1,elinewidth=3,capsize=4)
plt.xticks(x, flow_num_str)


plt.errorbar(x,laten_avr_ad_for,laten_std_ad_for,label="Error bars plot with NAT",fmt="bs--",linewidth=1,elinewidth=1,capsize=4)
plt.xticks(x, flow_num_str)
plt.legend(loc=2)
plt.title("initial latency of UDP")
plt.xlabel("flow number")
plt.ylabel("us")
plt.savefig("/Users/user/Desktop/plot/initial_latency_udp.png", dpi=200)
plt.show()
plt.close()