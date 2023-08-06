# -*- coding: utf-8 -*-
"""
爬虫框架
"""
import abc
import logging
from typing import Any, Optional, Union
import urllib.request

import requests
from requests.adapters import HTTPAdapter, Retry
from bs4 import BeautifulSoup
from logdecorator import log_on_error


class BaseCrawler(abc.ABC):
    """
    爬虫基类
    """

    def __init__(self, request_url_prefix: Optional[str] = None, request_require_proxy: bool = False,
                 request_retry: int = 0, request_retry_backoff_factor: int = 0, html_parser: str = 'lxml'):
        """

        :param request_url_prefix:
        :param request_require_proxy:
        :param request_retry:
        :param request_retry_backoff_factor:
        :param html_parser:
        """
        # 请求配置
        self.request_url_prefix = request_url_prefix
        self.request_require_proxy = request_require_proxy
        self.request_retry = Retry(total=request_retry, backoff_factor=request_retry_backoff_factor)
        # 设置请求Session
        self.set_request_session()
        # 解析配置
        self.html_parser = html_parser

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()

    def set_request_session(self):
        # 初始化session
        self.session = requests.Session()
        # 请求重试策略
        # https://stackoverflow.com/questions/15431044/can-i-set-max-retries-for-requests-request
        # https://urllib3.readthedocs.io/en/latest/reference/urllib3.util.html#module-urllib3.util.retry
        if self.request_url_prefix:
            self.session.mount(self.request_url_prefix, HTTPAdapter(max_retries=self.request_retry))
        else:
            # 默认对HTTP和HTTPS请求处理
            self.session.mount('http://', HTTPAdapter(max_retries=self.request_retry))
            self.session.mount('https://', HTTPAdapter(max_retries=self.request_retry))
        # 请求代理
        if self.request_require_proxy:
            proxies = {k: v.replace('https://', 'http://') for k, v in urllib.request.getproxies().items()}
            self.session.proxies.update(proxies)

    def close(self):
        self.session.close()

    def prepare_response(self, response: requests.Response) -> Union[BeautifulSoup, list, dict, str, requests.Response]:
        """
        预处理响应体
        :param response:
        :return:
        """
        if 'text/html' in response.headers['Content-Type']:
            return BeautifulSoup(response.content, self.html_parser)
        if 'application/json' in response.headers['Content-Type']:
            return response.json()
        try:
            return response.text
        except UnicodeDecodeError:
            return response

    @log_on_error(log_level=logging.ERROR, message="Error on requesting {url:s}: {e!r}",
                  on_exceptions=requests.exceptions.RequestException)
    def request(self, method: str, url: str, **kwargs) -> Any:
        """
        请求
        :param method:
        :param url:
        :param kwargs:
        :return:
        """
        return self.session.request(method, url, **kwargs)

    def get(self, url, **kwargs) -> Any:
        return self.request(method='GET', url=url, **kwargs)

    def post(self, url, data=None, json=None, **kwargs) -> Any:
        return self.request(method='POST', url=url, data=data, json=json, **kwargs)

    def parse(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def save(self, *args, **kwargs) -> Any:
        raise NotImplementedError()

    def run(self, *args, **kwargs) -> None:
        raise NotImplementedError()
