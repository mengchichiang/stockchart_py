import os
curDir = os.path.dirname(os.path.abspath(__file__)) # Do't use curDir. curDir maybe pollute by other import module. Using PROJECT_ROOT for safe
PROJECT_ROOT = os.path.dirname(curDir) # mean cd..
#print(PROJECT_ROOT)

#import sys
#sys.path.append(PROJECT_ROOT) #add module search path
#print(sys.path)

from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockData as stockData
import lib.stockUtil as stockUtil

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.core.serializers.json import DjangoJSONEncoder
import json
import re
import decimal
import datetime

def root_vf(request): #root of portfolio
  pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
  #print(pfGroupArray)
  return HttpResponseRedirect("/portfolio/" + pfGroupArray[0])

def createPortfolio(pfGroup, portfolioName, symbolArray): #market type TW inlculde OTC market.
  stockArray=[];
  if (symbolArray != []):  
    #print(symbolArray)
    for i in range(0,len(symbolArray)):
      stockSymbol=symbolArray[i].strip();
      #print(stockSymbol)
      #the followings copy from addSymbol
      stockSymbol1, marketType = stockUtil.parseInputSymbol(pfGroup, stockSymbol); #If stockSymbol=xxxx__xx, stockSymbol1=xxxxx
      stockName = stockUtil.getStockNameFromCSV(marketType ,stockSymbol1); #Assume input is stockId. if input not in CSV, stockName is set None 
      stockId = stockUtil.getStockIdFromCSV(marketType, stockSymbol1); #Assume input is stockName.  if input not in CSV, stockId is set None
      if stockId==None and stockName!=None:
        stockId=stockSymbol1;  #input is stockId
      if stockId!=None and stockName==None:
        stockName=stockSymbol1;  #input is stockName
      if stockId==None and stockName==None: 
        stockId=stockSymbol1;  #input can't found in csv Table
        stockName=stockId;  #input can't found in csv Table
      #print("stockId:" + stockUtil.cvNone(stockId))
      #print("stockName:" + stockUtil.cvNone(stockName))
      #print("marketType:" + stockUtil.cvNone(marketType))
      #print("stockSymbol1:" + stockUtil.cvNone(stockSymbol1))
      stockArray.append( {"stockId":stockId , "stockName":stockName, "marketType":marketType});
    #print(stockArray);
  pfCount=len(Portfolio.select().where(Portfolio.group  == pfGroup))
  #q=Portfolio.insert({"group":pfGroup, "index":pfCount, "name": portfolioName ,"stock_array":stockArray})
  q=Portfolio.insert(group=pfGroup, index=pfCount, name=portfolioName ,stock_array=stockArray)
  #q=Portfolio.insert({Portfolio.group:pfGroup, Portfolio.index:pfCount, Portfolio.name: portfolioName ,Portfolio.stock_array:stockArray})
  q.execute()

def pfGroup_vf(request,pfGroup):
  return HttpResponseRedirect("/portfolio/" + pfGroup + "/pf0")

def pfGroup_create_vf(request,pfGroup):
  from django import forms
  #print(request)
  if request.method == "GET":
    return render(request, "portfolioGroup_create.html",{'form':forms})
  elif request.method == "POST":
    symbolList=request.POST["symbol"]
    symbolArray=symbolList.strip().upper().replace("\r\n"," ").split()
    createPortfolio(pfGroup, request.POST["pfName"], symbolArray)
    return HttpResponseRedirect("/portfolio/" + pfGroup + "/pf0")

def pfGroup_edit_vf(request,pfGroup):
  return render(request, "portfolioGroup_edit.html")

def pfGroup_reorder_vf(request,pfGroup):
  return render(request, "portfolioGroup_reorder.html")

