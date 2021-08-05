#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Wed Apr 28 16:29:09 2021

@author: shauangel
"""
from stackapi import StackAPI
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from bs4 import BeautifulSoup
import json

#存放stackoverflow的post資料
#包含取得資料的函式
class StackData:
    def __init__(self, url):
        #取得問題id
        self.id = PurePosixPath(urlparse(unquote(url)).path).parts[2]
        self.link = url
        #設定stackAPI工具
        self.site = StackAPI('stackoverflow')
        self.site.page_size = 10
        self.site.max_pages = 1
        self.question, self.bestAnsID = self.__getQuestion()
        self.answers = self.__getAnswers(self.id)
    
    #private method: 取得問題資訊
    def __getQuestion(self):
        
        data = self.site.fetch('questions', filter='withbody', ids=[self.id])['items'][0]
        result = {
                "id" : self.id,
                "title" : data['title'], 
                "content" : self.__addClass2Code(data['body']), 
                "abstract" : self.__getPureText(data['body']),
                }
        if 'accepted_answer_id' in data.keys():
            return result, data['accepted_answer_id']
        else:
            return result, ""
    
    #private method: 取得答案資訊, 最佳解&其他解
    def __getAnswers(self, ids):
        data = self.site.fetch('questions/{ids}/answers', filter='withbody', ids=[ids], sort='votes', order='desc')['items']
        result = []
        for ans in data:
            result.append({
                    "id" : ans['answer_id'],
                    "score" : ans['score'],
                    "vote": 0,
                    "content" : self.__addClass2Code(ans['body']),
                    "abstract" : self.__getPureText(ans['body']),
                    })
        return result
    
    def __getPureText(self, html):
        #get sentences without html tag & code
        soup = BeautifulSoup(html, 'html.parser')
        abstract = [i.text for i in soup.findAll('p')]
        result = " ".join(abstract)
        return result
    
    def __addClass2Code(self, html):
        soup = BeautifulSoup(html, 'html.parser')
        pre = soup.findAll('pre')
        for p in pre:
            code = p.find('code')
            try:
                code['class'] = code.get('class', []) + ['python']
                p.replaceWith(p)
            except:
                continue
            
        return str(soup)
    
    def showData(self):
        display = {
                "link" : self.link,
                "question" : self.question,
                "answers" : self.answers
                }
        return display
    
    def insertDB(self):
        return
    
    
    
    
if __name__ == "__main__":
    url_list = ["https://stackoverflow.com/questions/46349370/javascript-file-not-found-using-relative-path-during-flask-render-template",
                "https://stackoverflow.com/questions/31002890/how-to-reference-a-html-template-from-a-different-directory-in-python-flask/31003097",
                "https://stackoverflow.com/questions/21765692/flask-render-template-with-path/48040453",
                "https://stackoverflow.com/questions/42005613/cant-find-flask-template-specified-by-relative-path",
                "https://stackoverflow.com/questions/23846927/flask-unable-to-find-templates"]
    test = [StackData(url) for url in url_list]
    d = [s.showData() for s in test]
        
    with open('DATA_test.json', 'w', encoding='utf-8') as f:
        json.dump(d, f)
    
    
    
    
