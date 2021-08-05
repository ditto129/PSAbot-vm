# This files contains your custom actions which can be used to run
# custom Python code.
#
# See this guide on how to implement these action:
# https://rasa.com/docs/rasa/custom-actions


# This is a simple example for a custom action which utters "Hello World!"

from typing import Any, Text, Dict, List

from rasa_sdk import Action, Tracker
from rasa_sdk.events import SlotSet
from rasa_sdk.executor import CollectingDispatcher
import random
import requests
import json
#加入文字分析模組&外部搜尋模組
from . import TextAnalyze
from .OuterSearch import outerSearch
##摘要
from . import StackData

#head_url='http://localhost:55001/api/'
head_url='https://soselab.asuscomm.com:55002/api/'

#將整句話(問題描述、錯誤訊息)填入slot
class fill_slot(Action):
    def name(self) -> Text:
        return "fill_slot"

    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        function = tracker.get_slot("function")
        os = tracker.get_slot("os")
        pl = tracker.get_slot("pl")
        
        if os!=None and pl!=None:
            if "錯誤訊息" in function:
                reply = "請貼上您的錯誤訊息"
            elif "引導式" in function:
                reply = "請描述您遇到的問題"
            else:
                reply = "你的function抓不到"
        elif os == None:
            reply = "請問您使用的是什麼作業系統？<br>若之後要修改，請輸入「我要更改作業系統」"
        else:
            reply = "請問您使用的是什麼程式語言？<br>若之後要修改，請輸入「我要更改程式語言」"
        
        dispatcher.utter_message(text=reply)
        return []

#分析並搜尋並記下使用者輸入及相關關鍵字（第一次搜尋）
class analyze_and_search(Action):
    def name(self) -> Text:
        return "analyze_and_search"
    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        print('in analyze_and_search')
        function = tracker.get_slot("function")
        os = tracker.get_slot("os")
        pl = tracker.get_slot("pl")
        if "錯誤訊息" in function:
            #拿到所需訊息及最後一句使用者輸入
            question_or_error_message = tracker.latest_message.get('text')
            question_or_error_message = question_or_error_message.split(',',1)[1]
            qkey = question_or_error_message.split(' ')
            qkey.append(os)
            qkey.append(pl)
            
            #外部搜尋結果（URL）
            resultpage = outerSearch(qkey, 10, 0)
            
#            stack_items = [StackData(url) for url in resultpage]
            result_title = []
            for i in resultpage:
#            for items in stack_items:
                #showData回傳的資料即是傳送到前端的json格式
#                display = items.showData()
#                result_title.append(display['question']['title'])
                result_title.append(i)
    
            reply = "謝謝您的等待，以下為搜尋結果的資料摘要："
            for i in range(0, len(resultpage)):
                reply += ("<br>" + str(i+1) + ".<a href=\"" + resultpage[i] + "\">"+ result_title[i] + "</a>")
            reply += "<br>點選摘要連結可顯示內容。<br><br>感謝回饋，歡迎下次光臨！"

            #reply += "<a href=\"#\" onclick=\"summary('all')\">點我查看所有答案排名</a>"
            dispatcher.utter_message(text=reply)
            return []
        elif "引導式" in function:
            #拿到所需訊息及最後一句使用者輸入
            question_or_error_message = tracker.latest_message.get('text')
            question_or_error_message = question_or_error_message.split(',',1)[1]
            print(question_or_error_message)
            
            #宣告文字分析器
            textAnalyzer = TextAnalyze.TextAnalyze()
            #擷取使用者問題的關鍵字
    #        qkey = ['flask']
            qkey = textAnalyzer.contentPreProcess(question_or_error_message)[0]
            #加上作業系統與程式語言作為關鍵字
            qkey.append(os)
            qkey.append(pl)
            resultpage = outerSearch(qkey, 10, 0)
            #內部搜尋
            response = requests.post(head_url+'query_inner_search', json={'keywords':qkey})
    #        print("內部搜尋的結果: ", response.text)
    
            # 慈 START
            postNumber = 1
            reply = "謝謝您的等待，以下為搜尋結果：<br>"
            
            objectAllPost = json.loads(response.text)
            for i in range(0, len(objectAllPost["inner_search_result"])):
                postId = objectAllPost["inner_search_result"][i]
                singlePostResponse = requests.post(head_url+'query_inner_post', json={'_id':postId})
                # 轉成object
                objectSinglePost = json.loads(singlePostResponse.text)
    #            print("單篇文章結果: ", objectSinglePost)
                reply += str(postNumber)
                reply += '. <a href="#" onclick="clickChatroomInnerSearch(\''
                reply += objectSinglePost["_id"]
                reply += '\')">'
                reply += objectSinglePost["title"]
                reply += '</a><br>'
                postNumber += 1
            
    #        print("reply的結果: "+reply);
            # 慈 END
            
            #外部搜尋結果（URL）
            resultpage = outerSearch(qkey, 10, 0)
            for url in resultpage:
                print(url)

            #外部搜尋
            #stackoverflow物件
            stack_items = StackData.parseStackData(resultpage)
#假資料～～～～～
            
            #with open("DATA_test.json", "r", encoding="utf-8") as f:
            #    stack_items = json.load(f)
            raw_data = [" ".join([item['question']['abstract'], " ".join([ans['abstract'] for ans in item['answers']])]) for item in stack_items ]
            #取得block排名
            result = TextAnalyze.blockRanking(stack_items, qkey)
