from .base import *

DEBUG = True

ALLOWED_HOSTS = ['localhost', '127.0.0.1']
#ALLOWED_HOSTS = ['localhost', '127.0.0.1', '192.168.1.12']

LOGIN_EXEMPT_URLS = (
    r'^$',
    r'^portfolio/',
)
