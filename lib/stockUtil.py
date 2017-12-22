"""
pfGroup:交易市場TW,HK,US. 
stockSymbol是show給使用者看的股票代號.存在資料庫要轉成stockId和marketType
stockId各市場官方股票代碼,港股官方代碼為5碼,yahoo只能用4碼查詢,我們存在db上的stockId會把開頭為0的都去掉.
pfGroup + stockSymbol  -> marketType -> collections
pfGroup + stockSymbol  -> stockId -> as primary key of stockData 
marketType + stockId -> marketId -> 區別上市, 上櫃
marketType + stockId -> StockName
"""
import os
curDir = os.path.dirname(os.path.abspath(__file__)) # Do't use curDir. curDir maybe pollute by other import module. Using PROJECT_ROOT for safe
PROJECT_ROOT = os.path.dirname(curDir) # mean cd..
import re
import csv
import ast
import configparser

def read_config(i, j):
  config = configparser.ConfigParser()
  config.read(PROJECT_ROOT + "/config.ini")
  return config[i][j]

def searchStockNameFromCSV(marketType,queryString):
  queryString1=queryString.upper()
  ary=[]
  #regStr= '^(\\d+)' + ' ' + '(\\S*)' + queryString1 + '(\\S*)$'  # 取出數字部份
  regStr=  r'^(\d+)' + ' ' + r'(\S*' + queryString1 + r'\S*)$'  # 取出數字部份
  #print(regStr)
  if marketType=="TW":
    text = open(PROJECT_ROOT + "/lib/台股上市公司20171219.csv").read()
    found=re.findall(regStr, text, re.M|re.I)
    #print(found)
    if found!=None:
      for a in found:
        ary.append(a[1])
    text = open(PROJECT_ROOT + "/lib/台股上櫃公司20171219.csv").read()
    found=re.findall(regStr, text, re.M|re.I)
    #print(found)
    if found!=None:
      for a in found:
        ary.append(a[1])
  if marketType=="HK":
    text = open(PROJECT_ROOT + "/lib/港股代碼20160212.csv").read()
    found=re.findall(regStr, text, re.M|re.I)
    if found!=None:
      #print(found)
      for a in found:
        ary.append(a[1])
  f1 = open(PROJECT_ROOT + "/lib/custom.csv",encoding="utf-8")
  reader=csv.reader(f1)
  fieldNames = reader.__next__()
  for row in reader:
    if queryString1 in row[0].upper():
      ary.append(row[0])
    if queryString1 in row[1].upper():
      ary.append(row[1])
  f1.close()
  return ary

def getStockNameFromCSV(marketType, stockId): #return None if stockId not found
  #import sys
  #print(sys.getfilesystemencoding())
  #print(sys.stdin)
  #regStr= '^' + stockId + " " + r'((:?\D+)(:?\w*))' + '$'  # 取出非數字部份
  regStr=  '^' + stockId + " " + r'((:?\D)(:?[^\n]*$))'  # 取出非數字部份
  #print(regStr)
  if marketType=="US": 
    return stockId
  if marketType=="TW": #找上市公司名單
    text = open(PROJECT_ROOT + "/lib/台股上市公司20171219.csv").read()
    #print(text)
    found=re.search(regStr,text,re.M|re.I);
    if found!=None: 
      #print(found.group())
      return found.group(1).strip()
      found1=re.search(r'(\D+\w*)',found.group())
      if found1!=None:
        return found1.group().strip() #返回上市公司名稱
    else:  #上市公司名單中找不到,改找上櫃公司名單
      text = open(PROJECT_ROOT + "/lib/台股上櫃公司20171219.csv").read()
      #print(text)
      found=re.search(regStr,text,re.M|re.I);
      if found!=None:
        return found.group(1).strip() 
        found1=re.search(r'(\D+\w*)',found.group())
        if found1!=None:
          return found1.group().strip() #返回上市公司名稱
    return None  #上市櫃名單中都找不到
  if marketType=="HK":
      if re.search("^\d+$",stockId)==None:
        return stockId
      stockId1=str(int(stockId)); #去掉開頭0部份例如00836 變 836
      #print(stockId1)
      regStr= r'^(:?[0]*)' + stockId1 + " " + r'((:?\D+)(:?\w*))\n'; # 取出非數字部份
      #regStr= r'^(:?[0]*)' + stockId1 + " " + r'((:?\D)(:?[^\n]*$))'; # 取出非數字部份
      #print(regStr)
      text = open(PROJECT_ROOT + "/lib/港股代碼20160212.csv").read()
      #print(text)
      found=re.search(regStr,text,re.M|re.I)
      if found!=None: 
        #print(found.group())
        return found.group(2).strip()
        found1=re.search(r'(\D+\w*)',found.group())
        if found1!=None:
          return found1.group().strip() #返回港股公司名稱
      return None 
  if marketType=="CUS": 
      f1 = open(PROJECT_ROOT + "/lib/custom.csv",encoding="utf-8")
      reader=csv.reader(f1)
      fieldNames = reader.__next__()
      for row in reader:
        if stockId.upper()==row[0].upper():
          return row[1].strip()
      f1.close()
  return None 

