# -*- coding: utf-8 -*-
import urlparse
from urllib2 import urlparse

def parse_url(url):
    p = urlparse.urlsplit(url)
    params = dict(urlparse.parse_qsl(p.query))
    return {
        'parse': p,
        'params': params
    }
