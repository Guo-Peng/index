# -*- coding: UTF-8 -*-
from get_article import store
import requests
from bs4 import BeautifulSoup
import bs4
from multiprocessing.dummy import Pool as ThreadPool, Lock

lock = Lock()


def get_blog(path):
    pool = ThreadPool(20)
    url = 'http://www.yinwang.org'
    contents = set()
    for blog_url in get_blog_url(url):
        pool.apply_async(get_content, args=(blog_url, contents))
    pool.close()
    pool.join()
    store(path, contents, 'docs_cn')


def get_content(url, contents):
    res = request(url)
    tree = BeautifulSoup(res.content, 'lxml')
    content = tree.find('body').contents
    header = ''
    body = ''
    for tag in content[2:]:
        if not isinstance(tag, bs4.element.Tag):
            continue
        if tag.name == 'h2':
            header = tag.text
        body += tag.text
    lock.acquire()
    contents.add((header.encode('utf-8').strip(), body.encode('utf-8').strip()))
    lock.release()


def get_blog_url(url):
    res = request(url)
    tree = BeautifulSoup(res.content, 'lxml')
    items = tree.find_all('li', class_='list-group-item title')
    blog_url = set([item.a['href'] for item in items])
    return blog_url


def request(url):
    try:
        res = requests.get(url)
        return res
    except Exception, e:
        print e
        return request(url)


if __name__ == '__main__':
    get_blog('/Users/Peterkwok/Documents/docs_cn/')
