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

param =  {
        "i": "http://google.com",
        "m": "gbook",
        "t": "cy9NLS5Jys%2FPBgA%3D",
        "mod": "qcomment"
      }
url = "http://app10.com/search.php?query=&mod_id=http%3A%2F%2Fgoogle.com&AXSRF_token="
#params = data["params"]
param["sesskey"] = ""
edc = urllib.urlencode(param)
fullurl = url +"?"+ edc
try:
    resp = opener.open(url)
    print resp.url
except HTTPError as h:
    print h.reason, h.code
except URLError as e:
    print e.reason, e.code
except:
    print 'False positive found at', url
