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
