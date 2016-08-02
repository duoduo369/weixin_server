# -*- coding: utf-8 -*-
from django.conf import settings
from django.core import cache
from md5 import md5
from uuid import uuid4
from datetime import datetime
from .utils import create_mch_billno
import requests

try:
    cache = cache.get_cache('general')
except Exception:
    cache = cache.cache

SENDGROUPREDPACK_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendgroupredpack'
SENDREDPACK_URL = 'https://api.mch.weixin.qq.com/mmpaymkttransfers/sendredpack'

def sign(params):
    '''
    https://pay.weixin.qq.com/wiki/doc/api/tools/cash_coupon.php?chapter=4_3
    '''
    params = [(str(key), str(val)) for key, val in params.iteritems() if val]
    sorted_params_string = '&'.join('='.join(pair) for pair in sorted(params))
    sign = '{}&key={}'.format(sorted_params_string, settings.WEIXIN_PAY_API_KEY)
    return md5(sign).hexdigest().upper()

# TODO: 裂变接口没测过
def sendgroupredpack(re_openid='', total_amount=0,
        total_num=1, send_name=u'发送者', mch_billno=None,
        amt_type='ALL_RAND', wishing='', act_name='',
        remark=''):
    randuuid = uuid4()
    nonce_str = str(randuuid).replace('-', '')
    mch_id = settings.WEINXIN_PAY_MCH_ID
    wxappid = settings.WEIXIN_APP_ID
    if not mch_billno:
        mch_billno = create_mch_billno(mch_id)

    params = {
        'mch_billno': mch_billno,
        'mch_id': mch_id,
        'wxappid': wxappid,
        'send_name': send_name,
        're_openid': re_openid,
        'total_amount': total_amount,
        'amt_type': amt_type,
        'total_num': total_num,
        'wishing': wishing,
        'act_name': act_name,
        'remark': remark,
        'nonce_str': nonce_str,
    }
    sign_string = sign(params)

    template = ''' <xml>
   <sign><![CDATA[{sign}]]></sign>
   <mch_billno><![CDATA[{mch_billno}]]></mch_billno>
   <mch_id><![CDATA[{mch_id}]]></mch_id>
   <wxappid><![CDATA[{wxappid}]]></wxappid> 
   <send_name><![CDATA[{send_name}]]></send_name> 
   <re_openid><![CDATA[{re_openid}]]></re_openid> 
   <total_amount><![CDATA[{total_amount}]]></total_amount> 
   <amt_type><![CDATA[{amt_type}]]></amt_type> 
   <total_num><![CDATA[{total_num}]]></total_num> 
   <wishing><![CDATA[{wishing}]]></wishing>
   <act_name><![CDATA[{act_name}]]></act_name> 
   <remark><![CDATA[{remark}]]></remark> 
   <nonce_str><![CDATA[{nonce_str}]]></nonce_str> 
</xml>
'''
    params['sign'] = sign_string
    content = template.format(**params)
    headers = {'Content-Type': 'application/xml'}
    print content
    respose = requests.post(SENDGROUPREDPACK_URL, data=content, headers=headers)
    return respose


def sendredpack(re_openid='', total_amount=0,
        total_num=1, send_name=u'发送者', mch_billno=None,
        wishing='', act_name='', remark='',
        client_ip='127.0.0.1'):
    randuuid = uuid4()
    nonce_str = str(randuuid).replace('-', '')
    mch_id = settings.WEINXIN_PAY_MCH_ID
    wxappid = settings.WEIXIN_APP_ID
    if not mch_billno:
        mch_billno = create_mch_billno(mch_id)

    params = {
        'mch_billno': mch_billno,
        'mch_id': mch_id,
        'wxappid': wxappid,
        'send_name': send_name,
        're_openid': re_openid,
        'total_amount': total_amount,
        'total_num': total_num,
        'wishing': wishing,
        'client_ip': client_ip,
        'act_name': act_name,
        'remark': remark,
        'nonce_str': nonce_str,
    }
    sign_string = sign(params)

    template = '''<xml>
   <sign><![CDATA[{sign}]]></sign>
   <mch_billno><![CDATA[{mch_billno}]]></mch_billno>
   <mch_id><![CDATA[{mch_id}]]></mch_id>
   <wxappid><![CDATA[{wxappid}]]></wxappid> 
   <send_name><![CDATA[{send_name}]]></send_name> 
   <re_openid><![CDATA[{re_openid}]]></re_openid> 
   <total_amount><![CDATA[{total_amount}]]></total_amount> 
   <total_num><![CDATA[{total_num}]]></total_num> 
   <wishing><![CDATA[{wishing}]]></wishing>
   <client_ip><![CDATA[{client_ip}]]></client_ip>
   <act_name><![CDATA[{act_name}]]></act_name> 
   <remark><![CDATA[{remark}]]></remark> 
   <nonce_str><![CDATA[{nonce_str}]]></nonce_str> 
</xml>
'''
    params['sign'] = sign_string
    content = template.format(**params)
    headers = {'Content-Type': 'application/xml'}
    print content
    respose = requests.post(SENDREDPACK_URL, data=content, headers=headers,
            cert=(settings.WEIXIN_PAY_CERT_PATH, settings.WEIXIN_PAY_CERT_KEY_PATH))
    return respose
