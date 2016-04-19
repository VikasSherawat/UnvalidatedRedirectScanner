import urllib2, urllib,cookielib, Cookie
import logging
from urllib2 import HTTPError, URLError
import requests
from urlparse import urlparse

import cookielib


username = "admin"
password = "AdminAdmin1!"

cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Referer','https://www.google.com')]
sesskey = "http://www.google.com"
login_data = urllib.urlencode({'username' : username, 'password' : password})
lp = opener.open('https://app2.com/login/index.php', login_data)
print lp.url
s = str(lp.read())
index = s.index("sesskey")
if index >0:
    skey = s[index:index+20]
    name, sesskey = skey.split(":")
    sesskey = str(sesskey).replace("\"", "")
    print sesskey
data = {
      "url": "https://app2.com/calendar/set.php",
      "params": {
        "var": "setcourse",
        "sesskey": "K5ennuvTB1",
        "return": "aHR0cDovL2dvb2dsZS5jb20=",
        "submit": "Go"
      },
      "type": "get"
    }
url = data["url"]
params = data["params"]
params["sesskey"] = sesskey
print params
edc = urllib.urlencode(params)
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
