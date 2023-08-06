import jieba as jb
import jieba.posseg as pseg
import wordcloud
import mml_qae.MoreErrors as me
import pandas as pd
import numpy as np
def add(words:list,tag:list=[]):
    """将特定词语单独隔开,无返回值"""
    if tag==[]:
        for _ in words:
            tag.append("n")
    elif len(tag) != len(words):
        raise me.DataError6      
    for word in words:
        jb.add_word(word,tag[words.index(word)])
def make_words_list(text):
    """将给入的文本拆分成数个单词并返回列表形式"""
    words=jb.cut(text,cut_all=False) 
    list_of_words=list(words)
    return list_of_words
def make_words_list_with_tags(text:str):
    """将给入的文本拆分成数个单词并返回列表形式,包含每个词的词性;返回格式为两个列表,分别包含分词和对应的词性"""
    words=pseg.cut(text)
    list_of_words=list_of_tags=[]
    for word,tag in words:
        list_of_words.append(word)
        list_of_tags.append(tag)
    return list_of_words,list_of_tags 
def make_words_list_with_extra_words(text:str,path1:str,path2):
    '''使用此方法必须从Git上下载jiebapos.xlsx和data3-1.txt,网址为https://github.com/ZYpS-leader/mml-qae ;将它们在本机上的绝对路径传入,应当以".../jiebapos.xlsx"和".../data3-1.txt"结尾.'''
    words=[]
    year=2021
    year_words=[]
    year_words.extend(pseg.cut(text))
    for j in range(len(year_words)):
        i=list(year_words[j])
        i.append(year)
        words.append(i)
    sjk=pd.DataFrame(words,columns=["word","词性","year"])
    jpbs=pd.read_excel(path1,header=0)
    words_renamed=sjk.join(jpbs.set_index("词性英文名称"),on="词性") 
    stopwords=open(path2,encoding="utf-8").read().replace(" ","")
    Stopped_words=stopwords.split("\n")
    df_words=words_renamed[words_renamed.apply(lambda x:x.loc["word"] not in Stopped_words,axis=1)]
    return sjk,words_renamed,df_words