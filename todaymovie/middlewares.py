# -*- coding: utf-8 -*-

from scrapy import signals
import re
import random
import requests
import execjs
import logging


class TodaymovieSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class TodaymovieDownloaderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request, spider):
        # Called for each request that goes through the downloader
        # middleware.

        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    def process_response(self, request, response, spider):
        # Called with the response returned from the downloader.

        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        pass

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)


class RandomUserAgentMiddleWare(object):
    logger = logging.getLogger(__name__)

    def __init__(self, settings):
        self.USER_AGENTS = settings.getlist('USER_AGENTS')

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        user_agent = random.choice(self.USER_AGENTS)
        self.logger.info(f'当前UA, {user_agent}')
        request.headers.setdefault('User-Agent', user_agent)


class CookieDownloadMiddleware(object):
    logger = logging.getLogger(__name__)

    def process_response(self, request, response, spider):
        if response.status == 521:
            self.logger.info('{:-^60}'.format('返回521'))
            # js = 'function' + re.search(
            #     r'(?<=function)(.*?)(?=</script>)', response.text).group(1).replace('eval("qo=eval;qo(po);");', 'return po')
            # func = re.search(
            #     r'setTimeout\("(.*?)\((\d+)\)".*?\)', response.text).groups()
            # func_name = func[0]
            # func_para = func[1]
            # cookies = execjs.compile(js).call(func_name, func_para)
            # cookies_val = re.search(
            #     r"(?<=document.cookie=')(.*?)(?=; )", cookies).group(1)
            cookies_val = self.parse_cookies(response.text)
            self.logger.info(f'>>>获取到cookie, {cookies_val}')
            cookies_dict = self.listToDict(cookies_val.split('='))
            new_request = request.replace(
                cookies=cookies_dict, dont_filter=True)
            return new_request
        return response

    def listToDict(self, lst):
        op = {lst[i]: lst[i + 1] for i in range(0, len(lst), 2)}
        return op

    def parse_cookies(self, txt):
        js = 'function' + re.search(
            r'(?<=function)(.*?)(?=</script>)', txt).group(1).replace('eval("qo=eval;qo(po);");', 'return po')
        func = re.search(
            r'setTimeout\("(.*?)\((\d+)\)".*?\)', txt).groups()
        func_name = func[0]
        func_para = func[1]
        cookies = execjs.compile(js).call(func_name, func_para)
        cookies_val = re.search(
            r"(?<=document.cookie=')(.*?)(?=; )", cookies).group(1)
        return cookies_val


class ProxyMiddleware(object):
    logger = logging.getLogger(__name__)

    def __init__(self):
        self.proxy_list = self.get_proxies()

    def process_request(self, request, spider):
        if request.url != 'http://theater.mtime.com/China_Sichuan_Province_Chengdu/':
            self.logger.info(
                f'>> >【请求】：url + cookies,{request.url}, {request.cookies}')
            proxy = random.choice(self.proxy_list)
            self.logger.info(f'>>>使用proxy, {proxy}')
            request.meta['proxy'] = 'http://' + proxy

    def process_response(self, request, response, spider):
        self.logger.info(
            f'>>>【返回】：url + 状态码, {response.url}, {response.status}')
        if str(response.status).startswith('3') or str(response.status).startswith('4') or str(response.status).startswith('5'):
            self.logger.info('{:-^60}'.format(f'返回{response.status}，切换代理'))
            proxy = random.choice(self.proxy_list)
            new_request = request.replace(
                meta={'proxy': proxy}, dont_filter=True)
            return new_request
        return response

    def get_proxies(self, url='http://127.0.0.1:5000/all'):
        proxy_list = requests.get(url).json().get('result')
        return list(filter(lambda s: 'socks' not in s, proxy_list))
