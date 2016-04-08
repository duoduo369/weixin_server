# -*- coding: utf-8 -*-
import logging
from django.views.generic import View
from django.http.response import HttpResponse
from weixin.utils import wechat
from wechat_sdk.exceptions import ParseError

log = logging.getLogger(__name__)

class IndexView(View):

    def get(self, request):
        signature = request.GET.get('signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        echostr = request.GET.get('echostr', '')
        if wechat.check_signature(signature, timestamp, nonce):
            return HttpResponse(echostr)
        return HttpResponse('signature error')

    def post(self, request):
        content = request.body
        signature = request.GET.get('signature', '')
        msg_signature = request.GET.get('msg_signature', '')
        timestamp = request.GET.get('timestamp', '')
        nonce = request.GET.get('nonce', '')
        try:
            wechat.parse_data(
                    content,
                    msg_signature=msg_signature,
                    timestamp=timestamp,
                    nonce=nonce)
        except ParseError:
            return HttpResponse('Invalid Body Text')
        response_xml = wechat.response_text(content='get: {}'.format(wechat.message.content))
        return HttpResponse(response_xml, content_type='application/xml')
