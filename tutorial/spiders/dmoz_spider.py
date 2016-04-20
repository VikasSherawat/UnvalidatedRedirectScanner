from scrapy.utils.response import get_base_url
from scrapy.utils.url import urljoin_rfc
from scrapy.selector import HtmlXPathSelector
from scrapy.linkextractors.sgml import SgmlLinkExtractor
from scrapy.spiders import CrawlSpider, Rule
from scrapy.http import Request
import scrapy
from scrapy.http import FormRequest
import json
from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
#from urllib.parse import urlparse
from urlparse import urlparse, urljoin,parse_qs
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
import urllib
import re
import sys
import os

class DmozSpider(scrapy.Spider):
    name = "app"
    handle_httpstatus_list = [302,303,301,404,500]
    app_name = ""
    allowed_domains = []
    baseurl = ''
    formdata = {}
    visited_url = set()
    login_url = ''
    invalidresponse = []
    page_visited = set()
    pagegetdict = dict()
    forminjectionList = []
    output = dict()
    cookies = []
    injectiondictionary = dict()
    redirect_dict = dict()
    start_urls = []
    ignored_paths = []
    output_filename = ""
    redirect_filename = ""
    index = ""

    def load(self,filename):
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
            print "file not found ", filename
            sys.exit(1)

    def __init__(self):
        print "*******************************************",sys.path
        app = self.load('/home/user/scanner/UnvalidatedRedirectScanner/tutorial/spiders/config.json')
        self.app_name = app["app_name"].strip()
        self.baseurl = app["base_url"].strip()
        for ignore in app["ignored_paths"]:
          self.ignored_paths.append(re.compile(ignore))
        for strt_url in app["start_urls"]:
          self.start_urls.append(strt_url)
        for allwd_domains in app["allowed_domains"]:
          self.allowed_domains.append(allwd_domains)
        auth_details = app.get("auth",None)
        self.output["baseurl"] = self.baseurl
        if auth_details is not None:
          username = auth_details.get("username")
          password = auth_details.get("password")
          self.login_url = auth_details.get("login_url")
          loginList = []
          self.formdata.update({"username":username,"password":password})
          loginList.append(self.formdata)
          self.output["logindetails"] = loginList
          self.output["loginurl"] = self.login_url
          self.output["name"] = app["app_name"].strip()
        self.output_filename = app["output_file"].strip()
        self.output["outputfile"] = self.output_filename
        self.redirect_filename = app["redirect_file"].strip()
        self.output["redirectfile"] = self.redirect_filename
        dispatcher.connect(self.spider_closed, signals.spider_closed)


    def parse(self, response):
        print("--------------------------Inside parse method----------------------------------")
        self.logger.info('login url value is %s',self.login_url)
        if len(self.login_url) <= 0:
            return [Request(url=url, dont_filter=True, callback=self.extract_url) for url in self.start_urls]
        else:
            return scrapy.FormRequest(self.login_url,
                                  formdata=self.formdata,
                                  dont_filter=True,
                                  callback=self.check_login)

    def check_login(self, response):
            print("--------------------------Inside check login method----------------------------------")
            for c in response.request.headers.getlist("Cookie"):
              splitval = self.split_cookies(c)
              if len(self.cookies) == 0:
                self.cookies.append(splitval)
            print('Successfully Logged in!!! ')
            self.logger.info("Cookies are %s", self.cookies)
            self.output["cookies"] = self.cookies
            for url in self.start_urls:
              yield Request(url,callback=self.extract_url)

    def prep_url(self, uri, on_url):
      url = uri
      if url.find("://") < 0 and url.startswith("//") == False:
        parts = urlparse(on_url)
        url = urljoin(on_url, uri)
      return url

    def extract_url(self, response):
        if response is None:
          return
        self.logger.info("--------------------------Inside extract_url method for %s", response.url)
        self.extractformdata(response)
        ls = response.xpath('//a/@href').extract()
        status = response.status

        for url in ls:
            if str(url).startswith('/') or "http" not in str(url):
                url = urljoin(self.baseurl, url)
            if self.validURL(url, status):
                p = urlparse(url)
                if url not in self.visited_url and p.path not in self.page_visited:
                    self.page_visited.add(p.path)
                    self.visited_url.add(url)
                    self.logger.info("Added URL is -->%s", url)
                    ls = self.extractgetList(url)
                    self.addURLinjectList(ls, url)
                    yield Request(url, callback = self.extract_url)
            else:
                self.logger.info('Url Skipped %s', url)

    def validURL(self, url,status):
        url = str(url)
        p = urlparse(url)
        if str(status).startswith('4') or url.startswith('#') or "logout" in url:
            return False
        elif p.netloc not in self.allowed_domains:
          return False
        elif url.startswith('/'):
            return True
        #elif not("app10" in url) and "http" in url:
         #   return False
        else:
            return True

    def sendrequesttoform(self, requesttype, formparamlist, actionLink,url):
        self.logger.info('Inside sendrequesttoform method')

        #actionLink = self.prep_url(actionLink, url)
        p = urlparse(actionLink)
        if p.path not in self.page_visited:
          self.logger.info('About to crawl %s %s',actionLink,requesttype)
          self.page_visited.add(p.path)
          self.visited_url.add(actionLink)
          if requesttype.upper() == "GET":
            return Request("%s?%s" % (actionLink, urllib.urlencode(formparamlist)) if len(formparamlist) > 0 else actionLink,
            callback=self.extract_url)
          elif requesttype.upper() == "POST":
            return Request(actionLink, method="POST",
            headers={"Content-Type": "application/x-www-form-urlencoded"},
            body=urllib.urlencode({k: v.encode("utf8") for k, v in formparamlist.iteritems()}),
            callback=self.extract_url)

    def extractformdata(self, response):
        self.logger.info('Scanning page %s', response.url)
        formxpath = response.selector.xpath('//form')
        formList = []
        for form in formxpath:
            formsdict = dict()
            if form.xpath('.//@method'):
                requestType = form.xpath('.//@method').extract()[0]
            else:
                requestType = None
            if form.xpath('.//@action'):
                actionLink = form.xpath('.//@action').extract()[0]
                if str(actionLink).startswith('/') or "http" not in str(actionLink):
                    actionLink = urljoin(self.baseurl, actionLink)
            else:
                actionLink = None
            self.logger.info('Form is %s', form)
            self.logger.info('Request type: %s', requestType)
            self.logger.info('action link is: %s',actionLink)

            formparamList = list()
            params = form.xpath('.//input')
            count = 0
            for param in params:
                if param.xpath('.//@type'):
                    types = param.xpath('.//@type').extract()[0]
                else:
                    types = None

                if param.xpath('.//@name'):
                    name = param.xpath('.//@name').extract()[0]
                else:
                    name = "submit"

                if param.xpath('.//@value'):
                    value = param.xpath('.//@value').extract()[0]
                else:
                    value = ""
                #forming parameters dictionary
                paramdict = dict()
                paramdict["name"]= name
                paramdict["type"] = types
                paramdict["value"] = value
                formparamList.append(paramdict)
            formsdict["method"] = requestType
            formsdict["formactionLink"] = actionLink
            formsdict["params"] = formparamList
            #self.logger.info('This form action link is %s', actionLink)
            #self.logger.info('FormParamList is %s %s',formparamList, requestType)
            #self.sendrequesttoform(requestType, formparamList, actionLink)
            #self.test()
            formList.append(formsdict)
        pageformsdict = dict()
        pageformsdict["pageurl"] = response.url
        pageformsdict["formList"] = formList
        if response.url in self.injectiondictionary:
            formdc = self.injectiondictionary.get(response.url, None)
            formdc["body"] = pageformsdict
        else:
            formdc = dict()
            formdc["body"] = pageformsdict
            formdc["getlist"] = dict()
            self.injectiondictionary[response.url] = formdc



    def test(self):
        self.logger.info('Inside test method-----')

    def addURLinjectList(self, ls, url):
        self.logger.info("Inside Add URL injectLIst method for url %s ", url)
        if url in self.injectiondictionary:
            self.logger.info("Inside if block")
            pageurlsdict = self.injectiondictionary.get(url, None)
            pageurlsdict["getlist"] = ls

        else:
            self.logger.info("Inside else block")
            pageurlsdict = dict()
            pageurlsdict["getlist"] = ls
            pageurlsdict["body"] = dict()
            self.injectiondictionary[url] = pageurlsdict

        self.logger.info("Dictionary value is %s", self.injectiondictionary[url])

    def extractgetList(self, url):
        self.logger.info('Inside extractGetList method for URL %s', url)
        getList = dict()
        paramdc = dict()
        if str(url).find('?') >-1:
            path, query = str(url).split('?')
            queryList = str(query).split('&')
            for ele in queryList:
                if str(ele).index("=") > 0 :
                  key, value = str(ele).split('=')
                  paramdc[key] = value
            getList["path"] = path
            getList["params"] = paramdc
        return getList

    def split_cookies(self, cook):
        self.logger.info("Full cookies are %s", cook)
        index = cook.find("=")
        if index > 0:
            cookiedc = dict()
            cookiedc[cook[0:index]] = cook[index+1:len(cook)-1]
            return cookiedc
        else:
            return None

    def spider_closed(self, spider):
        self.logger.info('*********** Closing SPider********************')
        self.output["injections"] = self.injectiondictionary
        self.writePageURL()
        self.writeOutputJson()
        self.writeRedirects()
        self.logger.info('========================THE END ==========================================')

    def writeRedirects(self):
        data = ""
        if os.path.isfile("output/" + self.redirect_filename):
          with open('output/' + self.redirect_filename, 'r') as myfile:
            data = myfile.read()
          data = data[:len(data)-1]
          f = open('output/' + self.redirect_filename, 'w')
          f.write("{\"redirects\":[" + data+"]}")
          f.close()

    def writePageURL(self):
        self.logger.info("Writing all unique pages to a file")
        f = open("logs/allpages.log", "w")
        for ele in self.visited_url:
            f.write(ele)
            f.write('\n')
        f.close()

    def writeOutputJson(self):
        self.logger.info("dumping json data")
        f = open('output/'+self.output_filename, "w")
        json.dump(self.output, f, indent=2)
        f.close()