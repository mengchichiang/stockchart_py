import requests
from pyquery import PyQuery as pq

from dateutil.parser import parse
import datetime
import pytz
import csv
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil
import lib.stockData.util as stockDataUtil

########### get data from google Start  ###################
#資料來源: google
#可查美股, 台股上市, 港股
def transfer2googleStockId(stockId,marketType):
  if marketType=="US":
    googleStockId=stockId
  if marketType=="TW":
    googleStockId="TPE:" + stockId
  if marketType=="HK":
    googleStockId="HKG:" + '{:0>4}'.format(stockId)
  if marketType=="CUS":
    googleStockId=stockId
  return(googleStockId)

def getCid_google(stockId):
  googleFinanceUrl = "http://www.google.com/finance/historical?q="  + stockId
  print(googleFinanceUrl)
  res = requests.get(googleFinanceUrl)
  doc=pq(res.text)
  cid = doc('input[name="cid"]').attr("value")
  
  
""" 
 HTTP get request format of download history data from goolgle. Both format have been try to download sucessfuly.
 1. with  cid number (Failed after 2017/6/7)
 "http://www.google.com/finance/historical?cid=xxxx&startdate=xxx&enddate=xxx&start=0&num=100"
 2. with q=xxxx
 "http://www.google.com/finance/historical?q=xxxx&startdate=xxx&enddate=xxx&start=0&num=100"
"""

def getHistorical_google(stockId, marketType, startDate, endDate): #return key:value
  result=[]
  googleStockId=transfer2googleStockId(stockId,marketType)
  #print(googleStockId)
  #cid=getCid_google(googleStockId)
  #if cid == None:
  #  return []
  dt1 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
  endDt = datetime.datetime.strptime(endDate,"%Y-%m-%d")
  intervalDt = datetime.timedelta(days=50)
  if (dt1 + intervalDt)> endDt:
    dt2=endDt
  else:
    dt2=dt1 + intervalDt
  while dt1 <= endDt:
    #print("dt1=" + str(dt1) + "dt2=" + str(dt2))
    dt1Str= dt1.strftime("%b")+ '+' + dt1.strftime("%-1d")+ '+' + dt1.strftime("%Y")
    dt2Str= dt2.strftime("%b")+ '+' + dt2.strftime("%-1d")+ '+' + dt2.strftime("%Y")
    #googleFinanceUrl = "http://www.google.com/finance/historical?cid="  + cid +"&startdate="+dt1Str+"&enddate="+dt2Str+"&start=0&num=100"
    googleFinanceUrl = "http://www.google.com/finance/historical?q=" + googleStockId +"&startdate="+dt1Str+"&enddate="+dt2Str+"&start=0&num=100"
    print(googleFinanceUrl)
    res = requests.get(googleFinanceUrl)
    statusCode = res.status_code
    #print(res.text)
    if statusCode == 200:
      data=parseGoogleHistoryHtml(res.text, stockId)
      result.extend(data)
      dt1=dt2 + datetime.timedelta(days=1) 
      if (dt1 + intervalDt)> endDt:
        dt2=endDt
      else:
        dt2=dt1 + intervalDt
    else:
      return result
  return result

def parseGoogleHistoryHtml(body, stockId):
  doc=pq(body)
  historyTable=doc("table.gf-table.historical_price")
  tr=historyTable.filter("table tr")
  lentr=historyTable.filter("table tr").length
  #print(tr)
  result=[]
  for index in range(1,lentr,1):
    if tr.eq(index).children("td").length == 6:
      #print("##########index=" + str(index))
      strDate =tr.eq(index).children("td").eq(0).text() #date
      strOpen =tr.eq(index).children("td").eq(1).text().replace(",","") #open
      strHigh =tr.eq(index).children("td").eq(2).text().replace(",","") #high
      strLow  =tr.eq(index).children("td").eq(3).text().replace(",","") #low
      strClose=tr.eq(index).children("td").eq(4).text().replace(",","") #close 
      strVolume =tr.eq(index).children("td").eq(5).text().replace(",","") #volume
      data=stockDataUtil.filterHistoryData(stockId, strDate, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
      #print(data)
  return result

########### get data from google End  ###################

