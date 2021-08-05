''' =========== FAQ_DATA_COLLECTION =========== *
- 新增資料 : insert_資料名稱
- 取得資料 : query_資料名稱
- 刪除資料 : remove_資料名稱
- 資料名稱統一，以底線分隔
- 使用collection : _db.FAQ_DATA_COLLECTION
* ========================================'''

from . import _db
import re
from datetime import datetime
# 調整更新週期
def adjust_update_cycle(data_number,update_cycle):
    _db.FAQ_DATA_COLLECTION.update_one({'_id':'faq_settings'},{'$set':{'data_number':data_number,'update_cycle':update_cycle}})

# 取得更新週期
def query_update_cycle():
    return _db.FAQ_DATA_COLLECTION.find_one({'_id':'faq_settings'})

# 取得FAQ列表
def query_list(page_size,page_number,option):
    faq_count = [i for i in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1},
                                                               {'$count': 'faq_count'}])][0]['faq_count']
    if option == '': # 預設是用時間排
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1},
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords': 1,'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1}}, 
                                                                       {'$sort': {'time': -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    else : 
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1},
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords': 1,'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1}}, 
                                                                       {'$sort': {option: -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    return {'faq_count' : faq_count,'faq_list' : faq_list}
# 依標籤取得FAQ列表
def query_list_by_tag(tag_list,page_size,page_number,option):
    faq_count = len([i for i in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1},
                                                                   {'$project': {'hastag': {'$setIsSubset': [tag_list, '$tags']}}}, 
                                                                   {'$match': {'hastag': True}}])])
    if option == '': # 預設是用時間排
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1}, 
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords':1, 'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1, 'hastag': {'$setIsSubset': [tag_list, '$tags']}}}, 
                                                                       {'$match': {'hastag': True}},
                                                                       {'$sort': {'time': -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    else : 
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1}, 
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords':1, 'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1, 'hastag': {'$setIsSubset': [tag_list, '$tags']}}}, 
                                                                       {'$match': {'hastag': True}},
                                                                       {'$sort': {option : -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    return {'faq_count' : faq_count,'faq_list' : faq_list}
# 依字串取得FAQ列表
def query_list_by_string(search_string,page_size,page_number,option):
    # 用空白切割字串
    search_list = re.split(r'[ ]', search_string)       
    # 標題搜尋                                        
    regex_list = [{'question.title':{'$regex':'|'.join(search_list), '$options':'i'}}]
    # 關鍵字,tag搜尋
    for token in search_list:                                                                   
        regex_list.append({'keywords':{'$regex':token, '$options':'i'}})
        regex_list.append({'tags.tag_name':{'$regex':token, '$options':'i'}})
    faq_count = len([ i for i in _db.FAQ_DATA_COLLECTION.aggregate([{'$match': {'$or': regex_list}}])])
    if option == '': 
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1}, 
                                                                       {'$match': {'$or': regex_list}},
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords':1, 'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1}}, 
                                                                       {'$sort': {'time': -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    else :
        faq_list = [ doc for doc in _db.FAQ_DATA_COLLECTION.aggregate([{'$skip': 1}, 
                                                                       {'$match': {'$or': regex_list}},
                                                                       {'$project': {'_id': 1, 'question.title': 1, 'time': 1, 'keywords':1, 'tags': 1, 'score': {'$sum': '$score.score'}, 'view_count': 1}}, 
                                                                       {'$sort': {option: -1}}, 
                                                                       {'$skip': page_size * (page_number - 1)}, 
                                                                       {'$limit': page_size}])]
    return {'faq_count' : faq_count,'faq_list' : faq_list} 
# 新增單篇FAQ
def insert_faq(data_dict,data_type):
    all_faq = _db.FAQ_DATA_COLLECTION.find().skip(1)
    if all_faq.count() == 0:
        data_dict['_id'] = '000001'
    else:
        # sort _id,將最大的+1當作新的_id
        biggest_id = int(all_faq.skip(1).sort('_id',-1).limit(1)[0]['_id'])
        data_dict['_id'] = str(biggest_id + 1).zfill(6)
    # 文字分析模組
    data_dict['keywords'] = []
    # 管理員新增faq處理answer_id和資料庫tag
    if data_type == 'inner_faq':
        answer_id = 0
        for ans in data_dict['answers']:
            ans['id'] = str(answer_id + 1).zfill(6)
            answer_id += 1
        # 如果有tag，更新tag的紀錄
        if len(data_dict['tags']) != 0:
            for tag in data_dict['tags']:
                _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$set':{'recent_use':data_dict['time']},
                                                                     '$inc':{'usage_counter':1}})
    # FAQ加入資料庫
    _db.FAQ_DATA_COLLECTION.insert_one(data_dict)
# 匯入FAQ
def import_faq(data_list,data_type):
    all_faq = _db.FAQ_DATA_COLLECTION.find().skip(1)
    if all_faq.count() == 0:
        current_id = '000000'
    else:
        # sort _id,將最大的+1當作新的_id
        biggest_id = int(all_faq.skip(1).sort('_id',-1).limit(1)[0]['_id'])
        current_id = str(biggest_id + 1).zfill(6)
    for data_dict in data_list:  
        data_dict['_id'] = str(int(current_id) + 1).zfill(6)
        # 文字分析模組
        data_dict['keywords'] = []
        # 處理內部內部貼文 answer_id,tag
        if data_type == 'inner_faq':
            answer_id = 0
            for ans in data_dict['answers']:
                ans['id'] = str(answer_id + 1).zfill(6)
                answer_id += 1
            # 如果有tag，更新tag的紀錄
            if len(data_dict['tags']) != 0:
                for tag in data_dict['tags']:
                    _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$set':{'recent_use':data_dict['time']},
                                                                         '$inc':{'usage_counter':1}})
    # 加入多筆資料
    _db.FAQ_DATA_COLLECTION.insert_many(data_list)
    