def getStockIdFromCSV(marketType, stockName): #return None if stockName not found
  regStr= r'^(\d+)' + ' ' + stockName + '$'  # digit
  if marketType=="US":  return stockName
  if marketType=="TW":
    text = open(PROJECT_ROOT + "/lib/台股上市公司20171219.csv").read()
    found=re.search(regStr,text,re.M|re.I)
    if (found!=None):
      return found.group(1).strip()  #返回上市公司名稱
    else: 
      text = open(PROJECT_ROOT + "/lib/台股上櫃公司20171219.csv").read()
      found=re.search(regStr,text,re.M|re.I)
      if found!=None:
        return found.group(1).strip()  #返回上櫃公司名稱
    return None
  if marketType=="HK":
    text = open(PROJECT_ROOT + "/lib/港股代碼20160212.csv").read()
    found=re.search(regStr,text,re.M|re.I)
    if found!=None:  
      return found.group(1).strip()  #返回港股代號
    return None
  if marketType=="CUS": 
      f1 = open(PROJECT_ROOT + "/lib/custom.csv",encoding="utf-8")
      reader=csv.reader(f1)
      fieldNames = reader.__next__()
      for row in reader:
        if stockName.upper()==row[1].upper(): 
          f1.close()
          return row[0].strip()
      f1.close()
  return None

def getSourceFromCustomCSV(marketType, stockId): #return None if stockName not found
  if marketType == "CUS":
    f1 = open(PROJECT_ROOT + "/lib/custom.csv",encoding="utf-8")
    reader=csv.reader(f1)
    fieldNames = reader.__next__()
    for row in reader:
      if stockId.upper()==row[0].upper():
        f1.close()
        return row[2].strip()
    f1.close()
  return None

def getMarketId(marketType, stockId):
  if marketType=="TW":  #台股上市或上櫃
    text = open(PROJECT_ROOT + "/lib/台股上市公司20171219.csv").read()
    if re.search(stockId, text, re.M|re.I) != None:  return marketType
    else:  return 'TWO'
  if marketType=="US":
    str= r'"' + stockId +r'"' 
    #print(str)
    text = open(PROJECT_ROOT + "/lib/NYSEcompanylist.csv").read()
    if re.search(str, text, re.M|re.I) != None:  return "NYSE"
    text = open(PROJECT_ROOT + "/lib/AMEXcompanylist.csv").read()
    if re.search(str, text, re.M|re.I) != None:  return "NYSE"  #AMEX is acquire by NASDAQ
    text = open(PROJECT_ROOT + "/lib/NASDAQcompanylist.csv").read()
    if re.search(str, text, re.M|re.I) != None:  return "NASDAQ"
    return marketType
  if marketType=="HK":
    return marketType
  return marketType

def parseInputSymbol(pfGroup, stockSymbol): #extract  symbol and marketType from stockSymbol
  found = re.search(r'(.*)\_\_(\w+$)', stockSymbol, re.I)  #check stockSymbol style is  xxxx__xx(ie. xxxx__US)
  if found!=None:
    symbol1=found.group(1)
    marketType=found.group(2)
  else:
    symbol1=stockSymbol
    marketType=pfGroup;       #if symbol 
  #print("symbol1=" + symbol1)
  #print("market=" + marketType)
  return symbol1, marketType

def cvNone(x):  #for print Nonetype
  if x is None:
    return "NoneType"
  else: 
    return x
 
def evalTextArray(text):
  if text == "": 
    return []
  else:
    return ast.literal_eval(text)

def evalTextDict(text):
  if text == "": 
    return {}
  else:
    return ast.literal_eval(text)



