#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : yasin
# @time   : 18-12-28 下午9:28
# @File   : config.py

import logging.config

logging.config.fileConfig("logger.conf")
logger = logging.getLogger("novel-update-monitor-account")

bindIp = '0.0.0.0'
bindPort = 12126

token = 'VqmB965wOEBrPLNoMkHCfIOpxF0WWFM6'
getTokenUlr = 'https://gitlab.net.cn/wechat/token?type=access_token&secret=f3b2241f967aa3c7966f537cdd82ce11'
baseNotifyUrl = 'https://api.weixin.qq.com/cgi-bin/message/template/send?access_token='

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
}
