# -*- coding: UTF-8 -*-
import re
from get_article import get_conn
from functools import wraps


def get_inverted(n, stop_words):
    inverted = {}
    articles = get_articles(n)
    for doc_id, path in articles:
        word_index = get_word_index(get_doc(path), stop_words)
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


def get_word_index(content, stop_words):
    words = re.split(r'\W+', content.strip())
    if '' in words:
        words.remove('')
    return [(word.lower(), index + 1) for index, word in enumerate(words) if word not in stop_words]


def get_articles(n):
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'SELECT id,path FROM docs WHERE id<=%d' % n
    try:
        cursor.execute(sql)
        conn.commit()
        result = cursor.fetchall()
        return [(int(doc_id), path) for doc_id, path in result]
    except Exception, e:
        print e
        conn.rollback()
    finally:
        cursor.close()
        conn.close()


def get_doc(path):
    return open(path, 'r').read()


def get_stop_words():
    return [line.strip() for line in open('stop_words', 'r').readlines()]


def decorator_inverted(n):
    def decorator(func):
        stop_words = get_stop_words()
        inverted = get_inverted(n, stop_words)

        @wraps(func)
        def wrapper(query):
            return func(query, stop_words, inverted)

        return wrapper

    return decorator
