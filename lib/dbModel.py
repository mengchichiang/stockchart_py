import os
curDir = os.path.dirname(os.path.abspath(__file__)) # Do't use curDir. curDir maybe pollute by other import module. Using PROJECT_ROOT for safe
PROJECT_ROOT = os.path.dirname(curDir) # mean cd..
#print(PROJECT_ROOT)

import lib.stockUtil as stockUtil

from peewee import *

config_dbSel = stockUtil.read_config("database","database")
if config_dbSel == None :
  db = SqliteDatabase(stockUtil.read_config("database","FilePath"))
else: 
  if config_dbSel.lower() == "postgresql":
    db = PostgresqlDatabase(threadlocals=True, database="stockdb", user=stockUtil.read_config("database","user"), password=stockUtil.read_config("database","password"), host="127.0.0.1", port="5432")
  else:
    db = SqliteDatabase(stockUtil.read_config("database","FilePath"))

class Portfolio(Model):
  group = TextField() 
  index = IntegerField() #portfolio index in the group
  name = TextField()    #portfolio name
  stock_array=TextField() #stocks in this portfolio. element is {"stockId":stockId , "stockName":stockName, "marketType":marketType}
  class Meta:
    database = db
    db_table = "portfolio"

class HistoryData(Model):
    date = DateTimeField(null=True)
    open = DecimalField(null=True,max_digits=20,decimal_places=6)
    high = DecimalField(null=True,max_digits=20,decimal_places=6)
    low = DecimalField(null=True,max_digits=20,decimal_places=6)
    close = DecimalField(null=True,max_digits=20,decimal_places=6)
    volume = DecimalField(null=True,max_digits=20,decimal_places=0)
    stockid = TextField()
    class Meta:
      database = db
      db_table = 'history'
      primary_key = CompositeKey('date', 'stockid')

class StockInfo(Model):
    stockid = TextField()
    markettype = TextField()
    history_info = TextField()
    finance_info = TextField()
    class Meta:
      database = db
      db_table = 'stockinfo'

class ProjectInfo(Model):
    download_access = TextField() #TRUE if access right is lock. Let download job is only one at the same time.
    download_date = TextField()
    download_time = TextField()
    class Meta:
      database = db
      db_table = 'projectinfo'

db.connect()
Portfolio.create_table(True)
pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
for pfGroup in pfGroupArray:
  setattr(HistoryData._meta, "db_table", "history_" + pfGroup.lower())
  HistoryData.create_table(True) #argument=True: create table if table not exist.
StockInfo.create_table(True)
ProjectInfo.create_table(True)
db.close()
