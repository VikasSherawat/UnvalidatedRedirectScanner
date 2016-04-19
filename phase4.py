import json
import urllib2
from urlparse import urlparse
import urllib, urllib2, webbrowser
import cookielib
import re
from urllib2 import HTTPError, URLError

# cj = cookielib.CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener = urllib2.build_opener()
opener.addheaders = [('Referer','https://www.google.com')]


def isvulnerable(inp):
    s = str(inp)
    if s.find("www.google.com") > 0:
        return True
    else:
        return False


print '---------------------Starting phase4------------------------'
print '---------------------Validating bugs from phase3------------------------'

login_url = ""
login_detail = ""
base_url = ""
app_name = ""

with open('output/phase3output.json') as f:
    file = json.load(f)
    exploits = file["exploits"]
    if "baseurl" in file:
        base_url = file['baseurl']
    if "appname" in file:
        app_name = file['appname']
    if "loginurl" in file:
        login_url = file['loginurl']
    if "logindetails" in file and file['logindetails']:
        login_detail = file['logindetails'][0]

username ="admin"
password ="AdminAdmin1!"
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Referer','https://www.google.com')]
sesskey = "http://www.google.com"

if login_url != "":
    login_data = urllib.urlencode({'username' : username, 'password' : password})
    lp = opener.open(login_url, login_data)
    print lp.url
    s = str(lp.read())
    index = s.index("sesskey")
    if index >0:
        skey = s[index:index+20]
        name, sesskey = skey.split(":")
        sesskey = str(sesskey).replace("\"", "")
        print sesskey

bugCount = 0
errorCount = 0
falsePositiveCount = 0
indexCount = 0

for exploit in exploits:
    indexCount += 1
    print "Case Number : "+ str(indexCount)
    type = exploit["type"]
    url = exploit["url"]
    if type == "get" or type == "GET":
        params = exploit["params"]
        if "sesskey" in params  and login_url != "":
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            print "Page url : " + url
            print "Attack type : GET"
            resp = opener.open(url, data = edc)
            print "Response url : " + resp.url
            if isvulnerable(resp.url):
                # print 'Bug of type',type,'found at', url
                print "Bug verified"
                bugCount += 1
            else:
                print "False positive occured"
                falsePositiveCount += 1
        except:
            falsePositiveCount +=1
            print "False positive occured"
            #print 'Exception occured with param',params
    elif type == "post" or type == "POST":
        params = exploit["params"]
        if "sesskey" in params and login_url != "":
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            print "Page url : " + url
            print "Attack type : POST"
            resp = opener.open(url, data = edc)
            print "Response url : " + resp.url
            if isvulnerable(resp.url):
                # print 'Bug of type',type,'found at', url
                print "Bug verified"
                bugCount += 1
            else:
                print "False positive occured"
                falsePositiveCount += 1
        except:
            falsePositiveCount +=1
            #print 'exception occured with param',params
            print "False positive occured"
    else:
        print "page url : " + url
        print "Attack type : Redirect"
        try:
            resp = opener.open(url, data=edc)
            print "Response url : " + resp.url
            if isvulnerable(resp.url):
                # print 'Bug of type',type,'found at', url
                print "Bug verified"
                bugCount += 1
            else:
                print "False positive occured"
                falsePositiveCount += 1
        except:
            falsePositiveCount += 1
            print "False positive occured"

print "======================================================================================================="
print "Summary : "
print "Total Bugs reported:",str(bugCount+falsePositiveCount)
print "No. of bugs detected : " + str(bugCount)
print "No. of false positives detected : " + str(falsePositiveCount)
print 'Scanning has been completed, please check the result file'
print "======================================================================================================="