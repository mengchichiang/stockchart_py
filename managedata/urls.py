from django.conf.urls import url, include
from django.contrib import admin
from managedata.views import * 

urlpatterns = [
    url(r'^$', root_vf),
    url(r'download$', downloadData_vf),
    url(r'clean$', cleanData_vf),
    url(r'deleteData$', deleteData_vf),
    url(r'status$', status_vf),
]


