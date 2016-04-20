import json
import urllib2
from urlparse import urlparse
import urllib, urllib2, webbrowser
import cookielib
import re, logging
from urllib2 import HTTPError, URLError
import sys


def load(filename):
    try:
        f = open(filename, "r")
        config = json.load(f)
        count = 0
        for app in config.get("apps"):
            if app.get("is_running") == "true":
                break
            count = count + 1
        return config.get("apps")[count]
    except:
        logging.error('Config file not found  %s',filename)
        sys.exit(1)


def isvulnerable(inp):
    s = str(inp)
    if s.find("www.google.com") > 0 and app_name not in inp:
        return True
    else:
        return False

filename = 'tutorial/spiders/config.json'
app = load(filename)

app_name = app["app_name"]
# cj = cookielib.CookieJar()
#opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener = urllib2.build_opener()
opener.addheaders = [('Referer','https://www.google.com')]

login_url = ""
login_detail = ""
base_url = ""
phase3outputpath = 'output/' + app_name + "_p3.json"

logging.basicConfig(filename='logs/phase4.log',level=logging.DEBUG)
logging.info('---------------------Starting phase4------------------------')
logging.info('---------------------Validating bugs from phase3------------------------')

try:
    with open(phase3outputpath) as f:
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
except:
    logging.error('Phase 3 output file not found %s',phase3outputpath)
    sys.exit(1)
username = login_detail["username"]
password = login_detail["password"]
cj = cookielib.CookieJar()
opener = urllib2.build_opener(urllib2.HTTPCookieProcessor(cj))
opener.addheaders = [('Referer','https://www.google.com')]
sesskey = "http://www.google.com"

if login_url != "":
    login_data = urllib.urlencode({'username' : username, 'password' : password})
    lp = opener.open(login_url, login_data)
    s = str(lp.read())
    index = -1
    if "sesskey" in s:
        index = s.index("sesskey")
    index = s.index("sesskey")
    if index >0:
        skey = s[index:index+20]
        name, sesskey = skey.split(":")
        sesskey = str(sesskey).replace("\"", "")

bugCount = 0
errorCount = 0
falsePositiveCount = 0
indexCount = 0

for exploit in exploits:
    indexCount += 1
    logging.info("Case Number : %s",str(indexCount))
    type = exploit["type"]
    url = exploit["url"]
    if type == "get" or type == "GET":
        params = exploit["params"]
        if "sesskey" in params  and login_url != "":
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            logging.info("Page url : %s", url)
            logging.info("Attack type : GET")
            resp = opener.open(url, data = edc)
            logging.info("Response url :%s ",resp.url)
            if isvulnerable(resp.url):
                # logging.info('Bug of type',type,'found at', url
                logging.info("Bug verified")
                bugCount += 1
            else:
                logging.info("False positive occured")
                falsePositiveCount += 1
        except:
            falsePositiveCount +=1
            logging.info("False positive occured")
            #logging.info('Exception occured with param',params
    elif type == "post" or type == "POST":
        params = exploit["params"]
        if "sesskey" in params and login_url != "":
            params["sesskey"] = sesskey
        edc = urllib.urlencode(params)
        #url = url + "?"+edc
        try:
            logging.info("Page url : %s", url)
            logging.info("Attack type : POST")
            resp = opener.open(url, data = edc)
            logging.info("Response url : %s",resp.url)
            if isvulnerable(resp.url):
                # logging.info('Bug of type',type,'found at', url
                logging.info("Bug verified")
                bugCount += 1
            else:
                logging.info("False positive occured")
                falsePositiveCount += 1
        except:
            falsePositiveCount +=1
            #logging.info('exception occured with param',params
            logging.info("False positive occured")
    else:
        logging.info("Page url : %s", url)
        logging.info("Attack type : Redirect")
        try:
            resp = opener.open(url, data=edc)
            logging.info("Response url : " + resp.url)
            if isvulnerable(resp.url):
                # logging.info('Bug of type',type,'found at', url
                logging.info("Bug verified")
                bugCount += 1
            else:
                logging.info("False positive occured")
                falsePositiveCount += 1
        except:
            falsePositiveCount += 1
            logging.info("False positive occured")

logging.info("=======================================================================================================")
logging.info("Summary : ")
logging.info("Total Bugs reported: %s",str(bugCount+falsePositiveCount))
logging.info("No. of bugs detected : %s", str(bugCount))
logging.info("No. of false positives detected : %s", str(falsePositiveCount))
logging.info('Scanning has been completed, please check the result file')
logging.info("=======================================================================================================")