
# --- flask --- #
from flask import Blueprint, request, jsonify
# from flask_security import logout_user, login_required
'''湘的import'''
from flask import Flask, flash, redirect, url_for
import base64
import os
from os import path
from werkzeug.utils import secure_filename
import asyncio
'''end'''
# --- our models ---- #
from models import user
# rom models import psa_excption_handler

user_api = Blueprint("user_api", __name__)

# 取得使用者簡易資料，不包含技能樹、發文紀錄
@user_api.route('/query_user_profile', methods=['POST'])
def query_user_profile():
    data = request.get_json()
    user_dict = user.query_user(data['_id'])
    try:
        user_profile = {
            '_id' : user_dict['_id'],
            'name': user_dict['name'],
            'email':user_dict['email'],
        }
        
    except Exception as e :
        user_profile = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print("錯誤訊息: ", e)
    return jsonify(user_profile)


# 取得使用者發文紀錄
@user_api.route('/query_user_post_list', methods=['POST'])
def query_user_post_list():
    data = request.get_json()
    user_dict = user.query_user(data['_id'])
    try:
        user_record = user_dict['record']['posts']
        page_size = data['page_size']
        page_number = data['page_number']
        user_posts = {
            "post_count": len(user_record),
            "post_list": user_record[page_size * (page_number - 1) : page_size * (page_number - 1) + page_size]
        }
    except Exception as e :
        user_posts = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print(e)
    return jsonify(user_posts)
    
# 取得使用者回覆紀錄
@user_api.route('/query_user_response_list', methods=['POST'])
def query_user_response_list():
    data = request.get_json()
    user_dict = user.query_user(data['_id'])
    try:
        user_record = user_dict['record']['responses']
        page_size = data['page_size']
        page_number = data['page_number']
        user_posts = {
            "post_count": len(user_record),
            "post_list": user_record[page_size * (page_number - 1) : page_size * (page_number - 1) + page_size]
        }
    except Exception as e :
        user_posts = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print(e)
    return jsonify(user_posts)

# 取得使用者技能樹
@user_api.route('/query_user_skill', methods=['POST'])
def query_user_skill():
    data = request.get_json()
    user_dict = user.query_user(data['_id'])
    try:
        user_skill = user_dict['skill']
    except Exception as e :
        user_skill = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print(e)
    return jsonify(user_skill)
    
# 前端OK
# 編輯使用者簡易資料，不包含技能樹、發文紀錄
@user_api.route('/update_user_profile', methods=['POST'])
def update_user_profile():
    data = request.get_json()
    try:
        user_profile = {
            '_id' : data['_id'],
            'name': data['name'],
        }
        user.update_user(user_profile)
    except Exception as e :
        user_profile = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print(e)
    return jsonify(user_profile)

# 編輯使用者興趣
@user_api.route('/update_user_interest', methods=['POST'])
def update_user_interest():
    data = request.get_json()
    try:
        user.update_user_interest(data['_id'],data['tag'])
    except Exception as e :
        data = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print(e)
    return jsonify(data)
    
''' 湘的 start '''
#UPLOAD_FOLDER = '/Users/linxiangling/Documents/GitHub/PQAbot/static/images/user_img'
#UPLOAD_FOLDER = '/Users/cihcih/Documents/GitHub/PQAbot/static/images/user_img'
UPLOAD_FOLDER = "/home/bach/PSAbot-vm/static/images/user_img"
ALLOWED_EXTENSIONS = {'png'}

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

#判斷檔案是否合法
def allowed_file(filename):
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 前端OK
@user_api.route('save_user_img', methods=['post'])
#將書的img存入目錄
def save_user_img():
    # check if the post request has the file part
    if 'img' not in request.files:
         flash('No file part')
         return redirect(request.url)
    file = request.files['img']
    # if user does not select file, browser also
    # submit an empty part without filename
    if file.filename == '':
         flash('No selected file')
         return redirect(request.url)
    if file and allowed_file(file.filename):
         filename = secure_filename(file.filename)
         file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
         return redirect(url_for('base_flow_web.PSAbot'))
    else:
         return jsonify({'message':'falied'})

# 前端OK
@user_api.route('read_image', methods=['get'])
#讀取照片
def read_image():
    user_id=request.values.get('user_id')
    
    #define an image object with the location.
    #file = "/Users/linxiangling/Documents/GitHub/PQAbot/static/images/user_img/"+user_id+".png"
#    file = "/Users/cihcih/Documents/GitHub/PQAbot/static/images/user_img/"+user_id+".png"
    file = "/home/bach/PSAbot-vm/static/images/user_img/"+user_id+".png"
    #file = "../images/"+book_id+".png"
    #Open the image in read-only format.
    if path.exists(file) == False:
        #file = "/Users/linxiangling/Documents/GitHub/PQAbot/static/images/user_img/defaultPic.png"
#        file = "/Users/cihcih/Documents/GitHub/PQAbot/static/images/user_img/defaultPic.png"
        file = "/home/bach/PSAbot-vm/static/images/user_img/defaultPic.png"
        #file = "../static/images/user_img/defaultPic.png"
    with open(file, 'rb') as f:
        contents = f.read()
        
    data_uri = base64.b64encode(contents).decode('utf-8')
    img_tag = '<img class="img-40 img-radius" alt="User-Profile-Image"  src="data:image/png;base64,{0}">'.format(data_uri)
    return jsonify({'src': "data:image/png;base64,{0}".format(data_uri)})
''' 湘的 end '''
