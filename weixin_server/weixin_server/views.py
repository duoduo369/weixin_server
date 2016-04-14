# -*- coding: utf-8 -*-
import logging
from django.views.generic import View
from django.http.response import HttpResponse
from weixin.utils import wechat
from weixin.qrcode import create_temp_qrcode, create_permanent_qrcode
from wechat_sdk.exceptions import ParseError
from .mixins import WeixinDispatchMixin
from django.core.cache import cache

log = logging.getLogger(__name__)

class IndexView(View, WeixinDispatchMixin):

    def get(self, request):
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        if wechat.check_signature(signature, timestamp, nonce):
            return HttpResponse(echostr)
        return HttpResponse('signature error')

    def post(self, request, *args, **kwargs):
        return self.dispatch_weixin(request, *args, **kwargs)

    def weixin_handler_text(self, request, parsed_wechat, *args, **kwargs):
        response_xml = parsed_wechat.response_text(content=u'get: {}'.format(wechat.message.content))
        return HttpResponse(response_xml, content_type='application/xml')

    def weixin_handler_image(self, request, parsed_wechat, *args, **kwargs):
        response_xml = wechat.response_image(media_id=parsed_wechat.message.media_id)
        return HttpResponse(response_xml, content_type='application/xml')

    def weixin_handler_event(self, request, parsed_wechat, *args, **kwargs):
        response_xml = parsed_wechat.response_text(
            content=u'event事件: {}'.format(
                parsed_wechat.message.type))
        return HttpResponse(response_xml, content_type='application/xml')

    def weixin_handler_event_subscribe(self, request, parsed_wechat, *args, **kwargs):
        response_xml = parsed_wechat.response_text(
                content=u'感谢您的关注，这是学堂在线的测试账号')
        return HttpResponse(response_xml, content_type='application/xml')

    def weixin_handler_event_click(self, request, parsed_wechat, *args, **kwargs):
        message = parsed_wechat.message
        if message.key == 'CLICK_TEST_01':
            articles = [{
                'title': u'V2EX',
                'description': u'V2EX程序员的社区',
                'url': u'http://www.v2ex.com/',
            }, {
                'title': u'第二条新闻标题, 这条新闻无描述',
                'picurl': u'http://gaitaobao3.alicdn.com/tfscom/TB11DjAIFXXXXaTXFXXXXXXXXXX_!!0-item_pic.jpg',
                'url': u'http://xiapingwang.com/show/250555'
            }]
            response_xml = parsed_wechat.response_news(articles)
            return HttpResponse(response_xml, content_type='application/xml')
        elif message.key == 'CLICK_TEMP_QRCODE_01':
            key = 1
            cache_key = 'qrcode_temp_{}'.format(key)
            qrcode_url = cache.get(cache_key)
            if not qrcode_url:
                qrcode_url = create_temp_qrcode(key)
                cache.set(cache_key, qrcode_url, 60*60)
            response_xml = parsed_wechat.response_text(content=u'<img src="{}"/>'.format(qrcode_url))
            return HttpResponse(response_xml, content_type='application/xml')
        elif message.key == 'CLICK_PERMANENT_QRCODE_01':
            key = 'permanent_1'
            cache_key = 'qrcode_temp_{}'.format(key)
            qrcode_url = cache.get(cache_key)
            if not qrcode_url:
                qrcode_url = create_permanent_qrcode(key)
                cache.set(cache_key, qrcode_url, 60*60)
            response_xml = parsed_wechat.response_text(content=u'<img src="{}"/>'.format(qrcode_url))
            return HttpResponse(response_xml, content_type='application/xml')

        return self.weixin_handler_event(
                request, parsed_wechat, *args, **kwargs)
