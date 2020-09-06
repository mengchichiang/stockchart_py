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

########### get data from wsj  Start  ###################
#資料來源: The Wall Street Journal
#可查美股, 台股上市, 港股

def getHistorical_wsj(stockId, marketType, startDate, endDate):
  from fake_useragent import UserAgent
  ua = UserAgent()
  result=[]
  if marketType=="US":
    stockIdQry=stockId
    country="US"
  elif marketType=="TW":
    stockIdQry=stockId
    country="TW"
  elif marketType=="HK":
    stockIdQry='{:0>4}'.format(stockId)
    country="HK"
  else:
    stockIdQry=stockId
    country=marketType
  dt1 = datetime.datetime.strptime(startDate,"%Y-%m-%d")
  endDt = datetime.datetime.strptime(endDate,"%Y-%m-%d")
  intervalDt = datetime.timedelta(days=50)
  if (dt1 + intervalDt)> endDt:
    dt2=endDt
  else:
    dt2=dt1 + intervalDt
  while dt1 <= endDt:
    #print("dt1=" + str(dt1) + "dt2=" + str(dt2))
    dt1Str= dt1.strftime("%Y")+ '/' + dt1.strftime("%m")+ '/' + dt1.strftime("%d")
    dt2Str= dt2.strftime("%Y")+ '/' + dt2.strftime("%m")+ '/' + dt2.strftime("%d")
    wsjHistoryUrl =  ( "https://www.wsj.com/market-data/quotes/ajax/historicalprices/8/" + stockIdQry + "?MOD_VIEW=page&ticker=" + stockIdQry +

                     "&country=" + country  + "&instrumentType=STOCK&num_rows=90&range_days=90&"
                                    + "startDate=" + dt1Str + "&endDate="  + dt2Str )
    print(wsjHistoryUrl)
    user_agent = ua.random
    headers = {'user-agent': user_agent}
    res = requests.get(wsjHistoryUrl,headers=headers)
    #print(res.text)
    time.sleep(1)
    statusCode = res.status_code
    if statusCode == 200:
      data=parseWsjHistoryHtml(res.text, stockId)
      result.extend(data)
      dt1=dt2 + datetime.timedelta(days=1) 
      if (dt1 + intervalDt)> endDt:
        dt2=endDt
      else:
        dt2=dt1 + intervalDt
    else:
      return result
  return result



def parseWsjHistoryHtml(body, stockId):
  result=[]
  doc=pq(body)
  historyTable=doc("table[class=cr_dataTable]").eq(1)
  #print(historyTable)
  tr=historyTable.filter("table tbody tr")
  lentr=historyTable.filter("table tbody tr").length 
  #print(tr)
  for index in range(0,lentr,1):
    if tr.eq(index).children("td").length == 6:
      #print("##########index=" + str(index))
      strDate =tr.eq(index).children("td").eq(0).text() #date. date format "Jul 23, 2020"
      strOpen =tr.eq(index).children("td").eq(1).text().replace(",","") #open
      strHigh =tr.eq(index).children("td").eq(2).text().replace(",","") #high
      strLow  =tr.eq(index).children("td").eq(3).text().replace(",","") #low
      strClose=tr.eq(index).children("td").eq(4).text().replace(",","") #close 
      strVolume =tr.eq(index).children("td").eq(5).text().replace(",","") #volume
      strDate1 = parse(strDate).strftime('%Y-%m-%d')
      data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
  return result

