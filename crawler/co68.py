
#-*- coding=utf-8 -*-

import requests
import traceback
import lxml
import lxml.html as html
import gevent
from gevent import queue, lock, monkey

import gevent.monkey
import sys
import signal
import re
import os
import time
import sqlite3
import urlparse
from pybloom import BloomFilter
import argparse
from log import log_service

gevent.monkey.patch_socket()
#- self defined module

from page import Page
from spider import spider



logger = log_service("craw_log.log", debug=True)
url_pool = BloomFilter(capacity=50000, error_rate=0.0001)
download_records = set()


def db_save(table, url):
    global sqlite
    conn = sqlite
    cur = conn.cursor()
    cur.execute("INSERT INTO %s (url) VALUES ('%s') " % (table, url))
    conn.commit()


def kill_all():

    for i in g_workers:
        i.kill()


class Topit_Page(Page):

    def __init__(self, img_store_path="./pics/", *args, **kwds):
        self.img_store_path = img_store_path
        super(Topit_Page, self).__init__(*args, **kwds)

    def find_links(self, css_selector=None, xpath_selector=None):
        self.parsed = True
        logger.info("at find links %r" % self.deepth)
        links = set()
        ITEM_PATTERN = re.compile("http://www\.topit\.me/item/\d+.$")

        IMG_UNIQ_SELECTOR = "#item-tip"

        if not self.fill_html():
            logger.debug("fill content error..")
            return links
        logger.debug("%r" % self.html)
        if self.deepth == 0 and isinstance(self.html, lxml.html.HtmlElement):
            logger.info(self.html)
            content = self.css_select("#content")
            logger.info("in select  page element")
            if content:
                logger.debug(content)
                urls = content[0].iterlinks()
                urls = [i[2] for i in urls if ITEM_PATTERN.search(i[2])]
                for i in urls:
                    links.add(i)
        if self.deepth != 0 and ITEM_PATTERN.search(self.url):
            if isinstance(self.html, lxml.html.HtmlElement):
                z = self.html.cssselect(IMG_UNIQ_SELECTOR)
                if z:
                    link = z[0].get("href")
                    links.add(link)
        logger.debug("find links %r " % links)
        return links

    def find_all_child(self):
        global url_pool

        logger.info("in finding child .......... ")
        links = self.find_links()
        if not links:
            logger.info("children %r" % str(links))
            logger.warning(
                "find_links might error .. got nothing ... in url: %r" % self.url)
        for i in links:
            if url_pool and i in url_pool:
                logger.debug("found it int pool %r" % i)
                continue
            child_deepth = self.deepth is not None and self.deepth + 1 or None
            child_page = Topit_Page(
                url=i, deepth=child_deepth, referer=self.url)
            self.add_child(child_page)
            url_pool.add(child_page)
            db_save("childs", child_page.url)
        return self

    def store(self, dir_path="pics"):

        name = urlparse.urlparse(self.url)
        name = "_".join((name.netloc, name.path.replace("/", "_")))
        filename = os.path.join(dir_path, name)
        f = open(filename, 'wb')
        f.write(self.content)
        f.close()


def generate_init_tasks(urls=[], img_store_path="./pics"):
    tasks = []

    job = "download"
    if isinstance(urls, list):
        for url in urls:
            page = Topit_Page(img_store_path=img_store_path, url=url, deepth=0)
            task = (job, None, spider.download, (), {"page": page}, None)
            tasks.append(task)

        return tasks


def test_topit(page_num=20, thread_num=10, limit=None,
               img_store_path="./pics/"):

    global sqlite
    global url_pool
    global g_workers
    global img_download_counter

    img_download_counter = 0

    URL_PREFIX = "http://www.topit.me/"

    def construct_root_url(num=2):
        url_prefix = URL_PREFIX
        url = lambda n: url_prefix + "?p=" + str(n)
        start_pages = map(url, range(num))
        start_pages = set(start_pages)
        return start_pages 

    DB_PATH = "./topit.db"
    sqlite = sqlite3.connect(DB_PATH)
    cur = sqlite.cursor()
    cur.execute("SELECT url FROM urls")
    urls = cur.fetchall()
    map(url_pool.add, urls)
    del urls

    urls = construct_root_url(num=page_num)
    urls = list(urls)

    tasks = generate_init_tasks(urls=urls, img_store_path=img_store_path, )

    g_workers = []

    store_queue = queue.Queue()
    img_download_queue = queue.Queue()
    parse_queue = queue.Queue()
    download_queue = queue.Queue()

    spider_instance = spider(urls=urls,
                             store_queue=store_queue,
                             img_download_queue=img_download_queue,
                             download_queue=download_queue,
                             parse_queue=parse_queue,
                             limits=limit
                             )

    spider_instance._setup(tasks, download_queue)
    for i in range(thread_num):
        w = gevent.spawn(spider_instance.run,)
        w.working = None
        w.page = None
        g_workers.append(w)
    gevent.joinall(g_workers)




signal.signal(signal.SIGTERM, kill_all)

if __name__ == "__main__":

    thread_num = 10
    dest_dir = "./pics"
    max_limits = None

    parser = argparse.ArgumentParser(description="coroutine spider ")
    parser.add_argument(
        "-n", "--thread_num", help="specified concurrent threads number", metavar="thread_num")
    parser.add_argument(
        "-o", "--dest_dir", help="specified the dir where download to", metavar="dst_dir")
    parser.add_argument(
        "-l", "--limit", help="specified how many pics to download", metavar="limit")

    args = parser.parse_args()

    if args.thread_num:
        thread_num = int(args.thread_num)
    if args.dest_dir:
        dest_dir = args.dest_dir
        if os.path.exists(dest_dir) and os.path.isdir(dest_dir):
            print("will download directory : %r" % dest_dir)
        elif not os.path.exists(dest_dir):
            os.mkdir(dest_dir)

    if args.limit:
        limits = int(args.limit)
    else:
        limits = None

    test_topit(thread_num=thread_num, limit=limits, img_store_path=dest_dir,)
