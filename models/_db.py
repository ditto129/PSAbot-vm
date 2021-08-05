#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 23 21:46:58 2021

@author: linxiangling
"""

from pymongo import MongoClient


DB = MongoClient('mongodb+srv://pqamanager:pass123word@pqacluster0.umi6y.mongodb.net/test')['PQAbot']

TAG_COLLECTION = DB['Tag']
USER_COLLECTION = DB['User']
INNER_POST_COLLECTION = DB['InnerPost']
OUTER_DATA_COLLECTION = DB['OuterData']
OUTER_DATA_CACHE_COLLECTION = DB['OuterDataCache']