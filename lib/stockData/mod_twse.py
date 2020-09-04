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

########### get data from twse Start  ###################
#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 台灣證券交易所
#可查台股上市
#下載幾筆資料後會被拒絕連線
def getHistorical_twse(stockId, marketType, startDate, endDate):
  from fake_useragent import UserAgent
  ua = UserAgent()
  startDate_year=parse(startDate).strftime("%Y")
  startDate_month=parse(startDate).strftime("%m")
  startDate_day=parse(startDate).strftime("%d")
  startDateStr= startDate_year + startDate_month + startDate_day
  endDate_year=parse(endDate).strftime("%Y")
  endDate_month=parse(endDate).strftime("%m")
  endDate_day=parse(endDate).strftime("%d")  
  endDateStr= endDate_year + endDate_month + endDate_day
  #print(startDateStr + "to" + endDateStr)
  result=[]
  timestamp1='{:.0f}'.format(datetime.datetime.now().timestamp()*1000)
  for qryYear in list(range(int(startDate_year),int(endDate_year)+1,1)):
    for qryMonth in list(range(int(startDate_month),int(endDate_month)+1,1)):
      date1=str(qryYear) + '{:0>2}'.format(str(qryMonth)) + "01"
      twseHistoryUrl= ("http://www.twse.com.tw/exchangeReport/STOCK_DAY?response=csv" +
                           "&date=" + date1 + "&stockNo=" + stockId )
      print(twseHistoryUrl)
      user_agent = ua.random
      headers = {'user-agent': user_agent}
      #headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      res = requests.post(twseHistoryUrl, headers=headers)
      time.sleep(5)  # sleep=3 will fail, sleep=5 OK
      decoded_content = res.content.decode('Big5')
      #print(decoded_content.splitlines())
      ary=decoded_content.splitlines()
      #print(ary)
      #del ary[0:2]
      ary=ary[2:-5]
      cr = csv.reader(ary)
      ary1 = list(cr)
      #print(ary1)
      for row in ary1:
        if len(row)==10:
          strDate=row[0] #date. date format 109/07/21
          strOpen=row[3].replace(",","") #open
          strHigh=row[4].replace(",","") #high
          strLow=row[5].replace(",","") #Low
          strClose=row[6].replace(",","") #Close
          strVolume=row[1].replace(",","") #volume
          if stockDataUtil.is_date(strDate) == True:
            strDate1 = stockDataUtil.twYear2StandardYear(strDate) # date format change to 19-07-21
            strVolume1=str(int(float(strVolume)))
            data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
            if data!={}: result.append(data)
            #print(data)
  return result

def getHistorical_twse_old(stockId, marketType, startDate, endDate):
  twseHistoryUrl="http://www.twse.com.tw/ch/trading/exchange/STOCK_DAY/STOCK_DAYMAIN.php"
  print(twseHistoryUrl)
  startDate_year=parse(startDate).strftime("%Y")
  startDate_month=parse(startDate).strftime("%m")
  startDate_day=parse(startDate).strftime("%-1d")
  startDateStr= startDate_month + '+' + startDate_day + '+' + startDate_year
  endDate_year=parse(endDate).strftime("%Y")
  endDate_month=parse(endDate).strftime("%m")
  endDate_day=parse(endDate).strftime("%-1d")  
  endDateStr= endDate_month + '+' + endDate_day + '+' + endDate_year
  #print(startDateStr + "to" + endDateStr)
  result=[]
  for qryYear in list(range(int(startDate_year),int(endDate_year)+1,1)):
    for qryMonth in list(range(int(startDate_month),int(endDate_month)+1,1)):
      #print(str(qryYear) + "-" + str(qryMonth))
      payload = {
      "download":"",
      "query_year":str(qryYear),
      "query_month":str(qryMonth),
      "CO_ID":stockId,
      "query-button":"查詢",
      }
      headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      res = requests.post(twseHistoryUrl, data = payload, headers=headers)
      doc=pq(res.text)
      historyTable=doc("table")
      tr=historyTable.filter("table tbody tr")
      lentr=historyTable.filter("table tbody tr").length
      #print(res.text)     
      for index in range(0,lentr,1):
        #print("##########index=" + str(index))
        strDate =tr.eq(index).children("td").eq(0).text() #date, format 104/1/1
        strOpen =tr.eq(index).children("td").eq(3).text().replace(",","") #open
        strHigh =tr.eq(index).children("td").eq(4).text().replace(",","") #high
        strLow  =tr.eq(index).children("td").eq(5).text().replace(",","") #low
        strClose=tr.eq(index).children("td").eq(6).text().replace(",","") #close 
        strVolume =tr.eq(index).children("td").eq(1).text().replace(",","") #volume
        strDate1 = parse(stockDataUtil.twYear2StandardYear(strDate)).strftime("%Y-%m-%d")
        strVolume1=str(int(int(strVolume)/1000))
        data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
  return result

########### get data from TWSE End  ###################

