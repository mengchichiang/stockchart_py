import os
curDir = os.path.dirname(os.path.abspath(__file__)) 
import requests
from pyquery import PyQuery as pq

import datetime
import pytz
import csv
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo

from importlib.machinery import SourceFileLoader

def get_func_from_modStockData( funcStr, source): 
  #for python version>=v3.4
  modStockData = SourceFileLoader( "mod_" + source, curDir + "/mod_" + source +".py").load_module()
  return getattr(modStockData, funcStr)

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


