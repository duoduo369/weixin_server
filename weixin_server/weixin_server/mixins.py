# -*- coding: utf-8 -*-
from weixin.wechat import get_wechat
from wechat_sdk.messages import MESSAGE_TYPES, EventMessage

wechat = get_wechat()

REVERSED_MESSAGE_TYPES = {value:key for key, value in MESSAGE_TYPES.iteritems()}

class WeixinDispatchMixin(object):

    def dispatch_weixin(self, request, *args, **kwargs):
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
        handler_name = self.get_weixin_handler_name(request, wechat, *args, **kwargs)
        handler = getattr(self, handler_name, self.http_method_not_allowed)
        return handler(request, wechat, *args, **kwargs)

    def get_weixin_handler_name(self, request, parsed_wechat, *args, **kwargs):
        message = parsed_wechat.message
        if isinstance(message, EventMessage):
            event_name = REVERSED_MESSAGE_TYPES[type(message)]
            event_detail_name = 'weixin_handler_{}_{}'.format(event_name, message.type)
            if hasattr(self, event_detail_name):
                event_name = event_detail_name
                return event_name
        return u'weixin_handler_{}'.format(REVERSED_MESSAGE_TYPES.get(type(message), 'unsupport'))
