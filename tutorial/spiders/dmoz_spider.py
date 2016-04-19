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
from urlparse import urlparse, urljoin
from scrapy.conf import settings
from scrapy.exceptions import CloseSpider
import urllib



class DmozSpider(scrapy.Spider):
    name = "app2"
    handle_httpstatus_list = [302,303,301,404,500]
    allowed_domains = ['app2.com']
    baseurl = 'https://app2.com/'
    formdata = {'username': 'admin', 'password': 'AdminAdmin1!'}
    visited_url = set()
    login_url = 'https://app2.com/login/index.php'
    invalidresponse = []
    page_visited = set()
    pagegetdict = dict()
    forminjectionList = []
    output = dict()
    cookies = []
    injectiondictionary = dict()
    start_urls = [
        'https://app2.com/login/index.php'
        #'http://app10.com/index.php'
    ]
    def __init__(self):
        self.output["name"] = self.name
        loginList = []
        loginList.append(self.formdata)
        self.output["logindetails"] = loginList
        self.output["baseurl"] = self.baseurl
        self.output["loginurl"] = self.login_url
        dispatcher.connect(self.spider_closed, signals.spider_closed)

    def parse(self, response):
            print("--------------------------Inside parse method----------------------------------")
            return scrapy.FormRequest(self.login_url,
                                      formdata=self.formdata,
                                      dont_filter=True,
                                      callback=self.check_login)

    def check_login(self, response):
        print("--------------------------Inside check login method----------------------------------")
        print response.body
        if True: #"Admin User" in str(response.body):
            print('Successfully Logged in!!! ')
            cook = response.request.headers.getlist("Cookie")
            print cook
            for c in cook:
                splitval = self.split_cookies(c)
                self.cookies.append(splitval)
            self.logger.info("Cookies are %s", self.cookies)
            self.output["cookies"] = self.cookies
            urllist = list()
            urllist.append("https://app2.com/mod/wiki/filesedit.php?pageid=1&subwiki=1")
            urllist.append('https://app2.com/backup/backupfilesedit.php?currentcontext=22&contextid=22')
            for url in urllist:
                yield Request(url, callback = self.extract_url)
        else:
            print("Logged in Failed-----------------------------------------------------Failed")
            return

    def extract_url(self, response):
        self.logger.info("--------------------------Inside extract_url method for %s", response.url)
        self.extractformdata(response)
        ls = response.xpath('//a/@href').extract()
        status = response.status
        for url in ls:
            if self.validURL(url, status):
                if str(url).startswith('/'):
                    url = urljoin(self.baseurl, url)
                if str(url).find("/") == -1:
                    slashindex = str(response.url).rfind("/")
                    url = str(response.url)[0:slashindex+1]+url
                p = urlparse(url)
                if p.path not in self.page_visited:
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
        if str(status).startswith('4') or url.startswith('#') or "logout" in url:
            return False
        elif url.startswith('/') or url.find("/") == -1:
            return True
        elif self.name in url: # ("http" in url and self.name not in url):
            return True
        else:
            return False

    def extractformdata(self, response):
        self.logger.info('Scanning page %s', response.url)
        if response.xpath('//form') is None:
            return
        formxpath = response.xpath('//form')
        formList = []
        for form in formxpath:
            formsdict = dict()
            if form.xpath('.//@method'):
                requestType = form.xpath('.//@method').extract()[0]
            else:
                requestType = None
            if form.xpath('.//@action'):
                actionLink = form.xpath('.//@action').extract()[0]
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
        self.logger.info('========================THE END ==========================================')

    def writePageURL(self):
        self.logger.info("Writing all unique pages to a file")
        f = open("logs/allpages.log", "w")
        for ele in self.visited_url:
            f.write(ele)
            f.write('\n')
        f.close()

    def writeOutputJson(self):
        self.logger.info("dumping json data")
        f = open("/home/user/tutorial/phase1Output.json", "w")
        json.dump(self.output, f, indent=2)
        f.close()