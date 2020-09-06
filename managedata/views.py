import os
curDir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(curDir)
#print(PROJECT_ROOT)
import sys
#sys.path.append(PROJECT_ROOT) #add module search path
#print(sys.path)

from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockData as stockData
import lib.stockUtil as stockUtil

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
import json
import re
import datetime

pollMsgQueue=[]

def downloadDataHistory(stockId, marketType):
  #dictText=StockInfo.select(StockInfo.history_info).where(StockInfo.stockid == stockId, StockInfo.markettype == marketType)
  qry=StockInfo.select().where(StockInfo.stockid == stockId, StockInfo.markettype == marketType).first()
  if qry==None:
    q=StockInfo.insert(stockid=stockId,markettype=marketType,history_info="{'DoneYear':[]}", finance_info="{}")
    q.execute()
    qry=StockInfo.select().where(StockInfo.stockid == stockId, StockInfo.markettype == marketType).first()
  historyInfoDict=stockUtil.evalTextDict(qry.history_info)
  historyDoneYearAry=historyInfoDict["DoneYear"]
  #print(historyInfoDict)
  now=datetime.datetime.now()
  currentDate=now.strftime("%Y-%m-%d")
  currentYear=now.strftime("%Y")
  rangeYears  = stockUtil.read_config("stockData.history","rangeYears")
  fromYear = str(int(currentYear) - int(rangeYears) + 1)
  toYear = currentYear
  print(stockId + " is being processed.")
  pollMsgQueue.append(stockId + " downloading...")
  for i in range(int(fromYear), int(toYear)+1):
    startDate = str(i) + "-01-01"
    endDate = str(i) + "-12-31"
    print("processing year " + str(i) + "...")
    #print(historyDoneYearAry)
    if str(i) not in  historyDoneYearAry:
      if str(i) == currentYear:
        setattr(HistoryData._meta, "db_table", "history_" + marketType.lower())
        lastData=HistoryData.select().where(HistoryData.stockid==stockId).order_by(HistoryData.date.desc()).first()
        #print(lastData.date.year)
        if lastData != None and lastData.date.strftime("%Y") == currentYear:
          startDate=(lastData.date + datetime.timedelta(days=1)).strftime("%Y-%m-%d")
        endDate = currentDate
      print("Download " + stockId + " from " + startDate + " to " + endDate)
      marketId=stockUtil.getMarketId(marketType, stockId)
      #print("marketId:" + marketId)
      source=stockUtil.getSourceFromCustomCSV(marketType, stockId) #get source from custom table
      if source==None: #get source from config.ini
        if marketType in ["US","TW","HK"]:
          sourceDict=stockUtil.evalTextDict(stockUtil.read_config("stockData.history","source_" + marketType))
          #print(sourceDict)
          #print("getHistorical_" + sourceDict[marketId].lower())
          #print(marketType.lower())
          source=sourceDict[marketId].lower()
      if source!=None: #get history data from source
        #print("Download from source:" + source)
        #getHistorical = getattr(stockData,"getHistorical_" + source)
        getHistorical = stockData.get_func_from_modStockData("getHistorical_" + source, source)
        quotes=getHistorical(stockId, marketType, startDate, endDate)  
        stockData.saveHistoryData(stockId, quotes, "history_" + marketType.lower())
        #print(quotes)
        if str(i) != currentYear:
          historyDoneYearAry.append(str(i))
          q=StockInfo.update(history_info={'DoneYear':historyDoneYearAry}).where(StockInfo.id==qry.id)
          q.execute()
  
def downloadDataFinancial(stockId, marketType):
  now=datetime.datetime.now()
  currentDate=now.strftime('%Y-%m-%d')
  currentYear=now.strftime("%Y")
  rangeYears  = stockUtil.read_config("stockData.history","rangeYears")
  fromYear = str(int(currentYear) - int(rangeYears) + 1)
  toYear = currentYear
  for i in range(int(fromYear), int(toYear)+1):
    startDate = str(i) + "-01-01"
    endDate = str(i) + "-12-31"
    if i == int(currentYear):
      endDate = currentDate

def downloadData(pfGroup):
  qry = Portfolio.select().where(Portfolio.group == pfGroup).order_by(Portfolio.index)
  for item in qry:
    stockArray = stockUtil.evalTextArray(item.stock_array)
    for stock in stockArray:
      for i in range(0,2):
        try:
          downloadDataHistory(stock["stockId"], stock["marketType"])
          #downloadDataFinancial(stock["stockId"], stock["marketType"])
        except Exception as e:
          print("Unexpected error:", sys.exc_info()[0]) #print error type
          print(str(e))#print error message         
          continue #skip "break" instruction
          #raise
        break  #let stock be donload only 1 time if no exception.
  pollMsgQueue.append("History data download complete.")
         
