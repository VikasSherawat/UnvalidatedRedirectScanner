import json
import urllib2
from urlparse import urlparse
import urllib, urllib2, webbrowser
import cookielib
import re
from urllib2 import HTTPError, URLError

# cj = cookielib.CookieJar()
# opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
# opener.addheaders = [('Referer','https://www.google.com')]


def isvulnerable(inp):
    s = str(inp)
    if s.find("www.google.com") > 0:
        return True
    else:
        return False

print '---------------------Starting phase4------------------------'
print '---------------------Validating bugs from phase3------------------------'
with open('phase3output.json') as f:
    file = json.load(f)
    exploits = file["exploits"]

username ="admin"
password ="AdminAdmin1!"
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

for exploit in exploits:
    type = exploit["type"]
    url = exploit["url"]
    if type == "get":
        params = exploit["params"]
        if "sesskey" in params:
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            resp = opener.open(url, data = edc)
            print resp.url
        except:
            print 'Exception occured in type',type,params
            print url
    elif type == "post":
        params = exploit["params"]
        if "sesskey" in params:
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            resp = opener.open(url, data = edc)
            print resp.url
        except:
            print 'exception occured in type ',type,params
            print url
    else:
        resp = opener.open(url)
    try:
        if isvulnerable(resp.url):
            print 'Bug of type',type,'found at', url
        else:
            print 'False positive found at',url
    except HTTPError as h:
        print 'Page cannot be found %s', url
    except URLError as e:
        print 'URL is malformed %s', url
    except:
        print 'False positive found at', url

print 'Scanning has been completed, please check the result file'
