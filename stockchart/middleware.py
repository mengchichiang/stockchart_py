import os
curDir = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(curDir)
#print(PROJECT_ROOT)
import sys
sys.path.append(PROJECT_ROOT)
#print(sys.path)

from django.http import HttpResponse,HttpResponseRedirect, JsonResponse
from django.shortcuts import render
from django.conf import settings
from re import compile
import base64
from lib.dbModel import db, Portfolio, HistoryData, StockInfo, ProjectInfo
import lib.stockUtil as stockUtil

#reference to: https://python-programming.courses/recipes/django-require-authentication-pages/

#LOGIN_EXEMPT_URLS in settin.py is the path that you want to skip authentication.
EXEMPT_URLS =[]
if hasattr(settings, 'LOGIN_EXEMPT_URLS'):
  EXEMPT_URLS += [compile(expr) for expr in settings.LOGIN_EXEMPT_URLS]

class LoginRequiredMiddleware:
  def process_request(self, request):
    path = request.path_info.lstrip('/')
    #print(path)
    if not any(m.match(path) for m in EXEMPT_URLS):
      if request.META.get('HTTP_AUTHORIZATION', False):
        authtype, auth1 = request.META['HTTP_AUTHORIZATION'].split(' ')
        auth2 = base64.b64decode(auth1).decode('utf-8')
        #print(authtype)
        #print(auth2)
        username, password = str(auth2).split(':')
        if username == stockUtil.config["authentication"]["user"] and password == stockUtil.config["authentication"]["password"] : #set user and password
          return None
      response = HttpResponse("Auth Required", status = 401)
      response['WWW-Authenticate'] = 'Basic realm="My Realm"'
      return response

class PeeweeConnectionMiddleware(object):
  def process_request(self, request):
    db.connect()
  def process_response(self, request, response):
    if not db.is_closed():
      db.close()
    return response

