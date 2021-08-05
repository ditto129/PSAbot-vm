#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 22:34:45 2021

@author: shauangel
"""
import json
from urllib.request import urlopen
from urllib.parse import quote

class Translate:
    URL = "http://translate.google.cn/translate_a/single?client=gtx&dt=t&dj=1&ie=UTF-8&sl=auto&tl=en&q="
    def __init__(self, string):
        self.urlstr = quote(string.encode('utf-8'))
    
    def getTranslate(self):
        request = urlopen(self.URL + self.urlstr)
        data = json.load(request)
        return data['sentences'][0]['trans']

