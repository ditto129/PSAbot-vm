# --- flask --- #
from flask import Blueprint, request, jsonify
from datetime import datetime
#from flask_security import logout_user, login_required

# --- our models ---- #
from models import faq_data

faq_api = Blueprint('faq_api', __name__)

# 調整更新週期
@faq_api.route('/adjust_faq_update', methods=['POST'])
def adjust_faq_update():
    data = request.get_json()
    try:
        setting_dict = {
            'data_number':data['num'],
            'update_cycle':data['cycle']
        } 
        faq_data.adjust_update_cycle(setting_dict['data_number'],setting_dict['update_cycle'])
    except Exception as e :
        setting_dict = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print("錯誤訊息: ", e)
    return jsonify(setting_dict)

# 查看更新週期
@faq_api.route('/query_faq_update', methods=['POST'])
def query_faq_update():
    try:
        update_data = faq_data.query_update_cycle()
        update_data.pop('_id')
    except Exception as e :
        update_data = {"error" : e.__class__.__name__ + ":" +e.args[0]}
        print("錯誤訊息: ", e)
    return jsonify(update_data)

# 取得FAQ列表
@faq_api.route('/query_faq_list', methods=['POST'])
def query_faq_list():
    data = request.get_json()
    try: 
        list_dict = faq_data.query_list(data['page_size'],data['page_number'],data['option'])
        
    except Exception as e :
        list_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(list_dict)
# 依標籤取得FAQ列表
@faq_api.route('/query_faq_list_by_tag', methods=['POST'])
def query_faq_list_by_tag():
    data = request.get_json()
    try: 
        list_dict = faq_data.query_list_by_tag(data['tag'],data['page_size'],data['page_number'],data['option'])
        
    except Exception as e :
        list_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(list_dict)
# 依字串取得FAQ列表
@faq_api.route('/query_faq_list_by_string', methods=['POST'])
def query_faq_list_by_string():
    data = request.get_json()
    try: 
        list_dict = faq_data.query_list_by_string(data['search_string'],data['page_size'],data['page_number'],data['option'])
        
    except Exception as e :
        list_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(list_dict)
# 新增單篇FAQ
@faq_api.route('/insert_faq_post', methods=['POST'])
def insert_faq_post():
    data = request.get_json()
    try: 
        faq_dict = {
                        "_id" : "",          
                        "link" : data['link'],         
                        "question" : 
                        {
                            "_id" : "",       
                            "title" : data['question']['title'],    
                            "content": data['question']['content'],   
                            "vote" : data['question']['vote'],      
                            "score" : [],
                        },
                        "answers" : 
                        [
                            {       
                                "_id" : "",       
                                "content" : a['content'],
                                "vote" : a['vote'],     
                                "score" : [],
                            } for a in data['answers']
                        ],
                        "keywords" : [],     
                        "tags" : data['tags'],
                        "time" : datetime.fromisoformat(data['time']),
                        "view_count" : 0
        }
        faq_data.insert_faq(faq_dict,'inner_faq')
    except Exception as e :
        faq_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(faq_dict)
    
# 匯入FAQ
@faq_api.route('/import_faq_post', methods=['POST'])
def import_faq_post():
    data = request.get_json()
    try: 
        faq_list = [
            {
                        "_id" : "",          
                        "link" : faq['link'],         
                        "question" : 
                        {
                            "id" : "",       
                            "title" : faq['question']['title'],    
                            "content": faq['question']['content'],   
                            "vote" : faq['question']['vote'],      
                            "score" : [],
                        },
                        "answers" : 
                        [
                            {       
                                "id" : "",       
                                "content" : a['content'],
                                "vote" : a['vote'],     
                                "score" : [],
                            } for a in faq['answers']
                        ],
                        "keywords" : [],     
                        "tags" : faq['tags'],
                        "time" : datetime.fromisoformat(faq['time']),
                        "view_count" : 0
            } for faq in data['faq_list']
        ]
        faq_data.insert_faq(faq_list,'inner_faq')
    except Exception as e :
        faq_list = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(faq_list)

# 查看單篇FAQ
@faq_api.route('/query_faq_post', methods=['POST'])
def query_faq_post():
    data = request.get_json()
    try: 
        faq_dict = faq_data.query_faq_post(data['_id'])
    except Exception as e :
        faq_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(faq_dict)
# 對FAQ按讚
@faq_api.route('/like_faq_post', methods=['POST'])
def like_faq_post():
    data = request.get_json()
    try:
        score_dict = {
            'faq_id' : data['post_id'],
            'answer_id' : data['response_id'],
            'user':data['user'],
            'score' : 1,
        }
        faq_data.update_score(score_dict)
    except Exception as e :
        score_dict = {"error" : e.__class__.__name__ + ":" +e.args[0]}
    return jsonify(score_dict)
# 對FAQ按倒讚
@faq_api.route('/dislike_faq_post', methods=['POST'])
def dislike_faq_post():
    data = request.get_json()
    try:
        score_dict = {
            'faq_id' : data['post_id'],
            'answer_id' : data['response_id'],
            'user':data['user'],
            'score' : -1,
        }
        faq_data.update_score(score_dict)
    except Exception as e :
        score_dict = {"error" : e.__class__.__name__ + ":" +e.args[0]}
    return jsonify(score_dict)
# 新增answer
@faq_api.route('/insert_faq_answer', methods=['POST'])
def insert_faq_answer():
    data = request.get_json()
    try: 
        answer_dict = {
            'faq_id':data['faq_id'],
            'id':"",
            'content':data['content'],
            'vote':data['vote'],
            'score':[]
        }
        faq_data.insert_answer(answer_dict)
    except Exception as e :
        answer_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(answer_dict)
# 編輯單個answer
@faq_api.route('/update_faq_answer', methods=['POST'])
def update_faq_answer():
    data = request.get_json()
    try: 
        answer_dict = {
            'faq_id':data['faq_id'],
            'id':data['id'],
            'content':data['content'],
            'vote':data['vote'],
        }
        faq_data.insert_answer(answer_dict)
    except Exception as e :
        answer_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(answer_dict)
# 刪除單個answer
@faq_api.route('/delete_faq_answer', methods=['POST'])
def delete_faq_answer():
    data = request.get_json()
    try: 
        answer_dict = {
            'faq_id':data['faq_id'],
            'id':data['id']
        }
        faq_data.insert_answer(answer_dict)
    except Exception as e :
        answer_dict = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(answer_dict)
# 編輯單篇FAQ
@faq_api.route('/update_faq_post', methods=['POST'])
def update_faq_post():
    data = request.get_json()
    try: 
        data['time'] = datetime.fromisoformat(data['time'])
        faq_data.update_faq(data)
    except Exception as e :
        data = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(data)

# 刪除單篇FAQ
@faq_api.route('delete_faq_post', methods=['POST'])
def delete_faq_post():
    data = request.get_json()
    try: 
        faq_data.remove_faq(data['_id'])
    except Exception as e :
        data = {"error" : e.__class__.__name__ + " : " +e.args[0]}
    return jsonify(data)