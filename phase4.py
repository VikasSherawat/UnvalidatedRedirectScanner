import json
import urllib2
from urlparse import urlparse
import urllib, urllib2, webbrowser
import cookielib
import re, logging
from urllib2 import HTTPError, URLError
from selenium import webdriver
import time
import os

def saveResponse(testId, content):

    # Save the response
    f = open(directory + "/response"+str(testId)+".html", "w")
    f.write(content)
    f.close()
    
    url = "file:///" + path + "/" + directory + "/response"+str(testId)+".html"
    driver = webdriver.Firefox()
    driver.get(url)
    time.sleep(3)
    driver.close()

def clearFolder(folder_path):
    for the_file in os.listdir(folder_path):
        file_path = os.path.join(folder_path, the_file)
        try:
            if os.path.isfile(file_path):
                os.unlink(file_path)
            # elif os.path.isdir(file_path): shutil.rmtree(file_path)
        except Exception as e:
            print(e)

def load(filename):
    f = open(filename, "r")
    config = json.load(f)
    count = 0
    for app in config.get("apps"):
        if app.get("is_running") == "true":
            break
        count = count + 1
    return config.get("apps")[count]


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

path = os.getcwd()
directory = "p4output"
if not os.path.exists(directory):
    os.makedirs(directory)
clearFolder(path + "/" + directory)

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

if login_url != "":
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
	    saveResponse(indexCount, resp.read())
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
	    saveResponse(indexCount, resp.read())
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
	    saveResponse(indexCount, resp.read())
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