def pfGroup_import_vf(request,pfGroup):
  from django import forms
  import csv
  result=[]
  class UploadFileForm(forms.Form):
    upload = forms.FileField()
  if request.method == "GET":
    return render(request, "portfolioGroup_import.html")
  elif request.method == "POST":
    form1 = UploadFileForm(request.POST, request.FILES) #request.FILES is django UploadedFile class
    if form1.is_valid():
      f1=request.FILES['upload']
      with open(PROJECT_ROOT + "/portfolio/static/upload/" + f1.name, 'wb+') as destination:
          for chunk in f1.chunks():
            destination.write(chunk)	    
      f=open(PROJECT_ROOT + "/portfolio/static/upload/" + f1.name,encoding='utf-8')
      reader=csv.reader(f)
      fieldNames = reader.__next__()
      #print(fieldNames)
      fieldCount=len(fieldNames)
      for i in range(0,fieldCount):
        result.append([])
      #print(result) #result=[[],[],[],[],[]]
      for row in reader:
        for i in range(0,fieldCount):
          if row[i]!="":
            result[i].append(row[i])
      f.close()
      #print(result)
      if pfGroup == 'HK': #tranform stockId+stockName to stockId
        for i in range(0,fieldCount):
          for j in range(0,len(result[i])):
            stockSymbol=result[i][j]  
            #print(stockSymbol)
            found = re.search(r'(.*)\_\_(\w+$)', stockSymbol, re.I) 
            if found!=None:  #symbol is  xxxx__TW, xxxx__US in portfolio
              stockId=stockSymbol
            else:
              found=re.search(r'^([0-9]+)' + r'\u0020*([^0-9]\S*)',stockSymbol)
              if found!=None:
                stockId=found.group(1)
              else:
                stockId=stockSymbol
              #print(stockId)
            result[i][j]=stockId
      #print(result)
      for i in range(0,fieldCount): #convert portfolio array to str
        #print(fieldNames[i])
        createPortfolio(pfGroup, fieldNames[i], result[i])
      return HttpResponseRedirect('/portfolio/' + pfGroup )
    else:
      form1 = UploadFileForm()
    return render(request, 'portfolioGroup_import.html', {'form': form1})
  
def pfGroup_export_vf(request,pfGroup):
  import itertools
  downloadName = "portfolio" + pfGroup + ".csv"
  portfolios = Portfolio.select().where(Portfolio.group == pfGroup)
  portfolioCount=len(portfolios)
  array=[[] for i in range(0,portfolioCount)] #generate [[],[],[],[],[]]
  for i, portfolio in enumerate(portfolios):
    #print(portfolio.name)
    array[portfolio.index].append(portfolio.name)
    stockArray=stockUtil.evalTextArray(portfolio.stock_array)
    #print(stockArray)
    for stock in stockArray:
      if pfGroup == stock["marketType"]:
        if pfGroup=='HK':
          cell = stock["stockId"] + stock["stockName"]
        else:
          cell=stock["stockName"]
      else:  
          cell = stock["stockName"] + "__" + stock["marketType"]
      array[portfolio.index].append(cell)
  #print(array)
  result=list(itertools.zip_longest(*array))
  #print(result)
  data=""
  for row in result:
    newRow = [x if x!=None else ""  for x in row]
    data = data + ",".join(newRow) + "\n"
  #print(data)
  response = HttpResponse(data,content_type='text/csv')
  response['Content-Disposition'] = "attachment; filename=%s" % downloadName
  return response

def pfGroup_delete_vf(request,pfGroup):
    return render(request, "portfolioGroup_delete.html")

@csrf_exempt
def pfGroup_portfolioList_vf(request,pfGroup):
  data=[]
  if request.method == "POST":
    qrys = Portfolio.select(Portfolio.id, Portfolio.group, Portfolio.index, Portfolio.name).where(Portfolio.group  == pfGroup)
    for qry in qrys:
      data.append({"id":qry.id, "group":qry.group, "index":qry.index, "name":qry.name} )
    #print(data)
    return JsonResponse(data, safe=False)
    #return HttpResponse(json.dumps(data), content_type='application/json')

@csrf_exempt
def pfGroup_deletePortfolioList_vf(request,pfGroup):
  if request.method == "POST":
     body_unicode = request.body.decode('utf-8')
     delIdStr = json.loads(body_unicode)
     delIdArray=delIdStr.split(",")
     for Id in delIdArray:
       #print(Id)
       q=Portfolio.delete().where(Portfolio.id == Id)
       q.execute()
     qry = Portfolio.select().where(Portfolio.group  == pfGroup).order_by(Portfolio.index)
     qry.count
     for index, item in enumerate(qry):
       #print(item._data)
       q = Portfolio.update(index=index).where(Portfolio.id == item.id)
       q.execute()
  return HttpResponseRedirect("/portfolio/" + pfGroup + "/pf0")

@csrf_exempt
def pfGroup_updatePortfolioList_vf(request,pfGroup): #ajax post json
  if request.method == "POST":
    body_unicode = request.body.decode('utf-8')
    updateArray = json.loads(body_unicode)
    #print(updateArray)
    for item in updateArray:
      #print(item)
      q=Portfolio.update(index=item["index"],name=item["name"]).where(Portfolio.id == item["id"]) #Portfolio is a class, item is a dictionary.
      q.execute()
  return HttpResponseRedirect("/portfolio/" + pfGroup + "/pf0")

