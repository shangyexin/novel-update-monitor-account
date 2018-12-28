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
