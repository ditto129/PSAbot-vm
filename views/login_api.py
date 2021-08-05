# --- flask --- #
from flask import Blueprint, request, jsonify,session
#from flask_security import logout_user, login_required
from flask_login import login_user, current_user, logout_user
# --- google sign-in --- #
from google.oauth2 import id_token
from google.auth.transport import requests

# --- our models ---- #
from models import user
from models.PSAbotLoginManager import UserModel

login_api = Blueprint("login_api", __name__)
GOOGLE_OAUTH2_CLIENT_ID = '417777300686-b6isl0oe0orcju7p5u0cpdeo07hja9qs.apps.googleusercontent.com'

@login_api.route('/google_sign_in', methods=['POST'])
def google_sign_in():
    token = request.json['id_token']

    try:
        # Specify the GOOGLE_OAUTH2_CLIENT_ID of the app that accesses the backend:
        id_info = id_token.verify_oauth2_token(
            token,
            requests.Request(),
            GOOGLE_OAUTH2_CLIENT_ID
        )
        if id_info['iss'] not in ['accounts.google.com', 'https://accounts.google.com']:
            raise jsonify({'error':'Wrong issuer.'})
    except ValueError:
        # Invalid token
        return jsonify({'error':'Invalid token'})
    # 取得使用者資料，若使用者不存在就建立一份
    user_dict = user.query_user(id_info['sub'])
    if user_dict == None:
        user_dict = {
            "_id" : id_info['sub'],
            "role" : 'google_user',
            "name" : id_info['name'],
            "email" : id_info['email'],
            "skill" : [],
            "record" : {
                "posts" : [],
                "responses" : []
            },
            "notification":[]
        }
        user.insert_user(user_dict)
        user_dict = user.query_user(id_info['sub'])
    # --- flask login --- #
    user_now = UserModel(user_dict['_id'])  
    login_user(user_now) 
    session['user_id'] = user_dict['_id']
    session['role'] = user_dict['role']
    return jsonify(user_dict)

@login_api.route('/facebook_sign_in', methods=['POST'])
def facebook_sign_in():
    data = request.get_json()
    user_dict = user.query_user(data['id'])
    # 取得使用者資料，若使用者不存在就建立一份
    if user_dict == None:
        user_dict = {
            "_id" : data['id'],
            "role" : 'facebook_user',
            "name" : data['name'],
            "email" : data['email'],
            "skill" : [],
            "record" : {
                "posts" : [],
                "responses" : []
            },
            "notification":[]
        }
        user.insert_user(user_dict)
        user_dict = user.query_user(data['id'])
    # --- flask login --- #
    user_now = UserModel(user_dict['_id'])  
    login_user(user_now) 
    session['user_id'] = user_dict['_id']
    session['role'] = user_dict['role']
    return jsonify(user_dict)

@login_api.route('/logout', methods=['GET'])
def logout():
    try:
        msg = {
            "msg" : "user " + current_user.get_id() + " logged out."
        }
        logout_user()
        session['user_id'] = None
        session['role'] = None
    except Exception as e :
        msg = {"error" : e.__class__.__name__ + ":" +e.args[0]}
    return jsonify(msg)