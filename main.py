import sys, os, json

from PyQt5.QtWebEngineWidgets import QWebEngineView
from PyQt5.QtWidgets import (QApplication, QWidget, QVBoxLayout, QHBoxLayout, QStackedLayout,
                             QPushButton, QLabel, QLineEdit, QTabWidget, QTabBar, QFrame, QShortcut,
                             QKeySequenceEdit, QSplitter)
from PyQt5.QtGui import QIcon, QWindow, QImage, QKeySequence
from PyQt5.QtCore import *
from PyQt5.QtWebEngine import *


class Address_Bar(QLineEdit):
    def __init__(self):
        super().__init__()

    def mousePressEvent(self, e):
        self.selectAll()

class Application(QFrame):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Web Browser")
        self.create_app()
        self.setBaseSize(1024, 768)
        self.setMinimumSize(1024, 768)
        self.setWindowIcon(QIcon("logo.png"))

    def create_app(self):

        self.layout = QVBoxLayout()
        self.toolbar = QWidget()
        self.toolbar.setObjectName("toolbar")
        self.toolbar_layout = QHBoxLayout()
        self.layout.setSpacing(0)
        self.layout.setContentsMargins(0, 0, 0, 0)

        self.shortcutNewTab = QShortcut(QKeySequence("Ctrl+T"), self)
        self.shortcutNewTab.activated.connect(self.add_tab)

        self.shortcutReload = QShortcut(QKeySequence("Ctrl+R"), self)
        self.shortcutReload.activated.connect(self.reload_page)

        # Create Tabs
        self.tab_bar = QTabBar(movable=True, tabsClosable=True)
        self.tab_bar.tabCloseRequested.connect(self.close_tab)
        self.tab_bar.tabBarClicked.connect(self.switch_tab)
        self.tab_bar.setCurrentIndex(0)
        self.tab_bar.setDrawBase(False)

        # Keep track of tabs
        self.tab_count = 0
        self.tabs = []

        # Add Tab Button
        self.AddTabButton = QPushButton("+")
        self.AddTabButton.clicked.connect(self.add_tab)

        # Create address bar
        self.address_bar = Address_Bar()
        self.address_bar.returnPressed.connect(self.browse_to)

        # Set Toolbar Buttons
        self.back_button = QPushButton("<")
        self.back_button.clicked.connect(self.go_back)

        self.forward_button = QPushButton(">")
        self.forward_button.clicked.connect(self.go_forward)

        self.reload_button = QPushButton("R")
        self.reload_button.clicked.connect(self.reload_page)

        #Build Toolbar
        self.toolbar.setLayout(self.toolbar_layout)
        self.toolbar_layout.addWidget(self.back_button)
        self.toolbar_layout.addWidget(self.forward_button)
        self.toolbar_layout.addWidget(self.reload_button)
        self.toolbar_layout.addWidget(self.address_bar)
        self.toolbar_layout.addWidget(self.AddTabButton)

        # Set Main View
        self.container = QWidget()
        self.container.layout = QStackedLayout()
        self.container.setLayout(self.container.layout)

        self.layout.addWidget(self.tab_bar)
        self.layout.addWidget(self.toolbar)
        self.layout.addWidget(self.container)
        self.setLayout(self.layout)

        self.add_tab()

        self.show()

    def close_tab(self, i):
        self.tab_bar.removeTab(i)

    def add_tab(self):
        i = self.tab_count

        self.tabs.append(QWidget())
        self.tabs[i].layout = QVBoxLayout()
        self.tabs[i].layout.setContentsMargins(0, 0, 0, 0)
        self.tabs[i].setObjectName("tab" + str(i))

        # Open Webview
        self.tabs[i].content = QWebEngineView()
        self.tabs[i].content.load(QUrl.fromUserInput("http://google.com"))

        self.tabs[i].content.titleChanged.connect(lambda: self.set_tab_content(i, "title"))
        self.tabs[i].content.iconChanged.connect(lambda: self.set_tab_content(i, "icon"))
        self.tabs[i].content.urlChanged.connect(lambda: self.set_tab_content(i, "url"))

        # Add webview to tabs layout
        # self.tabs[i].splitview = QSplitter()
        self.tabs[i].layout.addWidget(self.tabs[i].content)

        # self.tabs[i].splitview.addWidget(self.tabs[i].content)

        # Set top level tab from [] to layout
        self.tabs[i].setLayout(self.tabs[i].layout)

        # Add tab to top level stacked widget
        self.container.layout.addWidget(self.tabs[i])
        self.container.layout.setCurrentWidget(self.tabs[i])

        # Create tab on tab bar,
        # Set tabData to tab<#> So it knows what self.tabs[#] it needs to control
        self.tab_bar.addTab("New Tab")
        self.tab_bar.setTabData(i, {"object": "tab" + str(i), "initial": i})
        self.tab_bar.setCurrentIndex(i)

        self.tab_count += 1

    def switch_tab(self, i):
        tab_data = self.tab_bar.tabData(i)["object"]
        tab_content = self.findChild(QWidget, tab_data)
        self.container.layout.setCurrentWidget(tab_content)
        new_url = tab_content.content.url().toString()
        self.address_bar.setText(new_url)


    def browse_to(self):
        text = self.address_bar.text()

        i = self.tab_bar.currentIndex()
        tab = self.tab_bar.tabData(i)["object"]
        web_view = self.findChild(QWidget, tab).content

        if "http" not in text:
            if "." not in text:
                url = "https://www.google.com/search?q=" + text
            else:
                url = "http://" + text
        else:
            url = text

        web_view.load(QUrl.fromUserInput(url))

    def set_tab_content(self, i, type):
        tab_name = self.tabs[i].objectName()
        count = 0
        running = True

        current_tab = self.tab_bar.tabData(self.tab_bar.currentIndex())["object"]

        if current_tab == tab_name and type == "url":
            new_url = self.findChild(QWidget, tab_name).content.url().toString()
            self.address_bar.setText(new_url)
            return False

        while running:
            tab_data_name = self.tab_bar.tabData(count)

            if count >= 99:
                running = False

            if tab_name == tab_data_name["object"]:
                if type == "title":
                    new_title = self.findChild(QWidget, tab_name).content.title()
                    self.tab_bar.setTabText(count, new_title)
                elif type == "icon":
                    new_icon = self.findChild(QWidget, tab_name).content.icon()
                    self.tab_bar.setTabIcon(count, new_icon)
                running = False
            else:
                count += 1

    def go_back(self):
        activeIndex = self.tab_bar.currentIndex()
        tab_name = self.tab_bar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.back()

    def go_forward(self):
        activeIndex = self.tab_bar.currentIndex()
        tab_name = self.tab_bar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.forward()

    def reload_page(self):
        activeIndex = self.tab_bar.currentIndex()
        tab_name = self.tab_bar.tabData(activeIndex)["object"]
        tab_content = self.findChild(QWidget, tab_name).content

        tab_content.reload()


if __name__ == "__main__":
    app = QApplication(sys.argv)
   # os.environ['QTWEBENGINE_REMOTE_DEBUGGING'] = "667"

    window = Application()

    with open("style.css", "r") as style:
        app.setStyleSheet(style.read())

    sys.exit(app.exec_())