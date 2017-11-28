import os
curDir = os.path.dirname(os.path.abspath(__file__)) # Do't use curDir. curDir maybe pollute by other import module. Using PROJECT_ROOT for safe
PROJECT_ROOT = os.path.dirname(curDir) # mean cd..
#print(PROJECT_ROOT)

from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.contrib import auth
import base64
import lib.stockUtil as stockUtil

def root_vf(request):
  return HttpResponseRedirect("/portfolio")

####################################################
## This use middleware for authorizattion.
## Below funcions are not use in this  project.
####################################################

#for using authorizattion by myself. work with "@my_auth"
def my_auth(f):
  def wrap(request, *args, **kwargs):
    if request.META.get('HTTP_AUTHORIZATION', False):
      authtype, auth1 = request.META['HTTP_AUTHORIZATION'].split(' ')
      auth2 = base64.b64decode(auth1).decode('utf-8')
      print(authtype)
      print(auth2)
      username, password = str(auth2).split(':')
      print(username)
      print(password)
      if username == stockUtil.config["authentication"]["user"] and password == stockUtil.config["authentication"]["password"] : #set user and password
        return f(request, *args, **kwargs)
    response = HttpResponse("Auth Required", status = 401)
    response['WWW-Authenticate'] = 'Basic realm="My Realm"'
    return response
  return wrap

#for django autherization. work with "@login_required"
def login_vf(request):
  print(request.user)
  if request.user.is_authenticated(): 
    return HttpResponseRedirect("/portfolio/TW/pf0")
  elif request.META.get('HTTP_AUTHORIZATION', False):
      authtype, auth1 = request.META['HTTP_AUTHORIZATION'].split(' ')
      auth2 = base64.b64decode(auth1).decode('utf-8')
      #print(authtype)
      #print(auth2)
      username, password = str(auth2).split(':')
      user = auth.authenticate(username=stockUtil.config["authentication"]["user"], password=stockUtil.config["authentication"]["password"])
      if user is not None and user.is_active:
        auth.login(request, user) #maintain the state of login
        return HttpResponseRedirect("/portfolio/TW/pf0")
  response = HttpResponse("Auth Required", status = 401)
  response['WWW-Authenticate'] = 'Basic realm="restricted area"'
  return response






