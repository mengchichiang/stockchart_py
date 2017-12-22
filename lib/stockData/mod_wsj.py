import requests
from pyquery import PyQuery as pq

from dateutil.parser import parse
import datetime
import pytz
import csv
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil
import lib.stockData.util as stockDataUtil

########### get data from wsj  Start  ###################
#資料來源: The Wall Street Journal
#可查美股, 台股上市, 港股
#格式：美股, 下載CSV, http://quotes.wsj.com/AAPL/historical-prices/download?MOD_VIEW=page&num_rows=90&range_days=90&startDate=09/05/2017&endDate=12/04/2017
#格式：台股, 下載CSV, http://quotes.wsj.com/TW/XTAI/2330/historical-prices/download?MOD_VIEW=page&num_rows=90&range_days=90&startDate=09/05/2017&endDate=12/04/2017
#格式：港股, 下載CSV, http://quotes.wsj.com/HK/XHKG/0001/historical-prices/download?MOD_VIEW=page&num_rows=90&range_days=90&startDate=09/05/2017&endDate=12/04/2017

def getHistorical_wsj(stockId, marketType, startDate, endDate):
  if marketType=="US":
    stockIdQry=stockId
  if marketType=="TW":
    stockIdQry="TW/XTAI/" + stockId
  if marketType=="HK":
    stockIdQry="HK/XHKG/" + '{:0>4}'.format(stockId)
  if marketType=="CUS":
    stockIdQry=stockId
  startDate_year=parse(startDate).strftime("%Y")
  startDate_month=parse(startDate).strftime("%m")
  startDate_day=parse(startDate).strftime("%d")
  startDateStr= startDate_month + '/' + startDate_day + '/' + startDate_year
  endDate_year=parse(endDate).strftime("%Y")
  endDate_month=parse(endDate).strftime("%m")
  endDate_day=parse(endDate).strftime("%d")  
  endDateStr= endDate_month + '/' + endDate_day + '/' + endDate_year
  #print(startDateStr + " to " + endDateStr)
  result=[]
  wsjHistoryUrl =  ( "http://quotes.wsj.com/" + stockIdQry + "/historical-prices/download?MOD_VIEW=page&num_rows=350&range_days=350&" +
                                    "startDate=" + startDateStr  + "&endDate="  + endDateStr )
  headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
  print(wsjHistoryUrl)
  res = requests.get(wsjHistoryUrl)
  ary=res.text.splitlines()
  #print(ary)
  if len(ary)== 1: #Try symbol is etf
    wsjHistoryUrl =  ( "http://quotes.wsj.com/etf/" + stockIdQry + "/historical-prices/download?MOD_VIEW=page&num_rows=350&range_days=350&" +
                                    "startDate=" + startDateStr  + "&endDate="  + endDateStr )
    headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
    print(wsjHistoryUrl)
    res = requests.get(wsjHistoryUrl)
    ary=res.text.splitlines()
    #print(ary)
  del ary[0]
  cr = csv.reader(ary)
  ary1 = list(cr)
  #print(ary1)
  for row in ary1:
      if len(row)==6:  #stock data
        strDate=row[0].replace("＊","") #date
        strOpen=row[1].replace(",","") #open
        strHigh=row[2].replace(",","") #high
        strLow=row[3].replace(",","") #Low
        strClose=row[4].replace(",","") #Close
        strVolume=row[5].replace(",","") #volume
        strDate1 =parse(strDate).strftime("%Y-%m-%d")
        #print(strDate1)
        strVolume1=str(int(float(strVolume)))
        data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
      if len(row)==5:  #index data, no volume data
        strDate=row[0].replace("＊","") #date
        strOpen=row[1].replace(",","") #open
        strHigh=row[2].replace(",","") #high
        strLow=row[3].replace(",","") #Low
        strClose=row[4].replace(",","") #Close
        strVolume="0"  #volume
        strDate1=parse(strDate).strftime("%Y-%m-%d")
        strVolume1=str(int(float(strVolume)))
        data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
  return result

########### get data from wsj  End  ###################