def pfGroup_pfIndex_vf(request,pfGroup,pfIndex):
  pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
  pfNameArray=[]
  #print("pfGroup:" + pfGroup) 
  #print("pfIndex:" + pfIndex) 
  pfIndexNo=int(pfIndex.replace("pf",""))
  currentPortfolio = Portfolio.select().where(Portfolio.group  == pfGroup, Portfolio.index == pfIndexNo).dicts().first()
  #print(currentPortfolio)
  if currentPortfolio != None:
    stockArray=stockUtil.evalTextArray(currentPortfolio["stock_array"]) #stock_array is converted form string type to array
    currentPortfolio["stock_array"]=stockArray 
  if currentPortfolio == None:
    createPortfolio(pfGroup, "1", [])
    return HttpResponseRedirect("/portfolio/" + pfGroup + "/pf0")
  qry = Portfolio.select().where(Portfolio.group  == pfGroup).order_by(Portfolio.index)
  for i in qry:
    pfNameArray.append({"group":i.group,"index":i.index,"name":i.name})
  #print(currentPortfolio)  
  #print(pfNameArray)  
  return render(request,"portfolio.html",{"pfGroupArray":pfGroupArray, "pfGroup": pfGroup, "pfIndex": pfIndex, "pfNameArray": pfNameArray, "currentPortfolio": currentPortfolio})

@csrf_exempt
def pfGroup_pfIndex_addSymbol_vf(request,pfGroup,pfIndex): #form post
  pfIndexNo=int(pfIndex.replace("pf",""))
  if request.method == "POST":
    stockSymbol = request.POST["symbol"]
    if stockSymbol != "":
      stockSymbol1, marketType = stockUtil.parseInputSymbol(pfGroup, stockSymbol); #If stockSymbol=xxxx__xx, stockSymbol1=xxxxx
      stockName = stockUtil.getStockNameFromCSV(marketType ,stockSymbol1); #Assume input is stockId. if input not in CSV, stockName is set None 
      stockId = stockUtil.getStockIdFromCSV(marketType, stockSymbol1); #Assume input is stockName.  if input not in CSV, stockId is set None
      if stockId==None and stockName!=None:
        stockId=stockSymbol1;  #input is stockId
      if stockId!=None and stockName==None:
        stockName=stockSymbol1;  #input is stockName
      if stockId==None and stockName==None: 
        stockId=stockSymbol1;  #input can't found in csv Table
        stockName=stockId;  #input can't found in csv Table
      #print("stockId:" + stockUtil.cvNone(stockId))
      #print("stockName:" + stockUtil.cvNone(stockName))
      #print("marketType:" + stockUtil.cvNone(marketType))
      #print("stockSymbol1:" + stockUtil.cvNone(stockSymbol1))
      currentPortfolio = Portfolio.select().where(Portfolio.group  == pfGroup, Portfolio.index == pfIndexNo).dicts().first()
      if currentPortfolio != None:
        stockArray=stockUtil.evalTextArray(currentPortfolio["stock_array"]) #stock_array is converted form string type to array
        stockArray.append( {"stockId":stockId.upper() , "stockName":stockName, "marketType":marketType});
        q = Portfolio.update(stock_array=stockArray).where(Portfolio.id == currentPortfolio["id"])
        q.execute()
        #print(currentPortfolio)
      #if no portfolio in pfGroup, addSymbol do nothing. User must add symbol by create portfolio menju.
      else:
        from django.contrib import messages
        messages.add_message(request, messages.INFO, 'add a symbol must within portfolio.')
  return HttpResponseRedirect("/portfolio/" + pfGroup + "/"+ pfIndex)
  
def pfGroup_pfIndex_edit_vf(request,pfGroup,pfIndex):
  return render(request, "portfolioWatchList_edit.html")

def pfGroup_pfIndex_reorder_vf(request,pfGroup,pfIndex):
  return render(request, "portfolioWatchList_reorder.html")

@csrf_exempt
def pfGroup_pfIndex_getWatchList_vf(request,pfGroup,pfIndex):
  pfIndexNo=int(pfIndex.replace("pf",""))
  currentPortfolio = Portfolio.select().where(Portfolio.group == pfGroup, Portfolio.index == pfIndexNo).dicts().first()
  stockArray = stockUtil.evalTextArray(currentPortfolio["stock_array"]) #stock_array is converted form string type to array
  currentPortfolio["stock_array"] = stockArray
  #print(currentPortfolio)
  return JsonResponse(currentPortfolio, safe=False)

@csrf_exempt
def pfGroup_pfIndex_updateWatchList_vf(request,pfGroup,pfIndex): #ajax POST.
  pfIndexNo=int(pfIndex.replace("pf",""))
  if request.method == "POST":
    body_unicode = request.body.decode('utf-8')
    updatePortfolio = json.loads(body_unicode)
    #print(updatePortfolio)
    #print(updatePortfolio["stock_array"])
    q=Portfolio.update(stock_array=updatePortfolio["stock_array"]).where(Portfolio.group == pfGroup, Portfolio.index == pfIndexNo)
    q.execute()
  return HttpResponseRedirect("/portfolio/" + pfGroup + "/"+ pfIndex)

