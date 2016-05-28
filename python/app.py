# !/usr/bin/python

__author__ = 'peter_000'
import sys
import lib.htmlparser.parser as psr

from PySide.QtWebKit import QWebView
from PySide.QtGui import QApplication, QWidget, QVBoxLayout, QLineEdit
from PySide.QtCore import *

import jinja2

class View(object):
    def __init__(self):


        self.widget = QWidget()
        layout = QVBoxLayout(self.widget)
        # layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        self.browser = QWebView()
        url = ""
        self.browser.load(QUrl(url))
        self.browser.setZoomFactor(1.4)
        self.browser.page().mainFrame().setScrollBarPolicy(Qt.Horizontal, Qt.ScrollBarAlwaysOff)
        layout.addWidget(self.browser)

        self.txtBox = QLineEdit(self.widget)
        layout.addWidget(self.txtBox)

        self.widget.setWindowTitle("Soba")
        self.widget.setBaseSize(800, 900)
        self.widget.show()
        QObject.connect(self.txtBox, SIGNAL("returnPressed()"), self.loadSearch)

        self.template = self.setupJinja()

    def setupJinja(self):
        templateLoader = jinja2.FileSystemLoader(searchpath="../")
        templateEnv = jinja2.Environment(loader=templateLoader)

        TEMPLATE_FILE = "www/index.html"
        template = templateEnv.get_template(TEMPLATE_FILE)
        return template


        outputText = template.render( templateVars )

    def loadSearch(self):
        keyword = self.txtBox.text()
        results = psr.googleParser(keyword).search()
        html = ""
        shownlist = []
        for result in results:
            if "stackoverflow.com/questions" in result[0] and "tagged" not in result[0]:
                shownlist.append(result[0])
        if len(shownlist) > 0:
            print shownlist[0]
            page = psr.SOParser(shownlist[0]).parse()
            title = page['title']
            answers = page['content']
            templateVars = {
                             "title": title,
                             "answers": answers
                           }
            html = self.template.render(templateVars)
        self.browser.setHtml(html)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    view = View()

    # Run the main Qt loop
    sys.exit(app.exec_())

