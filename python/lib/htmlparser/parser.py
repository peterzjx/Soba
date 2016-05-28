__author__ = 'peter_000'
from bs4 import BeautifulSoup
import urllib, urllib2


class googleParser(object):
    def __init__(self, keyword):
        self.keyword = keyword.replace(" ", "%20")
        self.result = []

    def request(self, url):
        request = urllib2.Request(url, None,
                                  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) \
                                    AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
        urlfile = urllib2.urlopen(request)
        page = urlfile.read()
        soup = BeautifulSoup(page, "html.parser")
        return soup

    def search(self):
        url = "https://www.google.com/search?q=site:stackoverflow.com+%s" % self.keyword
        self.parse(url)
        return self.result

    def parse(self, url):
        soup = self.request(url)
        for h3 in soup.findAll('h3', {"class": "r"}):
            if h3.a.has_attr('href'):
                self.result.append((h3.a['href'], h3.a.string))
        return


class SOParser(object):
    def __init__(self, url):
        self.url = url

    def request(self, url):
        request = urllib2.Request(url, None,
                                  {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_7_4) \
                                    AppleWebKit/536.11 (KHTML, like Gecko) Chrome/20.0.1132.57 Safari/536.11'})
        urlfile = urllib2.urlopen(request)
        page = urlfile.read()
        soup = BeautifulSoup(page, "html.parser")
        return soup

    def parse(self):
        soup = self.request(self.url)
        result = {}
        content = []
        title = soup.find('title').getText()
        result['title'] = title
        for posttext in soup.findAll('div', {"class": "post-text"}):
            content.append(str(posttext).decode('UTF-8'))
        result['content'] = content
        return result


def test_googleparser():
    gp = googleParser()
    keyword = "pandas"
    url = "https://www.google.com/search?q=site:stackoverflow.com+%s" % keyword
    gp.parse(url)
    print gp.result


def test_soparser():
    sp = SOParser()
    url = "http://stackoverflow.com/questions/5015483/test-if-an-attribute-is-present-in-a-tag-in-beautifulsoup"
    print sp.parse(url)


if __name__ == '__main__':
    test_soparser()
