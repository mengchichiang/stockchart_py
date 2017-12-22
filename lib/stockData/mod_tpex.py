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

########### get data from tpex Start  ###################
#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 證券櫃檯買賣中心
#可查台股上市櫃
#例：下載CSV, "http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_download.php?l=zh-tw&d=100/03&stkno=6121&s=0,asc,0";
def getHistorical_tpex(stockId, marketType, startDate, endDate):
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
      tpexHistoryUrl="http://www.tpex.org.tw/web/stock/aftertrading/daily_trading_info/st43_download.php?l=zh-tw&d=" + \
        str(qryYear-1911) + "/" + str(qryMonth)  +  "&stkno=" + stockId + "&s=0,asc,0";
      headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      print(tpexHistoryUrl)
      res = requests.get(tpexHistoryUrl)
      decoded_content = res.content.decode('Big5')
      #print(decoded_content.splitlines())
      ary=decoded_content.splitlines()
      del ary[0:5]
      ary.pop()
      #print(ary)
      cr = csv.reader(ary)
      ary1 = list(cr)
      #print(ary1)
      for row in ary1:
        if len(row)==9:
          strDate=row[0].replace("＊","") #date
          strOpen=row[3].replace(",","") #open
          strHigh=row[4].replace(",","") #high
          strLow=row[5].replace(",","") #Low
          strClose=row[6].replace(",","") #Close
          strVolume=row[1].replace(",","") #volume
          if stockDataUtil.is_date(strDate) == True:
            strDate1 = stockDataUtil.twYear2StandardYear(strDate)
            strVolume1=str(int(float(strVolume)))
            data=stockDataUtil.filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
            if data!={}: result.append(data)
            #print(data)
      time.sleep(3) 
  return result
########### get data from tpex End  ###################

