
from dateutil.parser import parse

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



