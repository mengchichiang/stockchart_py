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

def getHistorical_yahoo1(stockIdQry, stockId, startDate, endDate): #return key:value
  result=[]
  #Use UTC+0 match yahoo finance results. The both result lost the last day data. 
  dt1 = datetime.datetime.strptime(startDate,"%Y-%m-%d").replace(tzinfo=datetime.timezone.utc)
  endDt = datetime.datetime.strptime(endDate,"%Y-%m-%d").replace(tzinfo=datetime.timezone.utc) + datetime.timedelta(days=1)
  intervalDt = datetime.timedelta(days=50)
  if (dt1 + intervalDt)> endDt:
    dt2=endDt
  else:
    dt2=dt1 + intervalDt
  while dt1 <= endDt:
    #print("dt1=" + str(dt1) + "dt2=" + str(dt2))
    yahooFinanceUrl= ( "https://finance.yahoo.com/quote/" + stockIdQry + "/history?" +
                       "period1=" + str(int(dt1.timestamp())) + "&period2=" + str(int(dt2.timestamp())) +
                       "&interval=1d&events=history&crumb=c.GJfe3uHp/" )
    print(yahooFinanceUrl)
    res = requests.get(yahooFinanceUrl)
    time.sleep(1)
    statusCode = res.status_code
    #print(res.text)
    if statusCode == 200:
      data=parseYahooHistoryHtml(res.text, stockId)
      result.extend(data)
      dt1=dt2 + datetime.timedelta(days=1) 
      if (dt1 + intervalDt)> endDt:
        dt2=endDt
      else:
        dt2=dt1 + intervalDt
    else:
      return result
  return result

########### get data from yahoo  Start  ###################
#資料來源: yahoo
#可查美股, 台股上市櫃, 港股
def getHistorical_yahoo(stockId, marketType, startDate, endDate): #return key:value
  result=[]
  if marketType == "TW":
    marketId = stockUtil.getMarketId("TW", stockId)
    stockIdQry = stockId + "." + marketId
  elif marketType == "HK":
    stockIdQry = "{:04d}".format(int(stockId)) + ".HK"
  else:
    stockIdQry = stockId
  result=getHistorical_yahoo1(stockIdQry, stockId, startDate, endDate)
  if result==[] and marketType=="TW": #If marketId is wrong because of out of day CSV file, change marketId to another.
    if marketId=="TW":
      marketId="TWO"
    else:
      marketId="TW"
    stockIdQry = stockId + "." + marketId
    result=getHistorical_yahoo1(stockIdQry, stockId, startDate, endDate)
  return result

def parseYahooHistoryHtml(body, stockId):
  doc=pq(body)
  historyTable=doc("table[data-test='historical-prices']")
  #print(historyTable)
  tr=historyTable.filter("table tbody tr")
  lentr=historyTable.filter("table tbody tr").length 
  #print(tr)
  result=[]
  for index in range(0,lentr,1):
    if tr.eq(index).children("td").length == 7:
      #print("##########index=" + str(index))
      strDate =tr.eq(index).children("td").eq(0).text() #date. date format "Jul 23, 2020"
      strOpen =tr.eq(index).children("td").eq(1).text().replace(",","") #open
      strHigh =tr.eq(index).children("td").eq(2).text().replace(",","") #high
      strLow  =tr.eq(index).children("td").eq(3).text().replace(",","") #low
      strClose=tr.eq(index).children("td").eq(4).text().replace(",","") #close 
      strAdj  =tr.eq(index).children("td").eq(5).text().replace(",","") #Adj close* 
      strVolume =tr.eq(index).children("td").eq(6).text().replace(",","") #volume
      strDate1 = parse(strDate).strftime('%Y-%m-%d')
      data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
  return result

########### get data from yahoo  End###################
