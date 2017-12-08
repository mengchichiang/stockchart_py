from django.conf.urls import url, include
from django.contrib import admin
from portfolio.views import * 
import lib.stockUtil as stockUtil


pfGroupArray=stockUtil.evalTextArray(stockUtil.read_config("portfolio","pfGroupArray"))
pfGroupPath=r'(?P<pfGroup>'+ '|'.join(pfGroupArray).replace("'","") + ')'
#print(pfGroupPath)

urlpatterns = [
    url(r'^$', root_vf),
    url(pfGroupPath + r'/$',pfGroup_vf),
    url(pfGroupPath + r'/create$',pfGroup_create_vf),
    url(pfGroupPath + r'/edit$',pfGroup_edit_vf),
    url(pfGroupPath + r'/reorder$',pfGroup_reorder_vf),
    url(pfGroupPath + r'/import$',pfGroup_import_vf),
    url(pfGroupPath + r'/export$',pfGroup_export_vf),
    url(pfGroupPath + r'/delete$',pfGroup_delete_vf),
    url(pfGroupPath + r'/portfolioList$',pfGroup_portfolioList_vf),
    url(pfGroupPath + r'/deletePortfolioList$',pfGroup_deletePortfolioList_vf),
    url(pfGroupPath + r'/updatePortfolioList$',pfGroup_updatePortfolioList_vf),
    url(pfGroupPath + r'/reorder$',pfGroup_reorder_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)$', pfGroup_pfIndex_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/addSymbol$', pfGroup_pfIndex_addSymbol_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/edit$', pfGroup_pfIndex_edit_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/getStockNameAuto$', pfGroup_pfIndex_getStockNameAuto_vf), #for watch list edit menu
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/reorder$', pfGroup_pfIndex_reorder_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/getWatchList$', pfGroup_pfIndex_getWatchList_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/edit/getStockId$', pfGroup_pfIndex_edit_getStockId_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/edit/getStockName$', pfGroup_pfIndex_edit_getStockName_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/updateWatchList$', pfGroup_pfIndex_updateWatchList_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/queryLastStockData$', pfGroup_pfIndex_queryLastStockData_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/chart$', pfGroup_pfIndex_chart_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/queryStockData$', pfGroup_pfIndex_queryStockData_vf),
    url(pfGroupPath + r'/(?P<pfIndex>pf[0-9]+)/queryStockDataClose$', pfGroup_pfIndex_queryStockDataClose_vf),
]


