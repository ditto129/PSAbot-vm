#!/usr/bin/env python3
import numpy as np
import spacy
from spacy.lang.en.stop_words import STOP_WORDS  ##停用詞
from spacy_langdetect import LanguageDetector
from collections import Counter
from heapq import nlargest
#from Translate import Translate
###LDA model
from gensim.corpora.dictionary import Dictionary
from gensim.models import LdaModel
from itertools import chain

#文字分析模組 - stackoverflow外部資料 & PQAbot系統內部資料
class TextAnalyze:
    
    STOPWORDS = list(STOP_WORDS)               ##停用詞: 可忽略的詞，沒有賦予上下文句意義的詞
    POS_TAG = ['PROPN', 'ADJ', 'NOUN', 'VERB'] ##欲留下的詞類
    
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
        nlp = spacy.load('en_core_web_sm')
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
        flitered_token = [ word for word in lemma if not nlp.vocab[word].is_stop ]
        
        return flitered_token, doc
    
    #取得文章摘要 - extractive summarization
    def textSummarization(self, text):
        ###Step 1.過濾必要token
        keyword, doc = self.contentPreProcess(text)##保留詞
        freq_word = Counter(keyword)               #計算關鍵詞的出現次數
        ###Step 2.正規化
        max_freq_word = Counter(keyword).most_common(1)[0][1]  #取得最常出現單詞次數
        for word in freq_word.keys():
            freq_word[word] = freq_word[word]/max_freq_word    #正規化處理
        ###Step 3.sentence加權
        sentence_w = {}
        for sen in doc.sents:
            for word in sen:
                if word.text in freq_word.keys():
                    if sen in sentence_w.keys():
                        sentence_w[sen] += freq_word[word.text]
                    else:
                        sentence_w[sen] = freq_word[word.text]
        ###Step 4.nlargest(句子數量, 可迭代之資料(句子&權重), 分別須滿足的條件)
        summarized_sen = nlargest(3, sentence_w, key=sentence_w.get)
        
        return summarized_sen
    
    
    #利用LDA topic modeling取出關鍵字
    def keywordExtraction(self, data_list):
        comp_preproc_list = [self.contentPreProcess(data)[0] for data in data_list]
        keywords = []
        lda_model, dictionary = self.LDATopicModeling(comp_preproc_list, 5)
        for i in range(0,5):
            keywords.append([w[0] for w in lda_model.show_topics(formatted=False, num_words=3)[i][1]])
        keywords = list(chain.from_iterable(keywords))
        keywords = list(dict.fromkeys(keywords))
        return keywords
    
    #LDA topic modeling
    ##data -> 2維陣列[[keywords], [keywords], [keywords], ...[]]
    ##topic_num = 欲分割成多少數量
    ##keyword_num = 取前n關鍵字
    def LDATopicModeling(self, data, topic_num):
        dictionary = Dictionary(data)
        corpus = [dictionary.doc2bow(text) for text in data]
        lda_model = LdaModel(corpus, num_topics=topic_num, id2word=dictionary, per_word_topics=True)
        return lda_model, dictionary
    
    #關聯度評分
    ##input(question kewords, pure word of posts' question)
    def similarityRanking(self, question_key, compare_list):
        nlp = spacy.load('en_core_web_lg')
        ### pre-process text
        comp_preproc_list = [ self.contentPreProcess(content)[0] for content in compare_list ]
        ##LDA topic modeling
        lda_model, dictionary = self.LDATopicModeling(comp_preproc_list, 5)
        
        ##topic prediction
        q_bow = dictionary.doc2bow(question_key)
        q_topics = sorted(lda_model.get_document_topics(q_bow), key=lambda x:x[1], reverse=True)
        
        ##choose top 3 prediction
        top3_topic_pred = [ q_topics[i][0] for i in range(3) ]            #top3 topic
        #print(top3_topic_pred)
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



def blockRanking(stack_items, qkey):
    analyzer = TextAnalyze()
    ans = [items['answers'] for items in stack_items]
    
    #data pre-process
    all_content = [[{"id" : sing_ans["id"], "content" : sing_ans['abstract']} for sing_ans in q_ans_list] for q_ans_list in ans ]
    all_content_flat = list(chain.from_iterable(all_content))
    raw = [t["content"] for t in all_content_flat]
    
    ##similarity ranking
    temp_result = analyzer.similarityRanking(qkey, raw)
    for i in range(len(all_content_flat)):
        all_content_flat[i]["score"] = temp_result[i]
    rank = sorted(all_content_flat, key=lambda data:data["score"], reverse=True)
    return rank