#print(result)
            temp_data_id_list = requests.post(head_url + 'insert_cache', json={'data' : stack_items[0:5], 'type' : "temp_data"})
            block_rank_id = requests.post(head_url + 'insert_cache', json={'data': result, 'type' : "blocks_rank"})

            print(temp_data_id_list.text)
            print(block_rank_id.text)
            t_data_list = json.loads(temp_data_id_list.text)
            blocks = json.loads(block_rank_id.text)

            #每篇title
            result_title = [item['question']['title'] for item in stack_items]

            reply += "謝謝您的等待，以下為搜尋結果的資料摘要："
            for i in range(0, len(t_data_list)):
                reply += ("<br>" + str(i+1) + ".<a href=\"#\" onclick=\"summary('" + t_data_list[i] + "')\">" + result_title[i] + "</a>")
            reply += "<br>點選摘要連結可顯示內容。<br>"
            reply += "<a href=\"#\" onclick=\"rank('" + blocks[0] + "')\">點我查看所有答案排名</a>"
            reply += "<br><br>是否要繼續搜尋？"
            dispatcher.utter_message(text=reply)
            
    #        dispatcher.utter_message(text="是否繼續搜尋？")
            
            # 慈 START
    #        reply += "<br><br>是否繼續搜尋？"
#dispatcher.utter_message(text=reply)
            # 慈 END

            more_keywords = textAnalyzer.keywordExtraction(raw_data)
            qkey = qkey + more_keywords
            #！！！將關鍵字及更多關鍵字存入slot
            return [SlotSet("keywords", ','.join(qkey))]
            
            
            
#給user選關鍵字
class select_keyword(Action):
    def name(self) -> Text:
        return "select_keyword"
    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        #！！！拿到之前存的關鍵字
        print("給使用者選關鍵字了！")
        qkey = tracker.get_slot("keywords")
        print(qkey)
        qkey = qkey.split(',')
        
        #------------test------------#
        #textAnalyzer = TextAnalyze.TextAnalyze()
        #more_keywords = textAnalyzer.keywordExtraction(eval(raw_data))
        #----------------------------#
        
        reply = '新增/刪除用來搜尋的關鍵字<br><div id="keywords'
        #reply += keywordsTime
        reply += '">'
        id = 0
        for i in qkey:
            reply += '<label id="'
            reply += str(id)
            reply += '" class="badge badge-default purpleLabel">'
            reply += i
            reply += '<button class="labelXBtn" onclick="cancleKeyWords(\''
            reply += str(id)
            reply += '\')">x</button></label>'
            id += 1
        reply += '</div><br><input id="addBtn" class="btn btn-primary purpleBtnInChatroom" value="新增" onclick="wantAddKeyWord()"><input id="doneBtn"class="btn btn-primary purpleBtnInChatroom" value="完成" onclick="doneKeyWord()">'
        
        dispatcher.utter_message(text=reply)
        return []
        
        

#拿選好的關鍵字搜尋(繼續搜尋)
class outer_search(Action):
    def name(self) -> Text:
        return "outer_search"
    def run(self, dispatcher, tracker, domain) -> List[Dict[Text, Any]]:
        #拿到所需訊息及最後一句使用者輸入
        print("去外部搜尋了！")
        keywords = tracker.latest_message.get('text')
        keywords = keywords.split(',',1)[1]
        print(keywords)
        
        qkey = keywords.split(',')
        #外部搜尋結果（URL）
        resultpage = outerSearch(qkey, 10, 0)
        for url in resultpage:
            print(url)
        #外部搜尋
        #stackoverflow物件
        stack_items = StackData.parseStackData(resultpage)
        
        #假資料～～～～～
        #with open("DATA_test.json", "r", encoding="utf-8") as f:
        #    stack_items = json.load(f)
        
        raw_data = [ " ".join([item['question']['abstract'], " ".join([ans['abstract'] for ans in item['answers']])]) for item in stack_items ]
        #取得block排名
        result = TextAnalyze.blockRanking(stack_items, qkey)
        #print(result)
        temp_data_id_list = requests.post(head_url + 'insert_cache', json={'data' : stack_items[0:5], 'type' : "temp_data"})
        block_rank_id = requests.post(head_url + 'insert_cache', json={'data': result, 'type' : "blocks_rank"})
        print(temp_data_id_list.text)
        print(block_rank_id.text)
        t_data_list = json.loads(temp_data_id_list.text)
        blocks = json.loads(block_rank_id.text)
        
        #每篇title
        result_title = [item['question']['title'] for item in stack_items]
        
        reply += "謝謝您的等待，以下為搜尋結果的資料摘要："
        for i in range(0, len(t_data_list)):
            reply += ("<br>" + str(i+1) + ".<a href=\"#\" onclick=\"summary('" + t_data_list[i] + "')\">" + result_title[i] + "</a>")
        reply += "<br>點選摘要連結可顯示內容。<br>"
        reply += "<a href=\"#\" onclick=\"rank('" + blocks[0] + "')\">點我查看所有答案排名</a>"
        reply += "<br><br>是否要繼續搜尋？"
        dispatcher.utter_message(text=reply)
       
        return []
