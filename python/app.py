# !/usr/bin/python

__author__ = 'peter_000'
import sys
import lib.htmlparser.parser as psr
from lib.autocomplete import googlecompleter

from PySide.QtWebKit import QWebView
from PySide.QtGui import *
from PySide.QtCore import *

import time
import threading

import jinja2

class webThread(threading.Thread):
    def __init__(self, threadID, name, url, lock):
        threading.Thread.__init__(self)
        self.threadID = threadID
        self.name = name
        self.url = url
        self.lock = lock

    def run(self):
        print "Starting " + self.name
        page = self.parse_url()
        self.lock.acquire()
        view.pages.append(page)
        # view.render()
        self.lock.release()

    def parse_url(self):
        return psr.SOParser(self.url).parse()

class threadManager(object):
    def __init__(self):
        self.threadpool = []
        self.threadLock = threading.Lock()

    def addThread(self, url):
        newThread = webThread(1, str(url), url, self.threadLock)
        self.threadpool.append(newThread)
        newThread.start()

    def wait(self):
        for t in self.threadpool:
            t.join()
        print "Exiting Main Thread"

class ReadlineCompleter(QCompleter):
    def __init__(self, *args, **kwargs):
        super(ReadlineCompleter, self).__init__(*args, **kwargs)
        self.model = QStringListModel()
        self.setModel(self.model)
        self.comp = googlecompleter()
        self.lastupdate = time.time()
        self.setCaseSensitivity(Qt.CaseInsensitive)
        self.setCompletionMode(QCompleter.UnfilteredPopupCompletion)
        self.keyword = ""
        self.lastkeyword = ""
        self.update()

    def update(self):
        if self.keyword == self.lastkeyword:
            return
        elif time.time() < self.lastupdate + 1:
            threading.Timer(1.0, self.update).start()
        else:
            self.lastkeyword = self.keyword
            if len(self.keyword) > 4:
                matches = self.comp.complete(self.keyword)
                if matches:
                    self.model.setStringList(matches)
                    self.lastupdate = time.time()
            else:
                self.model.setStringList([])
                self.lastupdate = time.time()


class View(object):
    def __init__(self):
        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.txtBox = QLineEdit(self.widget)
        layout.addWidget(self.txtBox)

        self.browser = QWebView()
        url = ""
        self.browser.load(QUrl(url))
        self.browser.setZoomFactor(1.4)
        self.browser.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.browser)

        self.completer = ReadlineCompleter()
        self.txtBox.setCompleter(self.completer)

        self.widget.setWindowTitle("Soba")
        self.widget.resize(750, 1000)
        self.widget.show()
        QObject.connect(self.txtBox, SIGNAL("returnPressed()"), self.load_search)
        QObject.connect(self.txtBox, SIGNAL("textEdited(QString)"), self.text_changed)

        self.template = self.setup_jinja()
        self.pages = []

    def text_changed(self):
        self.completer.keyword = self.txtBox.text()
        self.completer.update()


    def setup_jinja(self):
        templateloader = jinja2.FileSystemLoader(searchpath="../")
        templateenv = jinja2.Environment(loader=templateloader)

        template_file = "www/index.html"
        template = templateenv.get_template(template_file)
        return template

    def load_search(self):
        global threadmanager
        keyword = self.txtBox.text()
        results = psr.googleParser(keyword).search()
        html = ""
        shownlist = []
        for result in results:
            if "stackoverflow.com/questions" in result[0] and "tagged" not in result[0]:
                shownlist.append(result[0])
        if len(shownlist) > 0:
            for url in shownlist[:3]:
                threadmanager.addThread(url)
            threadmanager.wait()
        self.render()



    def render(self):
        templateVars = {
                 "pages": self.pages,
               }
        html = self.template.render(templateVars)
        self.browser.setHtml(html)



if __name__ == '__main__':
    app = QApplication(sys.argv)
    threadmanager = threadManager()
    view = View()
    # Run the main Qt loop
    sys.exit(app.exec_())

