# -*- coding: UTF-8 -*-
from inverted_index import decorator_inverted
from get_article import get_conn
import re


@decorator_inverted(100)
def multi_word_query(query, stop_words, inverted):
    words = [word.lower() for word in re.split('\W+', query) if word not in stop_words if word is not '']
    if words:
        docs = [set(inverted[word].keys()) for word in words]
        result_id = reduce(lambda x, y: x & y, docs) if docs else []
        return result_id
    else:
        return []


@decorator_inverted(100)
def phrase_query(query, stop_words, inverted):
    multi_query_id = list(multi_word_query(query))
    if multi_query_id:
        words = [word.lower() for word in re.split('\W+', query) if word is not '']
        valid_index = [words.index(word) for word in words if word not in stop_words]
        if len(valid_index) <= 1:
            return []
        for doc_id in multi_query_id:
            for x in xrange(len(valid_index) - 1):
                if not is_neighbour(inverted[words[valid_index[x]]][doc_id],
                                    inverted[words[valid_index[x + 1]]][doc_id],
                                    valid_index[x + 1] - valid_index[x]):
                    multi_query_id.remove(doc_id)
                    break
        return multi_query_id


@decorator_inverted(100)
def close_query(query, stop_words, inverted):
    words, distance = get_distance(query, stop_words)
    multi_query_id = list(multi_word_query('\t'.join(words)))
    if multi_query_id:
        for doc_id in multi_query_id:
            for x in xrange(len(words) - 1):
                if not is_neighbour(inverted[words[x]][doc_id],
                                    inverted[words[x + 1]][doc_id],
                                    distance[x], True):
                    multi_query_id.remove(doc_id)
                    break
        return multi_query_id


def get_header_by_id(result_id):
    if not result_id:
        return []
    conn = get_conn()
    cursor = conn.cursor()
    sql = 'SELECT header FROM docs WHERE'
    for id in result_id:
        sql += ' id = %d or' % id
    sql = sql[-len(sql):-3]
    cursor.execute(sql)
    try:
        cursor.execute(sql)
        conn.commit()
        result = cursor.fetchall()
        return [header[0] for header in result]
    except Exception, e:
        print e
        conn.rollback()
        return get_header_by_id(result_id)
    finally:
        cursor.close()
        conn.close()


def get_distance(query, stop_words):
    split_words = [word.lower() for word in re.split('\W+', query) if word is not '']
    words = split_words[::2]
    distance = split_words[1::2]
    distance = map(int, distance)
    valid_index = [index for index, word in enumerate(words) if word not in stop_words]
    valid_distance = []
    for x in xrange(len(valid_index) - 1):
        valid_distance.append(sum(distance[valid_index[x]:valid_index[x + 1]]))
    return [words[index] for index in valid_index], valid_distance


def is_neighbour(index_list_1, index_list_2, distance=1, close=False):
    first = 0
    second = 0
    while True:
        if first == len(index_list_1) or second == len(index_list_2):
            return False
        if index_list_2[second] < index_list_1[first]:
            second += 1
            continue
        if close:
            if index_list_2[second] - index_list_1[first] <= distance:
                return True
        else:
            if index_list_2[second] - index_list_1[first] == distance:
                return True
            first += 1


if __name__ == '__main__':
    # when you analyze and visualize, remember the context of your data.
    q = 'context visualize analyze'
    print 'multi-query\n'
    for header in get_header_by_id(multi_word_query(q)):
        print header

    q = 'analyze and visualize'
    print '\nparse-query\n'
    for header in get_header_by_id(phrase_query(q)):
        print header

    print '\nclose-query\n'
    q = 'analyze 10 data'
    for header in get_header_by_id(close_query(q)):
        print header
