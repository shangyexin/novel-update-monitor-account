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

import config
from config import logger

class MainHandler(tornado.web.RequestHandler):
    def get(self):
        self.write("Welcome to use wechat access token server!")


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
    def get(self):
        self.write("NovelUpdateHandler!")


def makeApp():
    return tornado.web.Application([
        (r"/api/wechat", VerifyWechatSignHandler),
        (r"/api/novelupdate", NovelUpdateHandler),
        (r"/", MainHandler),
    ])


if __name__ == "__main__":
    app = makeApp()
    app.listen(config.bindPort, address=config.bindIp)
    logger.info('Start to run nove update monitor account!')
    tornado.ioloop.IOLoop.instance().start()
