#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 19:00:01 2021

@author: linxiangling
"""

import requests 
import json
import flask
from flask import request, Blueprint, jsonify
from models import user

notification_api=Blueprint('notification_api', __name__)

#有人回覆時加入通知
@notification_api.route('add_post_notification')
def add_post_notification():
    user_id=request.values.get('user_id')
    replier_name=request.values.get('replier_name')
    post_id=request.values.get('post_id')
    user.update_notification_add(user_id, replier_name, post_id)
    return jsonify({"message":"success"})
    
#檢查是否有新通知
@notification_api.route('check_new_notification')
def check_new_notification():
    user_id=request.values.get('user_id')
    notification=user.query_notification(user_id)['notification']
    for i in notification:
        if i['new'] == True:
            return jsonify({"new":True})
    return jsonify({"new":False})
   
#點開鈴鐺，new全設false
@notification_api.route('set_notification_new')
def set_notification_new():
    user_id=request.values.get('user_id')
    user.update_notification_new(user_id)
    return jsonify({"message":"success"})
    
#依頁數查看通知
@notification_api.route('check_notification_content')
def check_notification_content():
    user_id=request.values.get('user_id')
    page=request.values.get('page')
    result=user.query_notification_by_page(user_id, int(page))
    return jsonify({"result":result})
    
#查看通知後更改check
@notification_api.route('set_notification_check')
def set_notification_check():
    user_id=request.values.get('user_id')
    id=request.values.get('id')
    user.update_notification_check(user_id, int(id))
    return jsonify({"message":"success"})
