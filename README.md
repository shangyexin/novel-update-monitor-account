## novel-update-monitor-account
微信公众号程序实现的功能是，接收爬虫程序提交的章节更新```post```请求，将```post```的小说信息使用微信模板消息发送给用户。

### 使用流程
#### 1. 注册账号
因为只有服务号才能使用模板消息功能，所以我们选择“开箱即用”的微信公众平台测试账号。

点击下面的链接，无需注册即可登录使用：

https://mp.weixin.qq.com/debug/cgi-bin/sandbox?t=sandbox/login

#### 2. 接口配置
关于微信公众平台的接口配置详细步骤大家可以参阅[微信官方文档](https://mp.weixin.qq.com/wiki?t=resource/res_main&id=mp1421135319)。

这里只讲述一下操作步骤，首先填入公众号服务器响应的的URL和使用的Token：

![image](https://img-1252787176.cos.ap-shanghai.myqcloud.com/novel/configure.png)

其中URL中的IP地址是你的服务器IP地址，后面的```/api/wechat```是你的公众号中响应微信Token验证的路径。可以使用Nginx反向代理到Tornado的运行端口（在```config.py中配置```）。下面是Nginx配置示例：
```nginx
server {
    listen 80;
    server_name 35.234.33.8;
 
    location ~ ^/api/wechat {
    proxy_pass http://127.0.0.1:12126;
    }
}
```
Token填入你在```config.py中配置```的```token```即可。

下面是对应的Python代码实现:
```python
# 校验微信服务器签名
class VerifyWechatSignHandler(tornado.web.RequestHandler):
    def get(self):
        signature = self.get_argument('signature', 'UnKnown')
        timestamp = self.get_argument('timestamp', 'UnKnown')
        nonce = self.get_argument('nonce', 'UnKnown')
        echostr = self.get_argument('echostr', 'UnKnown')
        if (signature == 'UnKnown' or timestamp == 'UnKnown' or nonce == 'UnKnown' or echostr ==
                'UnKnown'):
            logger.error('Not enough parameters.')
            self.write("Invalid request : not enough parameters")
        else:
            try:
                # 排序
                params = [config.token, timestamp, nonce]
                params.sort()
                # sha1加密
                hash_sha1 = hashlib.sha1(''.join(params).encode('utf-8'))
                sign = hash_sha1.hexdigest()
                # 对比
                if (signature == sign):
                    logger.info('Correct wechat signature.')
                    self.write(echostr)
                else:
                    logger.error('Wrong wechat signature.')
                    self.write("Invalid request : wrong wechat signature")
            except Exception as e:
                logger.error(e)

def makeApp():
    return tornado.web.Application([
        (r"/api/wechat", VerifyWechatSignHandler)
    ])
```
#### 3. 关注测试账号，获得userid
配置完接口后，我们需要关注测试账号，获得我们的userid，将userid填入到```config.py```中.，具体对应的是下面的```touser```。
```json
notice = {
    "touser": "oQHU46Djs5O3yhsTmYGvDz_Hi0vo",
    "template_id": "oKa0UsZ6xvSlnFChlGGdMMH1O_yq2l91G-sIQPRg2BI",
    "url": "",
    "topcolor": "#FF0000",
    "data": {
        "first": {
            "value": "您订阅的小说更新啦！",
            "color": "#173177"
        },
        "novelName": {
            "value": "",
            "color": "#173177"
        },
        "sectionName": {
            "value": "",
            "color": "#173177"
        },
        "updateTime": {
            "value": "",
            "color": "#173177"
        },
        "remark": {
            "value": "点击详情立刻阅读最新章节↓↓↓",
            "color": "#173177"
        }
    }
```
#### 4. 新增测试模板
点击```新增测试模板```，输入模板标题和模板内容即可创建，需要注意的是模板需符合微信规定语法，我添加的与上面配置中对应的测试模板如下：

```{{first.DATA}} 作品名称：{{novelName.DATA}} 最新章节：{{sectionName.DATA}} 更新时间：{{updateTime.DATA}} {{remark.DATA}}```

模板添加完成后会生成模板ID，填入```config.py```中的```template_id```。

#### 5. 接收更新post并发送给用户
截止到当前步骤，所有的配置已经完成，我们只需要接收指定URL的```post```消息，解析完成后，填入模板中发送给用户即可。

接收消息的URL同样可以在Nginx中配置：
```nginx
server {
    listen 80;
    server_name 35.234.33.8;
 
    location ~ ^/api/novelupdate {
    proxy_pass http://127.0.0.1:12126;
    }
}
```
接收并解析更新```post```的Python代码：
```python
# 接收小说更新推送通知
class NovelUpdateHandler(tornado.web.RequestHandler):
    def post(self):
        try:
            bookName = self.get_argument('bookName', 'UnKnown')
            latestChapter = self.get_argument('latestChapter', 'UnKnown')
            updateTime = self.get_argument('updateTime', 'UnKnown')
            latestUrl = self.get_argument('latestUrl', 'UnKnown')

            if (bookName == 'UnKnown' or latestChapter == 'UnKnown'
                    or updateTime == 'UnKnown' or latestUrl == 'UnKnown'):
                logger.error('Wrong wechat signature.')
                self.write("Invalid request : wrong novel update post info")
            else:
                config.notice['data']['novelName']['value'] = bookName
                config.notice['data']['sectionName']['value'] = latestChapter
                config.notice['data']['updateTime']['value'] = updateTime
                config.notice['url'] = latestUrl
                # print(config.notice)
                putIntoQueue(config.notice)
                self.write("success")
        except Exception as e:
            logger.error(e)
```
给用户发送消息的Python代码：
```python
# 通知用户
def notifyUser(data):
    accessToken = getAccessToken()
    if accessToken is not None:
        notifyUrl = config.baseNotifyUrl + accessToken
        jsonData = json.dumps(data)
        # print(notifyUrl)
        try:
            request = tornado.httpclient.HTTPRequest(notifyUrl, method='POST', body=jsonData)
            syncHttpClient = tornado.httpclient.HTTPClient()
            response = syncHttpClient.fetch(request)
        except Exception as e:
            logger.error(e)
            logger.error('Notify wechat user failed.')
        else:
            logger.info('Notify wechat user success, response is %s.', response.body)
        syncHttpClient.close()
    else:
        config.notificationQueue.append(data)
```

### 运行部署
#### 1. Tmux
这里给大家推荐一款我一直在用的Linux终端复用神器，相信很多人也使用过，那就是```Tmux```。

Tmux可用于在一个终端窗口中运行多个终端会话。不仅如此，还可以通过 Tmux 使终端会话运行于后台或是按需接入、断开会话，这个功能非常实用。这样就可以不用使用```nohup```和```&```在后台运行Python程序。

ubuntu版本下直接apt-get安装：```sudo apt-get install tmux```

centos7版本下直接yum安装：```yum install -y tmux```

#### 2. 程序运行
```Tmux```安装完成后，我们就可以更简单地运行我们的代码了！

运行步骤：
1. ```git clone```源码。
2. 使用```pip3 install -r requirements.txt```安装依赖项
3. 修改```config.py```进行相关配置。
4. 使用```tmux new -s name_by_you```创建一个新的会话
5. 输入命令```python3 account.py```，注意需要使用的为Python的3.x版本，不支持2.0版本。
6. 按下```tmux```快捷键```ctr + b```，再按下键盘```d```键，即可实现程序在后台运行。

完成上面所有步骤后你还不放心的话，可以关闭终端后再次进入，使用```ps -axu | grep python3```查看是否还有你的python进程。

另外在终端使用命令```tmux a -t name_by_you```可以恢复在后台运行的```tmux```会话。
