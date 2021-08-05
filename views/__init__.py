#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr  6 23:30:56 2021

@author: linxiangling
"""

from .exchange_api import exchange_api
from .exchange_web import exchange_web
from .rasa_api import rasa_api
from .base_flow_web import base_flow_web
from .base_flow_rasa_api import base_flow_rasa_api
from .tag_api import tag_api
from .login_api import login_api
from .login_web import login_web
from .user_api import user_api
# from .user_web import user_web
from .post_api import post_api
# from .post_web import post_web
from .faq_api import faq_api
from .notification_api import notification_api
from .outersearch_cache_api import outersearch_cache_api

blueprint_prefix = [(exchange_api, "/api"), (exchange_web, "/site"),
                    (rasa_api, "/api"), (base_flow_web, "/site"),
                    (base_flow_rasa_api, "/api"), (tag_api, "/api"),
                    (login_api, "/api"),(login_web, "/site"),
                    (user_api,"/api"),
                    (post_api,"/api"),
                    (faq_api,"/api"),
                    (notification_api, "/api"),
                    (outersearch_cache_api, "/api")]

def register_blueprint(app):
    for blueprint, prefix in blueprint_prefix:
        app.register_blueprint(blueprint, url_prefix=prefix)
    return app