def root_vf(request):
    return render(request, "manageData.html")

@csrf_exempt
def downloadData_vf(request):
  pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
  if request.method == "GET":
    return render(request, "downloadData.html", {"pfGroupArray":pfGroupArray})
  else:
    for pfGroup in pfGroupArray:
      if request.POST.get("select" + pfGroup) == 'on':
        downloadData(pfGroup)
  return HttpResponse()

@csrf_exempt
def status_vf(request): #ajax post
  response = HttpResponse()
  while pollMsgQueue !=[]:
    item = pollMsgQueue[0]
    response.write(item + "<BR>")
    del pollMsgQueue[0]
  return response

def cleanData():
  pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
  allPfArray=[]  #collect all portfolio to allPfArray
  for pfGroup in pfGroupArray:
    qry = Portfolio.select().where(Portfolio.group == pfGroup).order_by(Portfolio.index)
    for item in qry:
      stockArray = stockUtil.evalTextArray(item.stock_array)
      for stock in stockArray:
        allPfArray.append(stock)
  #print(allPfArray)         
  #Delete the history data according to stockid not in portfolio.
  for pfGroup in pfGroupArray:
    setattr(HistoryData._meta, "db_table", "history_" + pfGroup.lower())
    data1=HistoryData.select(HistoryData.stockid).distinct().dicts()
    for x in data1:        #pick up stockid of historydata table
      founded=0
      #print(x["stockid"])         
      for y in allPfArray: #look up portfolio
        if pfGroup == y["marketType"] and  x["stockid"] == y["stockId"] :
          founded=1
          break;
      if founded==0:    
        q = HistoryData.delete().where(HistoryData.stockid == x["stockid"])
        q.execute()
  #Delete the stockinfo data according to stockid not in portfolio.
  data1=StockInfo.select().dicts()
  #data1=HistoryData.select(HistoryData.stockid).distinct().dicts()
  for x in data1:        #pick up stockid of historydata table
    founded=0
    #print(x)         
    for y in allPfArray: #look up portfolio
      if x["markettype"] == y["marketType"] and  x["stockid"] == y["stockId"] :
        founded=1
        break;
    if founded==0:    
      q = StockInfo.delete().where(StockInfo.id == x["id"])
      q.execute()
  #Delete old data outside date of range year
  now=datetime.datetime.now()
  currentYear=now.strftime("%Y")
  keepYears  = stockUtil.read_config("stockData.history","keepYears")
  fromYear = str(int(currentYear) - int(keepYears) + 1)
  for pfGroup in pfGroupArray:
    setattr(HistoryData._meta, "db_table", "history_" + pfGroup.lower())
    data1=HistoryData.select(HistoryData.stockid).distinct().dicts()
    q = HistoryData.delete().where(HistoryData.date < fromYear + "-01-01")
    q.execute()
  #update DoneYear in StockInfo table
  qry=StockInfo.select()
  for item in qry:
    historyInfoDict=stockUtil.evalTextDict(item.history_info)
    historyDoneYearAry=historyInfoDict["DoneYear"]
    array1=[]
    for i in historyDoneYearAry:
      if int(i) >= int(fromYear): 
         array1.append(str(i))
    q=StockInfo.update(history_info={'DoneYear':array1}).where(StockInfo.id==item.id)
    q.execute()
     
#Delete the history & stockinfo data according to stockid not in portfolio.
def cleanData_vf(request):
  try:
    cleanData()
  except:
    response = HttpResponse("Clean data fail.")
  else:
    response = HttpResponse("Clean data OK.")
  finally:
    return response

@csrf_exempt
def deleteData_vf(request):
  pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
  if request.method == "GET":
    return render(request, "deleteData.html", {"pfGroupArray":pfGroupArray})
  else:
    for pfGroup in pfGroupArray:
      if request.POST.get("select" + pfGroup) == 'on':
        setattr(HistoryData._meta, "db_table", "history_" + pfGroup.lower())
        q = HistoryData.delete()
        q.execute()
    q = StockInfo.delete()
    q.execute()
    q = ProjectInfo.delete()
    q.execute()
    return HttpResponse("Delete data OK.")


