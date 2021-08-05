#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 19 20:48:00 2021

@author: linxiangling
"""

import requests 
import json
import flask
from flask import request, Blueprint, jsonify
#from .Translate import Translate



base_flow_rasa_api=Blueprint('base_flow_rasa_api', __name__)
@base_flow_rasa_api.route('base_flow_rasa')
def base_flow_rasa():
    sender_id=request.values.get('sender_id')
    message=request.values.get('message')
    
    conversations_tracker = requests.get('http://localhost:5005/conversations/'+sender_id+'/tracker')
    results = json.loads(conversations_tracker.content.decode('utf8'))
#    print(results)
    #若為輸入描述問題 or 錯誤訊息的流程，則加入 question_or_error_message 前綴以填入整句話當 slot
    if len(results['events'])>=2:
        if 'text' in results['events'][-2].keys():
            #print(results['events'][-2]['text'])
            lastest_bot_reply=results['events'][-2]['text']
            if lastest_bot_reply == "請描述您遇到的問題" or lastest_bot_reply == "請貼上您的錯誤訊息":
                message = 'question_or_error_message, ' + message
                #print(message)
        
    payload = {'sender': sender_id, 'message': message}
    headers = {'content-type': 'application/json'}
    
    r = requests.post('http://localhost:5005/webhooks/rest/webhook', json=payload, headers=headers)
    
    print(r.json())
    if len(r.json()) == 0:
        return jsonify({"message":"no triggered intent"})
    else:
        return r.json()[0]
        
