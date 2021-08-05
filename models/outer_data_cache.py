''' ====== OUTER_DATA_CACHE_COLLECTION ====== *
- 新增資料 : insert_資料名稱
- 取得資料 : query_資料名稱
- 刪除資料 : remove_資料名稱
- 資料名稱統一，以底線分隔
- 使用collection : _db.OUTER_DATA_CACHE_COLLECTION
* ========================================'''
''' ====== ID DEFINITION ====== *
- c_ : 常用outerdata
- t_ : 暫存outerdata
- b_ : block排行
* =============================='''

from . import _db
#import _db
from datetime import datetime
##for test
import json
import copy

cache_format = {
        "_id" : "",
        "link" : "",
        "question" : { "id" : "",
                      "title" : "",
                      "content" : "",
                      "abstract" : "",
                      "score" : {},
                      "vote" : 0},
        "answers" : [],
        "keywords" : [],
        "tags" : [],
        "time" : "",
        "view_count" : 0
        }

#利用自訂id查詢資料
def query_by_id(idx):
    query = {"_id" : idx }
    return _db.OUTER_DATA_CACHE_COLLECTION.find(query)
    

#找最大id
def get_biggest_id():
    ids = _db.OUTER_DATA_CACHE_COLLECTION.find({},{'_id':1})
    id_list = [ int(i['_id'].split("_")[1]) for i in ids ]
    id_list.sort(reverse=True)
    return id_list[0]

#新增快取資料
def insert_cache(data_list, data_type):
    all_cache = _db.OUTER_DATA_CACHE_COLLECTION.find().skip(1)
    if all_cache.count() == 0:
        current_id = '000000'
    else:
        # sort _id,將最大的+1當作新的_id
        biggest_id = get_biggest_id()
        current_id = str(biggest_id).zfill(6)
    id_list = []
    if data_type == "blocks_rank":
        cache_data = transform_block_rank(data_list)
        cache_data['_id'] = "b_" + str(int(current_id) + 1).zfill(6)
        _db.OUTER_DATA_CACHE_COLLECTION.insert_one(cache_data)
        id_list.append(cache_data['_id'])
        
    else:    
        for data_dict in data_list:
            current_id = str(int(current_id) + 1)
            if data_type == "common_data":
                data_dict['_id'] = "c_" + current_id.zfill(6)
            elif data_type == "temp_data":
                data_dict['_id'] = "t_" + current_id.zfill(6)
                transform_temp_data(data_dict)
                
                
            id_list.append(data_dict['_id'])
        _db.OUTER_DATA_CACHE_COLLECTION.insert_many(data_list)
    return id_list

#block ranking 儲存格式
def transform_block_rank(data_list):
    blocks = [{
        "_id" : block['id'],
        "content" : block['content'],
        "vote" : 0,
        "score" : block['score']
        } for block in data_list]
    
    formal_form = copy.deepcopy(cache_format)
    formal_form['answers'] = blocks
    formal_form['time'] = datetime.now().replace(microsecond=0).isoformat()
    
    return formal_form

#暫存資料格式轉換
def transform_temp_data(data_dict):
    data_dict['keywords'] = []
    data_dict['tags'] = []
    data_dict['time'] = datetime.now().replace(microsecond=0).isoformat()
    data_dict['view_count'] = 0
    data_dict['question']['score'] = { "user_id" : "", "user_vote" : 0 }
    data_dict['question']['vote'] = 0
    for a in data_dict['answers']:
        a['score'] = { "user_id" : "", "user_vote" : 0 }
        a['vote'] = 0
        

def remove_all():
    _db.OUTER_DATA_CACHE_COLLECTION.delete_many({})


if __name__ == "__main__":
    filepath_A = "/Users/shauangel/Desktop/PSAbot專題/python/BLOCK_test.json"
    filepath_B = "/Users/shauangel/Desktop/PSAbot專題/python/DATA_test.json"
    with open(filepath_A, "r", encoding="utf-8") as f:
        data = json.load(f)
    
    #remove_all()
    #print(get_biggest_id())
    
    result = insert_cache(data, "blocks_rank")
    #result = insert_cache(data, "temp_data")
    print(result)
    #result = query_by_id(['t_000001', 't_000002', 't_000003', 't_000004', 't_000005'])
    #['b_000006']
    #for r in result:
    #    print(r['link'])
    #    print("------")
    












