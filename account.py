#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : yasin
# @time   : 18-12-28 下午9:23
# @File   : account.py

import tornado.ioloop
import tornado.web
import tornado.httpclient
import tornado.httputil
import tornado.gen
import hashlib
import json
import copy

import config
from config import logger


class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to use novel update monitor account!")


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


def makeApp():
    return tornado.web.Application([
        (r"/api/wechat", VerifyWechatSignHandler),
        (r"/api/novelupdate", NovelUpdateHandler),
        (r"/", MainHandler),
    ])


# 获取access token
def getAccessToken():
    accessToken = None
    request = tornado.httpclient.HTTPRequest(config.getTokenUlr, method='GET')
    # 同步客戶端
    syncHttpClient = tornado.httpclient.HTTPClient()
    try:
        response = syncHttpClient.fetch(request)
    except Exception as e:
        logger.error(e)
        logger.error('Get access token failed.')
    else:
        logger.info('Get access token response body: %s', response.body)
        # response body里面json格式的字典
        resDict = json.loads(response.body.decode('utf8'))
        accessToken = resDict['access_token']
        # print(accessToken)
    syncHttpClient.close()

    return accessToken

# 判断是否在勿扰模式时间段
def inSlientMode():
    from datetime import datetime, timedelta, timezone
    # 拿到UTC时间，并强制设置时区为UTC+0:00:
    utc_dt = datetime.utcnow().replace(tzinfo=timezone.utc)
    # astimezone()将转换时区为北京时间:
    bj_dt = utc_dt.astimezone(timezone(timedelta(hours=8)))
    hour = bj_dt.hour
    if hour >= config.slientModeStartTime or hour < config.slientModeEndTime:
        return True
    else:
        return False

# 将消息放入通知队列
def putIntoQueue(data):
    # 勿扰模式打开且在勿扰模式时间段
    if config.slientMode is True and inSlientMode() is True:
        # list直接append字典会得到重复的值，所以需要复制后再append
        dataCopy = copy.deepcopy(data)
        config.notificationQueue.append(dataCopy)
        logger.info(config.notificationQueue)
    else:
        # 否则直接通知用户
        notifyUser(data)

# 从队列里取出更新消息
def pickFromQueue():
    if inSlientMode() is not True and len(config.notificationQueue) > 0:
        for data in config.notificationQueue[:]:
            notifyUser(data)
            config.notificationQueue.remove(data)

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


if __name__ == "__main__":
    app = makeApp()
    app.listen(config.bindPort, address=config.bindIp)
    logger.info('Start to run novel update monitor account!')
    if config.slientMode is True:
        tornado.ioloop.PeriodicCallback(pickFromQueue, 5*60*1000).start()
    tornado.ioloop.IOLoop.instance().start()
