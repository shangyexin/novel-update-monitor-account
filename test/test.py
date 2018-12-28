#!/usr/bin/env python
# -*- coding: utf-8 -*-
# @author : yasin
# @time   : 18-12-30 下午2:59
# @File   : test.py

import requests

testPostUrl = 'http://127.0.0.1:12126/api/novelupdate'

bookInfo = {
    'bookName': '测试书名',
    'latestChapter': '测试章节',
    'updateTime': '2018年1月1日',
    'latestUrl': 'https://www.shangyexin.com'
}

if __name__ == '__main__':
    try:
        response = requests.post(testPostUrl, data=bookInfo)
        if (response.text == 'success'):
            print('Post success!')

        else:
            print('Post failed, response text is %s' % response.text)
    except Exception as e:
        print(e)
