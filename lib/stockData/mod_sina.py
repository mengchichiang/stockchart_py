import requests
from pyquery import PyQuery as pq

from dateutil.parser import parse
import datetime
import pytz
import csv
import time
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil
import lib.stockData.util as stockDataUtil

########### get data from sina Start  ###################
#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 新浪網
#可查港股 
def getHistorical_sina(stockId, marketType, startDate, endDate):
  from fake_useragent import UserAgent
  ua = UserAgent()
  sinaHistoryUrl="http://stock.finance.sina.com.cn/hkstock/history/" + stockId +".html"
  print(sinaHistoryUrl)
  startDate_year=parse(startDate).strftime("%Y")
  startDate_month=parse(startDate).strftime("%m")
  startDate_day=parse(startDate).strftime("%-1d")
  startDateStr= startDate_month + '+' + startDate_day + '+' + startDate_year
  endDate_year=parse(endDate).strftime("%Y")
  endDate_month=parse(endDate).strftime("%m")
  endDate_day=parse(endDate).strftime("%-1d")  
  endDateStr= endDate_month + '+' + endDate_day + '+' + endDate_year
  #print(startDateStr + " to " + endDateStr)
  result=[]
  for qryYear in list(range(int(startDate_year),int(endDate_year)+1,1)):
    for qrySeason in list(range(1,int((int(startDate_month)-1)/3)+2,1)):
      #print(str(qryYear) + "-" + str(qrySeason))
      payload = {
      "year":str(qryYear),
      "season":str(qrySeason)
      }
      #print(payload)
      user_agent = ua.random
      headers = {'user-agent': user_agent}
      #headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      res = requests.post(sinaHistoryUrl, data = payload, headers=headers)
      doc=pq(res.text)
      time.sleep(1)
      historyTable=doc("table")
      tr=historyTable.filter("table tbody tr")
      lentr=historyTable.filter("table tbody tr").length
      #print(tr)     
      for index in range(1,lentr,1):   #index=0為欄位名稱
        #print("##########index=" + str(index))
        strDate =tr.eq(index).children("td").eq(0).text() #date, format 104/1/1
        strOpen =tr.eq(index).children("td").eq(6).text().replace(",","") #open
        strHigh =tr.eq(index).children("td").eq(7).text().replace(",","") #high
        strLow  =tr.eq(index).children("td").eq(8).text().replace(",","") #low
        strClose=tr.eq(index).children("td").eq(1).text().replace(",","") #close 
        strVolume =tr.eq(index).children("td").eq(4).text().replace(",","") #volume
        strDate1 =parse(strDate).strftime("%Y-%m-%d")
        strVolume1=str(int(float(strVolume)))
        data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
  return result
########### get data from sina End  ###################

