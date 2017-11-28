import requests
from pyquery import PyQuery as pq

from dateutil.parser import parse
import datetime
import pytz
import csv
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil

def is_date(string):
  try: 
    parse(string)
    return True
  except ValueError:
    return False

def is_number(string):
  try: 
    float(string)
    return True
  except ValueError:
    return False

#converter TW year to AD year
def twYear2StandardYear(strDate):  
  strDate1= strDate.split("/")
  strDate2 = str(int(strDate1[0])+1911) + '-' + strDate1[1] + '-' + strDate1[2]
  return strDate2

########### database operate session start ###################

def saveHistoryData(stockId, quotes, tableName):
  setattr(HistoryData._meta, "db_table", tableName)
  HistoryData.create_table(True) #argument=True: create table if table not exist.
  for quote in quotes:
    #print(quote)
    dictQuote={"date":quote["date"],"open":quote["open"],"high":quote["high"],"low":quote["low"],"close":quote["close"],"volume":quote["volume"],"stockid":stockId}
    qry=HistoryData.select().where(HistoryData.date==quote["date"], HistoryData.stockid==stockId).first()
    if qry != None:
      q=HistoryData.update(**dictQuote).where(HistoryData.date==quote["date"], HistoryData.stockid==stockId) #with composite key
      #q=HistoryData.update(**dictQuote).where(HistoryData.id == qry.id) #without specify primary_key.
      q.execute()
    else:
      q=HistoryData.insert(**dictQuote)
      q.execute()
    #Check Duplicate data
    qryCount=HistoryData.select().where(HistoryData.date==quote["date"], HistoryData.stockid==stockId).count()
    if qryCount > 1:
      print("ERROR! Duplicate history data.")

def loadHistoryData(stockId, tableName):
  result=[]
  setattr(HistoryData._meta, "db_table", tableName)
  for data in HistoryData.select().where(HistoryData.stockid==stockId):
    data1= { "date":data.date, "open":data.open, "high":data.high, "low":data.low, "close":data.close, "volume":int(data.volume), "stockId":stockId }
    result.append(data1)
  return result

########### database operate session End ###################

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

def filterHistoryData(stockId, strDate, strOpen, strHigh, strLow, strClose, strVolume):
  if is_date(strDate) == True and is_number(strClose) == True and float(strClose) != 0:
    if is_number(strOpen) == False:
      strOpen=strClose 
    if is_number(strHigh) == False:
      strHigh=strClose
    if is_number(strLow) == False:
      strLow=strClose 
    if is_number(strVolume) == False:
      strVolume="0" 
    return {"date":strDate,"open":strOpen,"high":strHigh,"low":strLow,"close":strClose,"volume":strVolume, "stockId":stockId}
  else:
    return {}

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
      data=filterHistoryData(stockId, strDate, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
      #print(data)
  return result

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
      data=filterHistoryData(stockId, strDate, strOpen, strHigh, strLow, strClose, strVolume)
      if data!={}: result.append(data)
      #print(data)
  return result

#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 台灣證券交易所
def getHistorical_twse(stockId, marketType, startDate, endDate):
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
      headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      res = requests.post(twseHistoryUrl, headers=headers)
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
          strDate=row[0] #date
          strOpen=row[3].replace(",","") #open
          strHigh=row[4].replace(",","") #high
          strLow=row[5].replace(",","") #Low
          strClose=row[6].replace(",","") #Close
          strVolume=row[1].replace(",","") #volume
          if is_date(strDate) == True:
            strDate1 = twYear2StandardYear(strDate)
            strVolume1=str(int(strVolume))
            data=filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
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
      print(res.text)     
      for index in range(0,lentr,1):
        #print("##########index=" + str(index))
        strDate =tr.eq(index).children("td").eq(0).text() #date, format 104/1/1
        strOpen =tr.eq(index).children("td").eq(3).text().replace(",","") #open
        strHigh =tr.eq(index).children("td").eq(4).text().replace(",","") #high
        strLow  =tr.eq(index).children("td").eq(5).text().replace(",","") #low
        strClose=tr.eq(index).children("td").eq(6).text().replace(",","") #close 
        strVolume =tr.eq(index).children("td").eq(1).text().replace(",","") #volume
        strDate1 = twYear2StandardYear(strDate)
        strVolume1=str(int(int(strVolume)/1000))
        data=filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
  return result

#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 證券櫃檯買賣中心
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
          if is_date(strDate) == True:
            strDate1 = twYear2StandardYear(strDate)
            strVolume1=str(int(strVolume))
            data=filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
            if data!={}: result.append(data)
            #print(data)
  return result

#startDate and endDate the same is year, and return full month data, it ingore end day.
#資料來源: 新浪網
def getHistorical_sina(stockId, marketType, startDate, endDate):
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
      headers={'User-Agent':'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/47.0.2526.73 Safari/537.36'}
      res = requests.post(sinaHistoryUrl, data = payload, headers=headers)
      doc=pq(res.text)
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
        strVolume1=str(int(strVolume))
        data=filterHistoryData(stockId, strDate1, strOpen, strHigh, strLow, strClose, strVolume1)
        if data!={}: result.append(data)
        #print(data)
  return result
