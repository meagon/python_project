

#-*- coding=utf-8 -*-

import urlparse
import lxml
import requests


class Page(object):

    def __init__(self, url="", deepth=None, content=None, referer=None):
        self.url = url
        self.deepth = deepth
        self.content = content
        self.referer = referer
        self.html = None
        self.status = 0
        self.childs = set()
        self.parsed = False
        self.status_code = 0

    def __repr__(self):
        return '<%r %r %r>' % (
            self.__class__.__name__,
            hex(abs(id(self)))[2:],
            self.url)

    def add_child(self, child):
        self.childs.add(child)

    def is_empty(self):
        return bool(not self.content)

    def fill_html(self):
        ret = False
        if self.content:
            # if isinstance( self.content , unicode) :
            doc = lxml.html.fromstring(self.content)
            doc.make_links_absolute(base_url=self.url)
            self.html = doc
            return True
        return False

    def fill_content(self, content):
        self.content = content

    def xpath(self, path):
        if isinstance(self.html, lxml.html.HtmlElement):
            return self.html.xpath(path)

    def css_select(self, css_selector):
        if isinstance(self.html, lxml.html.HtmlElement):
            return self.html.cssselect(css_selector)

    def find_links(self, css_selector=None, xpath_selector=None):
        logger.info("at find links ..........%r ...?" % self.deepth)
        links = set()
        return links

    def download(self):
        logger.info("in page  download")
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 6.2; WOW64; rv:36.0) Gecko/20140101 Firefox/36.0", }
        try:
            r = requests.get(self.url, headers=header)
            self.content = r.content
            self.status_code = r.status_code
            logger.info("download ok ?")
        except Exception as e:
            logger.exception(e)

    def is_img(self):
        if self.url:
            return self.url.endswith(".jpg")
        return False

    def store(self, dir_path="pics"):

        name = urlparse.urlparse(self.url)
        name = "_".join((name.netloc, name.path.replace("/", "_")))
        filename = os.path.join(dir_path, name)
        f = open(filename, 'wb')
        f.write(self.content)
        f.close()