@csrf_exempt
def pfGroup_pfIndex_getStockNameAuto_vf(request,pfGroup,pfIndex): #ajax GET. For autocomplete.
  result = stockUtil.searchStockNameFromCSV(pfGroup, request.GET.get("term"))
  return HttpResponse(json.dumps(result))
  #return JsonResponse(result,safe=False)
 
@csrf_exempt
def pfGroup_pfIndex_edit_getStockName_vf(request,pfGroup,pfIndex): #ajax GET. For finding stockId of stockName or stockName of stockId.
  stockIdGet = request.GET.get("stockId")
  #print("stockIdGet=" + stockUtil.cvNone(stockIdGet))
  stockSymbol= stockIdGet.upper()
  stockSymbol1, marketType = stockUtil.parseInputSymbol(pfGroup, stockSymbol); #If stockSymbol=xxxx__xx, stockSymbol1=xxxxx
  stockName = stockUtil.getStockNameFromCSV(marketType, stockSymbol1) #if input is stock symbol
  return HttpResponse(stockName)
 
@csrf_exempt
def pfGroup_pfIndex_edit_getStockId_vf(request,pfGroup,pfIndex): #ajax GET. For finding stockId of stockName or stockName of stockId.
  stockNameGet = request.GET.get("stockName")
  #print("stockNameGet=" + stockUtil.cvNone(stockNameGet))
  stockSymbol = stockNameGet.upper()
  stockSymbol1, marketType = stockUtil.parseInputSymbol(pfGroup, stockSymbol); #If stockSymbol=xxxx__xx, stockSymbol1=xxxxx
  stockName = stockUtil.getStockNameFromCSV(marketType ,stockSymbol1); #Assume input is stockId. if input not in CSV, stockName is set None 
  stockId = stockUtil.getStockIdFromCSV(marketType, stockSymbol1); #Assume input is stockName.  if input not in CSV, stockId is set None
  return HttpResponse(stockId)

class historyDataEncoder(json.JSONEncoder):
  def default(self, obj):
    if isinstance(obj, decimal.Decimal):
      return float(obj)
    if isinstance(obj, datetime.datetime):
      return obj.isoformat()
    return json.JSONEncoder.default(self, obj)

@csrf_exempt
def pfGroup_pfIndex_queryLastStockData_vf(request,pfGroup,pfIndex): #ajax POST. for showing data in column of table 
  if request.method == "POST":
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode) 
    #print(body)
    if body!="":
      stockId = body.get("stockId")
      marketType = body.get("marketType")
      #print(stockId)
      #print(marketType)
      setattr(HistoryData._meta, "db_table", "history_" + marketType.lower())
      result=[]
      data=HistoryData.select().where(HistoryData.stockid==stockId).order_by(HistoryData.date.desc()).first()
      #print(data)
      if data!= None:
        data1 = { "date":data.date, "open":data.open, "high":data.high, "low":data.low, "close":data.close, "volume":int(data.volume), "stockId":stockId }
        result.append(data1)
      #print(result)
    return HttpResponse(json.dumps(result, cls=historyDataEncoder), content_type='application/json')

@csrf_exempt
def pfGroup_pfIndex_queryStockDataClose_vf(request,pfGroup,pfIndex): #ajax POST. For drawing half year graph in column of table 
  if request.method == "POST":
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode) 
    if body!="":
      stockId = body.get("stockId")
      marketType = body.get("marketType")
      #print(stockId)
      #print(marketType)
      setattr(HistoryData._meta, "db_table", "history_" + marketType.lower())
      result=[]
      for data in HistoryData.select(HistoryData.date, HistoryData.close).where(HistoryData.stockid==stockId).order_by(HistoryData.date.desc()).limit(120):
        result.append(float(data.close))
      #print(result)
    return HttpResponse(json.dumps(result), content_type='application/json')


def pfGroup_pfIndex_chart_vf(request,pfGroup,pfIndex): #href link. render a new page.
  portfolioCount = Portfolio.select().where(Portfolio.group==pfGroup).count()
  #print(request.GET)
  return render(request, "portfolioWatchList_chart.html", 
        { "stockObj":{"stockId":request.GET.get("stockId"), "marketType":request.GET.get("marketType"), "stockName":request.GET.get("stockName")},
                "index":request.GET.get("index"), "period":request.GET.get("period"), "portfolioCount":portfolioCount})

def pfGroup_pfIndex_queryStockData_vf(request,pfGroup,pfIndex): #ajax GET, send all history data of current stock for chart
  #print(request.GET.get("stockId"))
  #print(request.GET.get("marketType"))   
  quotes=stockData.loadHistoryData(request.GET.get("stockId"), "history_" + request.GET.get("marketType").lower())
  return HttpResponse(json.dumps(quotes, cls=historyDataEncoder), content_type='application/json')


