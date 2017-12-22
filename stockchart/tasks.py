from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
from lib import stockUtil

pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))

#downlad data if download have not be done today.
def downloadDataTask():
  import managedata.views
  import datetime
  today=datetime.date.strftime(datetime.datetime.now(), '%Y-%m-%d')
  db.connect()
  qry=ProjectInfo.select().first()
  if qry == None:
    q=ProjectInfo.insert(**{"download_date":"2010-01-01","download_access":"TRUE"})
    q.execute()
    qry=ProjectInfo.select().first()
  if qry != None:
    if qry.download_access == "TRUE":
      q=ProjectInfo.update(**{"download_access":"FALSE"}).where(ProjectInfo.id==qry.id)
      q.execute()      
      if qry.download_date == today:
        print("Download have been done today")
        pass
      else:
        for pfGroup in pfGroupArray:
          #managedata.views.cleanData()
          managedata.views.downloadData(pfGroup)
      q=ProjectInfo.update(**{"download_date":today,"download_access":"TRUE"}).where(ProjectInfo.id==qry.id)
      q.execute()
    else:
      pass
  db.close()






