from scrapy.contrib.downloadermiddleware.retry import RetryMiddleware
from scrapy.selector import HtmlXPathSelector
from scrapy.utils.response import get_meta_refresh
from scrapy import log
import json
import os.path
from spiders.dmoz_spider import DmozSpider

class CustomRetryMiddleware(RetryMiddleware):

    redirect_dict = {}
    def process_response(self, request, response, spider):
        get_list = {}
        obj = DmozSpider()
        redirect_filename = 'output/' + obj.redirect_filename
        from_url = request.url
        to_url = ''
        if response.status in [301,302,303, 307] and "Location" in response.headers:
            to_url = response.headers["Location"]
            get_list = self.extractgetList(from_url)
            redirect_dict = {"from_url":from_url,"params":get_list,"to_url":to_url}
            f = open(redirect_filename,'a')
            json.dump(redirect_dict,f,indent = 2)
            f.write(",")
            f.close()
            log.msg("trying to redirect : %s -> %s" %(from_url,to_url), level=log.INFO)
            reason = 'redirect %d' %response.status
            return self._retry(request, reason, spider) or response
        interval, redirect_url = get_meta_refresh(response)
        # handle meta redirect
        if redirect_url:
            get_list = self.extractgetList(to_url)
            redirect_dict = {"from_url":from_url,"params":get_list,"to_url":to_url}
            f = open(redirect_filename,'a')
            json.dump(redirect_dict,f,indent = 2)
            f.write(",")
            f.close()
            log.msg("trying to redirect : %s -> %s" %(from_url,to_url), level=log.INFO)
            reason = 'meta'
            return self._retry(request, reason, spider) or response
        return response


    def extractgetList(self, url):
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
