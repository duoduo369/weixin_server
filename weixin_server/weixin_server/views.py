# -*- coding: utf-8 -*-
import logging
from django.views.generic import View
from django.http.response import HttpResponse
from weixin.utils import wechat
from wechat_sdk.exceptions import ParseError
from .mixins import WeixinDispatchMixin

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
        response_xml = parsed_wechat.response_text(content=u'感谢您的关注，这是学堂在线的测试账号')
        return HttpResponse(response_xml, content_type='application/xml')
