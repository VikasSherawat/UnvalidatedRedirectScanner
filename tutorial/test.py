import urllib2, urllib,cookielib, Cookie
import logging
from urllib2 import HTTPError, URLError
import requests
from urlparse import urlparse

import cookielib


username = "admin"
password = "AdminAdmin1!"
login_url = 'https://bm2.com/login.php'
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
if len(username) >0:
    login_data = urllib.urlencode({'username' : username, 'password' : password})
    #print  loginurl
    lp = opener.open(login_url, login_data)
opener.addheaders = [('Referer','https://www.google.com')]

param =  {
        "encode":"aHR0cDovL2dvb2dsZS5jb20="
      }
url = "https://bm2.com/surveyRedirect.php"
#params = data["params"]
param["sesskey"] = ""
edc = urllib.urlencode(param)
fullurl = url +"?"+ edc
try:
    resp = opener.open(fullurl)
    print resp.url
except HTTPError as h:
    print h.reason, h.code
except URLError as e:
    print e.reason, e.code
except:
    print 'False positive found at', url
