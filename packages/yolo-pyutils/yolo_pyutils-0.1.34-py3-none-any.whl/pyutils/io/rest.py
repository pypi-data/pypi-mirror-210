import json
import time
import urllib
import urllib.request
import logging
from pyutils.processing.timer import Timer


class RestClient:

    def __init__(self, retry=3, retry_interval=0.1, timeout=0):
        self.__url = ''
        self.__urls = []
        self.__header = {}
        self.__timeout = timeout
        self.__retry = retry
        self.__retry_interval = retry_interval

    def url(self, url):
        self.__url = url
        self.__urls.clear()
        self.__urls.append(url)
        return self

    def urls(self, urls):
        self.__urls.clear()
        if type(urls) == list:
            self.__urls = urls
            self.__url = urls[0]
        elif type(urls) == str:
            self.__url = urls
            self.__urls.append(urls)
        return self

    def header(self, header):
        self.__header = header
        return self

    def timeout(self, timeout):
        self.__timeout = timeout
        return self

    def retry(self, retry):
        self.__retry = retry
        return self

    def switch_url(self):
        if len(self.__urls) > 1:
            for url in self.__urls:
                if url != self.__url:
                    self.__url = url
                    logging.info("switch url to %s", self.__url)
                    break
        return self

    def __build_request(self, data):
        if data is not None:
            if type(data) is dict:
                data = json.dumps(data)
            if self.__header is not None and len(self.__header) > 0:
                request = urllib.request.Request(self.__url, headers=self.__header, data=data)
            else:
                request = urllib.request.Request(self.__url, data=data)
        else:
            if self.__header is not None and len(self.__header) > 0:
                request = urllib.request.Request(self.__url, headers=self.__header)
            else:
                request = urllib.request.Request(self.__url)
        return request

    def __get_response(self, request):
        if self.__timeout > 0:
            response = urllib.request.urlopen(request, timeout=self.__timeout)
        else:
            response = urllib.request.urlopen(request)
        return response

    def __get_response_body(self, response):
        if response is None:
            return None
        response_body = response.read()
        if response_body is not None:
            response_body = response_body.decode()
        return response_body

    def __request(self, data, get_method=None):
        response = None
        retry = self.__retry
        timer = Timer(start=True)
        while retry > 0:
            try:
                request = self.__build_request(data)
                if get_method is not None:
                    request.get_method = lambda: get_method
                response = self.__get_response(request)
                break
            except Exception as ex:
                if isinstance(ex, urllib.error.HTTPError) and (ex.code == 404 or ex.code == 400):
                    raise ex
                retry -= 1
                logging.warning("Request %s error: %s, left retry cnt:%d", self.__url, str(ex), retry)
                if retry == 0:
                    raise ex
                self.switch_url()
                time.sleep(self.__retry_interval)
        logging.debug("requested url={}, get_method={}, data={}, elapse_ms={}, response_code={}, retry={}".format(
            self.__url, get_method, data, timer.get_elapse_ms(), response.getcode(), self.__retry - retry))
        return response

    def get_response_body_content(self):
        resp = self.__request(None)
        return self.__get_response_body(resp)

    def get(self):
        return self.__request(None)

    def post(self, data):
        return self.__request(data, 'POST')

    def put(self, data):
        return self.__request(data, 'PUT')

    def delete(self, data):
        return self.__request(data, 'DELETE')


def format_url(url, params):
    return format_urls(url, params)


def format_urls(urls, params):
    if params is not None and len(params) > 0:
        encoded_params = urllib.parse.urlencode(params)
        if type(urls) == list:
            new_urls = []
            for url in urls:
                url.append(__join_params(url, encoded_params))
            return new_urls
        elif type(urls) == str:
            return __join_params(urls, encoded_params)
    return urls


def __join_params(url, encoded_params):
    if url.find('?') == -1:
        return url + '?' + encoded_params
    else:
        return url + '&' + encoded_params


def append_url(url, appendix):
    return append_urls(url, appendix)


def append_urls(urls, appendix):
    if appendix is not None:
        if type(urls) == list:
            new_urls = []
            for url in urls:
                new_urls.append(url + appendix)
            return new_urls
        elif type(urls) == str:
            return urls + appendix
    return urls


def get_url_type(use_https):
    return 'https' if use_https is True else 'http'


def retrieve_file(remote_url, local_file_path, reporthook=None):
    urllib.request.urlretrieve(remote_url, filename=local_file_path, reporthook=reporthook)