def insert_answer(data_dict):
    faq_id = data_dict.pop('faq_id')
    target_faq = _db.FAQ_DATA_COLLECTION.find_one({'_id':faq_id})
    if len(target_faq['answers']) == 0:
        data_dict['id'] = '000001'
    else:
        biggest_id = int(sorted(target_faq['answers'], key = lambda k: k['id'],reverse=True)[0]['id'])
        data_dict['id'] = str(biggest_id + 1).zfill(6)
    _db.FAQ_DATA_COLLECTION.update({'_id':faq_id},{'$push':{'answers':data_dict}})
    # 更新tag count
    for tag in target_faq['tags']:
        _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$inc':{'usage_counter':1}})

def update_answer(data_dict):
    _db.FAQ_DATA_COLLECTION.update({'_id':data_dict['faq_id'],'answers.id':data_dict['id']},
                                   {'$set':{'answers.$.content':data_dict['content'],'answers.$.vote':data_dict['vote']}})

def remove_answer(data_dict):
    tags = _db.FAQ_DATA_COLLECTION.find_one({'_id':data_dict['faq_id']})
    _db.FAQ_COLLECTION.update_one({'_id':data_dict['faq_id']},
                                  {'$pull':{'answers':{'id':data_dict['id']}}})
    # 扣掉tag count
    for tag in tags:
        _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$inc':{'usage_counter': -1}})
    
# 查看單篇FAQ
def query_faq_post(faq_id):
    return _db.FAQ_DATA_COLLECTION.find_one(faq_id)

# 將爬蟲資料轉成FAQ格式
def transform_faq(faq_list):
    transformed_list = [
        {
            "_id" : "",          
            "link" : faq['link'],         
            "question" : 
            {
                "id" : faq['question']['id'],       
                "title" : faq['question']['title'],    
                "content" : faq['question']['content'],   
                "vote" : faq['question']['vote'],      
                "score" : []
            },
            "answers" : 
            [
                {       
                    "_id" : ans['id'],       
                    "content" : ans['content'],
                    "vote" : ans['vote'],     
                    "score" : [],
                } for ans in faq['answers']
            ],
            "keywords" : faq['kewords'],     
            "tags" : [],
            "time" : datetime.now().replace(microsecond=0).isoformat(),
            "view_count" : 0
        } for faq in faq_list
    ]
    import_faq(transformed_list,'outer_faq')

# 編輯貼文評分
def update_score(score_dict):
    target_faq = _db.FAQ_DATA_COLLECTION.find_one({'_id':score_dict['faq_id']})
    new_score_record = {
                'user_id': score_dict['user'],
                'score' : score_dict['score']
    }
    # response_id為空表示更新貼文評分
    if len(score_dict['answer_id']) == 0 :
        # 若使用者按過讚/倒讚，使用set
        if any(s['user_id'] == score_dict['user'] for s in target_faq['score']):
            _db.FAQ_DATA_COLLECTION.update_one({'_id':score_dict['faq_id'],'question.score.user_id': score_dict['user']},{'$set':{'question.score.$':new_score_record}})
        else:
            # FAQ本身push一個使用者評分
            _db.FAQ_DATA_COLLECTION.update_one({'_id':score_dict['faq_id']},{'$push':{'question.score':new_score_record}})
    # response_id不為空表示更新回覆評分
    else :
        target_answer = next(answer for answer in target_faq['answers'] if answer['_id'] == score_dict['answer_id'])
        # 若使用者按過讚/倒讚，使用set
        if any(s['user_id'] == score_dict['user'] for s in target_answer['score']):
            _db.FAQ_DATA_COLLECTION.update_one({'_id':score_dict['faq_id'],
                                                'answers.id':score_dict['answer_id'],
                                                'answers.score.user_id':score_dict['user']},
                                               {'$set':{'answers.$.score':new_score_record}})
        # 否則直接push一個評分
        else:
             _db.FAQ_DATA_COLLECTION.update_one({'_id':score_dict['faq_id'],
                                                'answers.id':score_dict['answer_id']},
                                               {'$push':{'answers.$.score':new_score_record}})
# 更新FAQ內容
def update_faq(data_dict):
    target_faq = _db.FAQ_DATA_COLLECTION.find_one({'_id':data_dict['_id']})
    if data_dict['question']['content'] != target_faq['question']['content']:
        target_faq['question']['content'] = data_dict['question']['content']
        # ------------------ 接文字分析模組 ----------------------- #
        target_faq['keywords'] = [] 
    target_faq['link'] = data_dict['link']
    target_faq['question']['title'] = data_dict['question']['title']
    target_faq['question']['vote'] = data_dict['question']['vote']
    target_faq['time'] = data_dict['time']
    # 更新tags，扣除舊tag計數
    target_faq['tags'] = data_dict['tags']
    for tag in target_faq['tags']:
         _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$inc':{'usage_counter':-1}})
    for tag in data_dict['tags']:
        _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$set':{'recent_use':data_dict['time']},
                                                             '$inc':{'usage_counter':1}})
    #更新資料庫FAQ
    _db.FAQ_DATA_COLLECTION.update_one({'_id':target_faq['_id']},{'$set':target_faq})

# 刪除FAQ
def remove_faq(faq_id):
    target_faq = _db.FAQ_DATA_COLLECTION.find_one({'_id':faq_id})
    # 移除tag計數
    for tag in target_faq['tags']:
         _db.TAG_COLLECTION.update_one({'_id':tag['tag_id']},{'$inc':{'usage_counter':-1}})
    _db.FAQ_DATA_COLLECTION.delete_one({'_id':faq_id})