# -*- coding: UTF-8 -*-
import requests
from bs4 import BeautifulSoup
import re
import psycopg2
from multiprocessing.dummy import Pool as ThreadPool, Lock

lock = Lock()


def get_all_content(path):
    contents = set()
    pool = ThreadPool(100)
    max_page = get_max_page()
    for x in xrange(1, max_page + 1):
        pool.apply_async(get_content, args=(x, contents))
    pool.close()
    pool.join()
    store(path, contents)


def get_page(n):
    url = 'http://flowingdata.com/most-recent/page/' + str(n)
    try:
        res = requests.get(url)
        return res
    except Exception, e:
        print e
        return get_page(n)


def get_max_page():
    tree = BeautifulSoup(get_page(1).content, 'lxml')
    nav = tree.find('li', class_='page_info')
    return int(re.search('Page \d+ of (\d+)', nav.text).group(1))


def get_content(n, contents):
    res = get_page(n)
    tree = BeautifulSoup(res.content, 'lxml')
    articles = tree.find_all('li', class_='archive-post')
    for article in articles:
        try:
            lock.acquire()
            header = article.find('h3').text
            body = article.find('div', class_='entry').find_all('p')
            content = ''
            for b in body:
                content += b.text
            contents.add((header.encode('utf-8').strip(), content.encode('utf-8').strip()))
            lock.release()
        except Exception, e:
            lock.release()
            print e


def store(path, contents):
    conn = get_conn()
    for header, body in contents:
        if '/' in header:
            header = header.replace('/', '-')
        with open(path + header, 'w')as f:
            f.write(body)
            store_article_path(path + header, header, conn)
    conn.close()


def get_conn():
    try:
        conn = psycopg2.connect(database='scraping',
                                user='postgres', password='123456', host='localhost', port='5432')
    except Exception, e:
        print e
        print '数据库打开失败'
        conn = None
    finally:
        return conn


def store_article_path(path, header, conn):
    cursor = conn.cursor()
    sql = 'INSERT INTO docs (header,path) VALUES(\'%s\',\'%s\')' % (header, path)
    try:
        cursor.execute(sql)
        conn.commit()
    except Exception, e:
        print e
        conn.rollback()
    finally:
        cursor.close()


if __name__ == '__main__':
    p = '/Users/Peterkwok/Documents/docs/'
    get_all_content(p)
