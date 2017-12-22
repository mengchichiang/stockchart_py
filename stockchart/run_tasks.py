import os
curDir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(curDir)
#print(PROJECT_ROOT)

import sys
sys.path.append(PROJECT_ROOT) #add module search path
#print(sys.path)

from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo

from stockchart.tasks import downloadDataTask

import threading
import managedata.views

def clearDownloadAccessFlag():  
  db.get_conn()
  qry=ProjectInfo.select().first()
  if qry == None:
    q=ProjectInfo.insert(**{"download_date":"2010-01-01","download_access":"TRUE"})
    q.execute()
    qry=ProjectInfo.select().first()
  if qry != None:
      q=ProjectInfo.update(**{"download_access":"TRUE"}).where(ProjectInfo.id==qry.id)
      q.execute()
  db.close()

managedata.views.cleanData()
clearDownloadAccessFlag()
downloadDataTask()
#threading.Timer(0, downloadDataTask).start()

