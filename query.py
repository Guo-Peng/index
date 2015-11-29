# -*- coding: UTF-8 -*-
from inverted_index import word_split, get_header_by_id, get_symbol, get_stop_words, get_inverted
from numpy import array
import re

symbol = get_symbol()
stop_words = get_stop_words()
inverted = get_inverted(symbol, stop_words)


def multi_word_query(query):
    query = word_split(query, symbol)
    words = [word for word in query if word not in stop_words]
    if words:
        docs = [set(inverted[word].keys()) for word in words]
        result_id = reduce(lambda x, y: x & y, docs) if docs else []
        return list(result_id)
    else:
        return []


def phrase_query(query):
    multi_query_id = list(multi_word_query(query))
    if multi_query_id:
        # 无内层list 无需进行深拷贝
        doc_ids = multi_query_id[:]
        words, distance = get_distance(query)
        if len(words) <= 1:
            return []
        for doc_id in multi_query_id:
            doc_index = [inverted[word][doc_id] for word in words]
            predict_dis = array(doc_index[0]) + distance[0]
            for x in xrange(1, len(doc_index)):
                index = is_contain(predict_dis, doc_index[x])
                if not index:
                    doc_ids.remove(doc_id)
                    break
                if x is len(doc_index) - 1:
                    break
                predict_dis = array(index) + distance[x]
    return doc_ids


def close_query(query):
    words, distance = get_distance(query, True)
    if len(words) <= 1:
        return []
    multi_query_id = list(multi_word_query(' '.join(words)))
    if multi_query_id:
        doc_ids = multi_query_id[:]
        for doc_id in multi_query_id:
            doc_index = [inverted[word][doc_id] for word in words]
            predict_dis = set()
            for num in doc_index[0]:
                predict_dis |= set(num + y for y in xrange(1, distance[0] + 1))
            for x in xrange(1, len(doc_index)):
                index = is_contain(list(predict_dis), doc_index[x])
                if not index:
                    doc_ids.remove(doc_id)
                    break
                if x is len(doc_index) - 1:
                    break
                predict_dis = set()
                for num in index:
                    predict_dis |= set(num + y for y in xrange(1, distance[0] + 1))
    return doc_ids


def get_distance(query, is_close=False):
    split_words = word_split(query, symbol)
    valid_distance = []
    if not is_close:
        words = split_words
        distance = [1] * (len(words) - 1)
    else:
        words = split_words[::2]
        distance = map(int, split_words[1::2])
    valid_index = [index for index, word in enumerate(words) if word not in stop_words]
    for x in xrange(len(valid_index) - 1):
        valid_distance.append(sum(distance[valid_index[x]:valid_index[x + 1]]))
    return [words[index] for index in valid_index], valid_distance


def is_contain(num_pre, num):
    result = re.findall('\\b' + '\\b|\\b'.join(map(str, num_pre)) + '\\b', ' '.join(map(str, num)))
    return map(int, result)


if __name__ == '__main__':

    q = '优秀 聪明'
    print 'multi-query\n'
    for header in get_header_by_id(multi_word_query(q)):
        print header
    q = '他太在乎自己是否优秀和聪明'
    print '\nparse-query\n'
    for header in get_header_by_id(phrase_query(q)):
        print header
    q = '函数 5 式 5 语言'
    print '\nclose-query\n'
    for header in get_header_by_id(close_query(q)):
        print header
