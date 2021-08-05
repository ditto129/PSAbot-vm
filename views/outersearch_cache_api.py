#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Aug  3 13:06:08 2021

@author: shauangel
"""
# --- flask --- #
from flask import Blueprint, request, jsonify
from datetime import datetime

# --- our models ---- #
from models import outer_data_cache

outersearch_cache_api = Blueprint('outersearch_cache_api', __name__)

#獲取摘要資訊
@outersearch_cache_api.route('/query_cache_by_id', methods=['POST'])
def query_cache_by_id():
    idx = request.get_json()
    try:
        result = outer_data_cache.query_by_id(idx)
        return jsonify(result)
        
    except Exception as e :
        setting_dict = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print("錯誤訊息: ", e)
    return jsonify(setting_dict)

#新增快取資料
@outersearch_cache_api.route('/insert_cache', methods=['POST'])
def insert_cache():
    data = request.get_json()
    try:
        result = outer_data_cache.insert_cache(data['data'], data['type'])
        return jsonify(result)
    except Exception as e :
        setting_dict = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print("錯誤訊息: ", e)
    return jsonify(setting_dict)









