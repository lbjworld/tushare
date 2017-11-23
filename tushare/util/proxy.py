# coding: utf-8
from __future__ import unicode_literals

import logging
import requests
from pyquery import PyQuery as pq

logger = logging.getLogger(__name__)

PROXY_SITE_URL = 'http://www.kuaidaili.com/free/{proxy_type}/{page}/'


def _parse_page(page_doc, http_type='http'):
    """
    Args:
        page_doc(object): PyQuery object
        http_type(string): [http, https]
    Returns:
        proxies(list)
    """
    _proxies = []
    proxy_item_selector = '#list > table > tbody > tr'
    for proxy_item in page_doc(proxy_item_selector).items():
        ip_col_selector = 'td:nth-child(1)'
        port_col_selector = 'td:nth-child(2)'
        type_col_selector = 'td:nth-child(4)'
        ip = proxy_item(ip_col_selector).text()
        port = proxy_item(port_col_selector).text()
        pro_type = proxy_item(type_col_selector).text()
        if pro_type and pro_type.lower() == http_type:
            _proxies.append({pro_type.lower(): '{ip}:{port}'.format(ip=ip, port=port)})
    return _proxies


def _get_proxy_page(page_num=5, timeout=10):
    _proxies = []
    for page in range(page_num):
        page += 1
        for proxy_type in ['inha', 'intr']:
            url = PROXY_SITE_URL.format(proxy_type=proxy_type, page=page)
            try:
                r = requests.get(url, timeout=timeout)
                doc = pq(r.content())
            except Exception as e:
                logger.error('get proxy page error: {e}'.format(e=e))
                continue
            _proxies.extend(_parse_page(doc))
    return _proxies


def _valid_proxy(proxy, target_url='http://www.baidu.com'):
    try:
        r = requests.get(target_url, timeout=0.5, proxies=proxy)
        if r.status_code != 200:
            return False
    except:
        return False
    return True


def get_proxies(count=10):
    _candidates = _get_proxy_page()
    _proxies = []
    for c in _candidates:
        if _valid_proxy(c):
            _proxies.append(c)
        if len(_proxies) >= count:
            break
    return _proxies
