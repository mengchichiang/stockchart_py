import requests
from pyquery import PyQuery as pq

import datetime
import pytz
import csv
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil
import lib.stockData.util as stockDataUtil


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
  dt1 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
  endDt = datetime.datetime.strptime(endDate,"%Y-%m-%d")
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

def parseYahooHistoryHtml(body, stockId):
  doc=pq(body)
  historyTable=doc("table[data-test='historical-prices']")
  #print(historyTable)
  tr=historyTable.filter("table tr")
  lentr=historyTable.filter("table tr").length 
  #print(tr)
  result=[]
  for index in range(1,lentr,1):
    if tr.eq(index).children("td").length == 7:
      #print("##########index=" + str(index))
      strDate =tr.eq(index).children("td").eq(0).text() #date
      strOpen =tr.eq(index).children("td").eq(1).text().replace(",","") #open
      strHigh =tr.eq(index).children("td").eq(2).text().replace(",","") #high
      strLow  =tr.eq(index).children("td").eq(3).text().replace(",","") #low
      strClose=tr.eq(index).children("td").eq(4).text().replace(",","") #close 
      strAdj  =tr.eq(index).children("td").eq(5).text().replace(",","") #Adj close* 
      strVolume =tr.eq(index).children("td").eq(6).text().replace(",","") #volume
      data=stockDataUtil.filterHistoryData(stockId, strDate, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
      #print(data)
  return result

########### get data from yahoo  End###################