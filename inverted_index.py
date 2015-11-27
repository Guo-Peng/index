# -*- coding: UTF-8 -*-
from get_article import get_conn
from functools import wraps
import jieba


def get_inverted(n, symbol, stop_words):
    inverted = {}
    #  获取文章
    chinese = True
    database = 'docs'
    if chinese:
        database += '_cn'
    articles = get_articles(n, database)
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


def get_articles(n, database):
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'SELECT id,path FROM ' + database + ' WHERE id<=%d' % n
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
    return [line.strip().decode('utf-8') for line in open('stop_words', 'r').readlines()]


def get_symbol():
    return [line.strip().decode('utf-8') for line in open('symbol', 'r').readlines()]


def decorator_inverted(n):
    def decorator(func):
        symbol = get_symbol()
        stop_words = get_stop_words()
        inverted = get_inverted(n, symbol, stop_words)

        @wraps(func)
        def wrapper(query):
            return func(query, symbol, stop_words, inverted)

        return wrapper

    return decorator


if __name__ == '__main__':
    s = '任天堂3DS游戏机'
    sy = get_symbol()
    print '//'.join(word_split(s, sy))
