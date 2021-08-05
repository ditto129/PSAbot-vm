#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Apr 26 19:07:59 2021

@author: shauangel
"""
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS  ##停用詞
from spacy_langdetect import LanguageDetector
from collections import Counter
from heapq import nlargest
from Translate import Translate
###LDA model
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel

#文字分析模組 - stackoverflow外部資料 & PQAbot系統內部資料
class TextAnalyze:
    
    STOPWORDS = list(STOP_WORDS)               ##停用詞: 可忽略的詞，沒有賦予上下文句意義的詞
    POS_TAG = ['PROPN', 'ADJ', 'NOUN', 'VERB'] ##欲留下的詞類
    
    #_type: inner data or outer data
    def __init__(self):
        return
        
    #語言辨識
    def checkLanguage(self, text):
        nlp = spacy.load('en_core_web_sm')
        nlp.add_pipe(LanguageDetector(), name='language_detector', last=True)
        doc = nlp(text)
        print(doc._.language)
        return
    
    #文本前置處理
    def contentPreProcess(self, text):
        #translator = Translate(text)
        #en_text = translator.getTranslate()
        
        #keyword = []
        nlp = spacy.load('en_core_web_sm')
        #nlp.tokenizer = WhitespaceTokenizer(nlp.vocab)
        ###Step 1. lowercase & tokenizing
        doc = nlp(text.lower())
        ###Step 2. reduce punctuation
        pure_word = [ token for token in doc if not token.is_punct and token.text != '\n' ]
        ###Step 3. pos_tag filter & lemmatization
        lemma = []
        for token in pure_word:
            if token.pos_ in self.POS_TAG:
                if token.lemma_  == "-PRON-":
                    lemma.append(token.text)
                else:
                    lemma.append(token.lemma_)
        lemma = list(dict.fromkeys(lemma))    #reduce duplicate words
        
        ###Step 4. reduce stopwords & puncuation
        fliter_stop = [ word for word in lemma if not nlp.vocab[word].is_stop ]
        print(fliter_stop)
        
        #return keyword, doc
        return fliter_stop, doc
    
    #取得文章摘要 - extractive summarization
    def textSummarization(self, text):
        ###Step 2.過濾必要token
        keyword, doc = self.contentPreProcess(text)##保留詞
        freq_word = Counter(keyword)               #計算關鍵詞的出現次數
        ###Step 3.正規化
        max_freq_word = Counter(keyword).most_common(1)[0][1]  #取得最常出現單詞次數
        for word in freq_word.keys():
            freq_word[word] = freq_word[word]/max_freq_word    #正規化處理
        ###Step 4.sentence加權
        sentence_w = {}
        for sen in doc.sents:
            for word in sen:
                if word.text in freq_word.keys():
                    if sen in sentence_w.keys():
                        sentence_w[sen] += freq_word[word.text]
                    else:
                        sentence_w[sen] = freq_word[word.text]
        ###Step 5.nlargest(句子數量, 可迭代之資料(句子&權重), 分別須滿足的條件)
        summarized_sen = nlargest(3, sentence_w, key=sentence_w.get)
        
        return summarized_sen
        
    
        #利用LDA topic modeling取出關鍵字
    def keywordExtraction():
        
        return 0
    
    #LDA topic modeling
    ##data -> 2維陣列[[keywords], [keywords], [keywords], ...[]]
    ##topic_num = 欲分割成多少數量
    ##keyword_num = 取前n關鍵字
    def LDATopicModeling(data, topic_num, keyword_num):
        dictionary = Dictionary(data)
        corpus = [dictionary.doc2bow(text) for text in data]
        lda_model = LdaModel(corpus, num_topics=7, id2word=dictionary)
        return 0
    
    #關聯度評分
    ##input(question kewords, pure word of posts' question)
    def similarityRanking(self, question_key, compare_list):
        nlp = spacy.load('en_core_web_lg')
        ### pre-process text
        comp_preproc_list = [ self.contentPreProcess(content)[0] for content in compare_list ]
        ##LDA topic modeling
        dictionary = Dictionary(comp_preproc_list)
        corpus = [dictionary.doc2bow(text) for text in comp_preproc_list]
        lda_model = LdaModel(corpus, num_topics=7, id2word=dictionary)
        
        ##topic prediction
        q_bow = dictionary.doc2bow(question_key)
        q_topics = sorted(lda_model.get_document_topics(q_bow), key=lambda x:x[1], reverse=True)
        
        ##choose top 3 prediction
        top3_topic_pred = [ q_topics[i][0] for i in range(3) ]            #top3 topic
        print(top3_topic_pred)
        top3_prob = [q_topics[i][1] for i in range(3)]                    #top3 topic prediction probability
        print(top3_prob)
        top3_topic_keywords = [" ".join([w[0] for w in lda_model.show_topics(formatted=False, num_words=5)[pred_t][1]]) for pred_t in top3_topic_pred ]
        print(top3_topic_keywords)
        q_vec_list = [nlp(keywords) for keywords in top3_topic_keywords]
        top3pred_sim = [[q_vec.similarity(nlp(" ".join(comp))) for comp in comp_preproc_list] for q_vec in q_vec_list]
        top3pred_sim = np.array(top3pred_sim)
        print(np.array([ top3pred_sim[i] * top3_prob[i] for i in range(3) ]))
        score_result = np.sum(np.array([ top3pred_sim[i] * top3_prob[i] for i in range(3) ]), axis=0)
        return score_result
                              

     
if __name__ == "__main__": 
    """
    q = "flask render_template with relative path"
    analyzer = TextAnalyze()
    k_list, k_doc = analyzer.keywordExtration(q)
    print(k_list)
    result = analyzer.similarityRanking(k_list, ["test test hi hello check checking run ran runner"])
    print(result)
    """
    c1 = "You can do if you want to return a JSON data in the response along with the error code. You can read about responses here and here for make_response API details"
    c2 = "You have a variety of options: The most basic: If you want to access the headers, you can grab the response object: Or you can make it more explicit, and not just return a number, but return a status code object You can read more about the first two here: About Responses (Flask quickstart) And the third here: Status codes (Flask API Guide)"
    c3 = " As lacks suggested send status code in return statement and if you are storing it in some variable like  and using than time make sure its type is int not str. as I faced this small issue also here is list of status code followed globally http://www.w3.org/Protocols/HTTP/HTRESP.html Hope it helps."
    content = "Flask-Restful provides an abort function, it's can raise an HTTPException with special HTTP code and message back to the client. So, you can try to change the code like below: then, the client will receive 403 and a valid JSON string like below: The last, the client should deal with the error message properly."
    
    analyzer = TextAnalyze()
    k_list, k_doc = analyzer.keywordExtration(c3)
    print(k_list)
    
        
"""
q_bow = dictionary.doc2bow(question_key)
q_topic = sorted(lda_model.get_document_topics(q_bow), key=lambda x:x[1], reverse=True)[0][0]
q_topic_keywords = " ".join([w[0] for w in lda_model.show_topics(formatted=False, num_words=5)[q_topic][1]])
q_vec = nlp(q_topic_keywords)
score_result = [q_vec.similarity(nlp(" ".join(comp))) for comp in comp_preproc_list]
return score_result
"""
    
