host="0.0.0.0",#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Mar 15 16:44:08 2021

@author: linxiangling
"""

#from flask import Flask
#from flask import render_template

#app = Flask(__name__)
#@app.route("/")
#def hello():
#    return render_template('test.html')
#if __name__ == "__main__":
#    app.run(host="0.0.0.0", port=55001)

from flask import Flask
#from flask_apscheduler import APScheduler
#from flask_security import Security
from flask_cors import CORS
#import models
from views import register_blueprint
#from lib import config
from os import urandom
from models.PSAbotLoginManager import PSAbotLoginManager,UserModel


def create_app():
    app = Flask(__name__)
    app.jinja_env.auto_reload = True
    app.config['SECRET_KEY'] = urandom(24).hex()
    #app.config.from_object(config.Config())
    CORS(app)
    # models setup
    #models.setup(app)

    # security setup

   # Security(app, models.user.USER_DATASTORE,login_form=models.user.ExtendedLoginForm)
    ''' --- login manager ---- '''
    login_manager = PSAbotLoginManager(app)
    @login_manager.user_loader
    def user_loader(user_id):  
        user_now = UserModel(user_id)   
        return user_now
    ''' ---------------------- '''
    # register app
    register_blueprint(app)
    return app


#def refresh_schedule():
#    models.reschedule.refresh_schedule()




if __name__ == "__main__":
    # scheduler=APScheduler()
    app = create_app()
    # scheduler.init_app(app)
    # scheduler.start()
    app.run(host='0.0.0.0', port=55001)
    
#"192.168.111.128",port=55001

