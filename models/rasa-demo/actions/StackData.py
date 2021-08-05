#!/usr/bin/env python3
from stackapi import StackAPI
from urllib.parse import urlparse, unquote
from pathlib import PurePosixPath
from bs4 import BeautifulSoup
#import json

#存放stackoverflow的post資料
#包含取得資料的函式
class StackData:
    def __init__(self, question, answers):
        #取得問題id
        self.id = question['question_id']
        self.link = question['link']
        self.question, self.bestAnsID = self.__getQuestion(question)
        self.answers = self.__getAnswers(answers)
    
    #private method: 取得問題資訊
    def __getQuestion(self, q):
        result = {
            "id" : q['question_id'],
            "title" : q['title'],
            "content" : self.__addClass2Code(q['body']),
            "abstract" : self.__getPureText(q['body']),
            "view_count" : q['view_count'],
            "web_score" : q['score']
            }
        if 'accepted_answer_id' in q.keys():
            return result, q['accepted_answer_id']
        else:
            return result, ""
    
    #private method: 取得答案資訊, 最佳解&其他解
    def __getAnswers(self, answers):
        result = []
        for ans in answers:
            result.append({
                          "id" : ans['answer_id'],
                          "score" : ans['score'],
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


def parseStackData(url_list):
    site = StackAPI('stackoverflow')
    site.page_size = 10
    site.max_pages = 1
    ##prepare query id
    query_ids = []
    for url in url_list:
        try:
            url_id = PurePosixPath(urlparse(unquote(url)).path).parts[2]
            query_ids.append(url_id)
        except:
            continue
        if len(query_ids) > 5:
            break
    question = site.fetch('questions', filter='withbody', ids=query_ids)['items']
    answers = site.fetch('questions/{ids}/answers', filter='withbody', ids=query_ids, sort='votes', order='desc')['items']
    print(question[0])
    ctg_ans = {}
    for ans in answers:
        if ans['question_id'] in ctg_ans:
            ctg_ans[ans['question_id']].append(ans)
        else:
            ctg_ans[ans['question_id']] = [ans]
    stack_items = []
    for q in question:
        try:
            temp = StackData(q, ctg_ans[q['question_id']]).showData()
            stack_items.append(temp)
        except:
            continue
    return stack_items







