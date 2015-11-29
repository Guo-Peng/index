# -*- coding: UTF-8 -*-
import jieba
import os


def get_inverted(symbol, stop_words):
    inverted = {}
    articles = get_articles()
    for doc_id, path in articles:
        word_index = get_word_index(get_doc(path), symbol, stop_words)
        word_list = get_word_list(word_index)
        inverted_add(inverted, doc_id, word_list)
    return inverted


def inverted_add(inverted, doc_id, word_list):
    for word, index_list in word_list.items():
        word_dic = inverted.setdefault(word, {})
        word_dic[doc_id] = index_list


def get_word_list(word_index):
    word_list = {}
    for word, index in word_index:
        index_list = word_list.setdefault(word, [])
        index_list.append(index)
    return word_list


def get_word_index(content, symbol, stop_words):
    words = word_split(content, symbol)
    return [(word, index + 1) for index, word in enumerate(words) if word not in stop_words]


def word_split(content, symbol):
    return [word.lower() for word in jieba.cut(content) if word not in symbol
            if word not in [u'', u' ', u'\t', u'\n']]


def get_articles():
    path = '/Users/Peterkwok/Documents/docs_cn/'
    doc_names = os.listdir(path)[1:]
    return [(index, path + name) for index, name in enumerate(doc_names)]


def get_header_by_id(id_list):
    if id_list:
        doc_names = os.listdir('/Users/Peterkwok/Documents/docs_cn/')[1:]
        return [doc_names[doc_id] for doc_id in id_list]
    else:
        return []


def get_doc(path):
    return open(path, 'r').read()


def get_stop_words():
    return [line.strip().decode('utf-8') for line in open('stop_words', 'r').readlines()]


def get_symbol():
    return [line.strip().decode('utf-8') for line in open('symbol', 'r').readlines()]

# def decorator(func):
#     symbol = get_symbol()
#     stop_words = get_stop_words()
#     inverted = get_inverted(symbol, stop_words)
#
#     @wraps(func)
#     def wrapper(query):
#         return func(query, symbol, stop_words, inverted)
#
#     return wrapper
