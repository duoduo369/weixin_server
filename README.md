微信公众号服务器
===

描述
---

微信公众号接入的时候要做很多事情，为了简化开发，提供一个django版本的服务器。

用到了[wechat-python-sdk](https://github.com/wechat-python-sdk/wechat-python-sdk)

安装
---

    git clone xxx weixin_server
    cd weixin_server
    source 你的virtualenv
    pip install -r requirements.txt

如果用mysql的话数据库新建一个你settings中的数据库

    python manage.py migrate

配置
---
####ngrok配置
微信服务器测试时需要打洞，用的ngrok, 在项目的ngrok目录下有个配置
start.sh里面把your_domain配置成你想用的二级域名，ngrok.conf下可以看到,
用的ittun.com这样访问的时候就可以用`你配置的二级域名.ittun.com`访问了，
注意这个域名要配置在微信的`URL(服务器地址)`

start.sh后面的8888是你本机服务的端口号，例如我用django的runserver启动在8888
端口，那么这里就是8888

####微信的各种配置
在settings.py目录下新建一个local_settings.py, 根据微信公众号的信息，
把下面的东西补全.

    # weixin config
    WEIXIN_TOKEN = 'Your weixin token'
    WEIXIN_APP_ID = 'Your weixin app id'
    WEIXIN_APP_SECRET = 'Your weixin app secret'
    WEIXIN_ENCODING_AES_KEY = 'Your weixin encoding aes key'
    WEIXIN_ENCRYPT_MODE = 'safe' # safe | compatible | normal

调试
---
ngrok的配置以`/etc/ngrok/ngrok -config=/etc/ngrok/ngrok.conf -subdomain=your_subdomin 8888`为例

    ./weixin_server/manager.py runserver 8888
    ./ngrok/start.sh

然后进入你的公众号发送信息就可以了。


微信开发有关的东西
===

描述
---
首先我们要理解一些事情，在公众号里面，用户直接给公众号发消息、图片、
关注、扫码等等这些操作都会直接给公众号服务器的**80端口**发送请求。

而你可以通过按钮，回复等引导用户进入另外的网站（html页面),此时另外
的网站需要引导用户做微信登录把微信用户转化为自己网站的用户实现用户
转化，这时候用[python-social-oauth](https://github.com/omab/python-social-auth),[django-socail-oauth](https://github.com/omab/django-social-auth)等都可以实现

上面说的外面的网站如果你的服务仅仅是这个服务号(所有用户所有功能仅为
这个服务号服务)，当然可以直接在我们的这个项目里面接入用户系统以及三方登录，此时我们的server就可以提供非80端口的一些html、接口开发，通过微信
的button、回复等引导到这些页面做复杂的逻辑。

开发
---
80端口的一些开发，例如用户给服务号发消息、扫码、关注等事件
可以参考[view.py](https://github.com/duoduo369/weixin_server/blob/master/weixin_server/weixin_server/views.py)

非event类型直接在IndexView里面添加weixin_handler_xxx方法, xxx支持的类型为[sdk message](https://github.com/wechat-python-sdk/wechat-python-sdk/blob/master/wechat_sdk%2Fmessages.py)里面的MESSAGE_TYPES的value, 即:text|image|video|shortvideo|location|link|event这些类型，而如果是event，则可以细化为weixin_handler_event_xxx方法,这里的xxx可以直接看[sdk文档的这个部分](http://wechat-python-sdk.com/official/message/#_1)

注意扫码的scan事件，用户未关注和关注的时候是不一样的，未关注时会先关注，此时应该在weixin_handler_event_subscribe以及weixin_handler_event_scan都做处理，而且两个方法取到的wechat.message.key是不同的，未关注时处理方法为weixin_handler_event_subscribe,key会加一个前缀`qrscene_`, 这点需要注意
