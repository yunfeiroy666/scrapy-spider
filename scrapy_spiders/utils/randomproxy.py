from scrapy.log import logger
from proxy.request_proxy_ip import get_proxy_ip_from_server


class RandomProxy(object):
    """"
    It's the middleware to add proxy to the scrapy request
    """

    def __init__(self, settings):
        self.proxy = get_proxy_ip_from_server()
        self.counter = 0
        # default change ip for every 50 requests
        self.request_limit = settings.get('REQUEST_LIMIT') if settings.get('REQUEST_LIMIT') else 50

    @classmethod
    def from_crawler(cls, crawler):
        return cls(crawler.settings)

    def process_request(self, request, spider):
        # Don't overwrite with a random one (server-side state for IP)
        if 'proxy' in request.meta:
            return
        # If reached the limit, request a new ip
        if self.counter >= self.request_limit:
            self.proxy = get_proxy_ip_from_server()
            self.counter = 0
            logger.info('Reached request limit. Request a new proxy {0}'.format(self.proxy))
        if self.proxy:
            request.meta['proxy'] = self.proxy
        self.counter += 1

    def process_exception(self, request, exception, spider):
        if 'proxy' in request.meta:
            proxy = request.meta['proxy']
            logger.info('Removing failed proxy {0}'.format(proxy))
            self.proxy = get_proxy_ip_from_server()
            if self.proxy:
                request.meta['proxy'] = self.proxy
        else:
            request.meta['proxy'] = self.proxy
        return request