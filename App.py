#!/usr/bin/env python3

"""
This code or file is pertinent to the 'Username Searcher' Project
Copyright (c) 2023, 'Aymen Brahim Djelloul'. All rights reserved.
Use of this source code is governed by a MIT license that can be
found in the LICENSE file.


@author : Aymen Brahim Djelloul.
date : 16.09.2023
version : 1.1
LICENSE : MIT

"""

# imports
import sys
import os.path
import webbrowser
from time import perf_counter
from functools import partial
from searcher import is_connected, Searcher
from PyQt5.QtGui import *
from PyQt5.QtCore import *
from PyQt5.QtWidgets import *
from PyQt5.QtCore import pyqtSignal, QObject

# define variables
_author_: str = 'Aymen Brahim Djelloul'
_version_: str = '1.1'
_release_d: str = '16.09.2023'


class App(QWidget):
    """
    Main application window class inheriting from QWidget.

    This class serves as the core UI for the application, managing user interactions,
    layouts, and connecting interface elements to backend logic.

    Typical responsibilities include:
    - Initializing the main window.
    - Setting up layouts, widgets, and styles.
    - Handling user inputs and events.
    - Communicating with underlying data or processing functions.

    Attributes:
        parent (QWidget): Optional parent widget for this window.

    """
    search_results = {}
    key_pressed = pyqtSignal(int)

    def __init__(self) -> None:
        super().__init__()

        # init about window
        about_window = AboutWindow()

        # define variables
        self.group_box = None
        self.old_Pos = None
        self.form_layout = None
        self.try_again_button = None
        self.no_internet_logo = None
        self.no_internet_logo_lbl = None
        self.no_internet_lbl = None
        self.no_internet_lbl = None
        self.loading_animation = None
        self.animation_label = None
        self.search_obj = None
        self.scroll_area = None

        # Load Application Font
        base_dir: str = os.path.dirname(os.path.abspath(__file__))
        font_path: str = os.path.join(base_dir, "resources", "Assets", "Cairo-Regular.ttf")

        font_id = QFontDatabase.addApplicationFont(font_path)

        if font_id == -1:
            print(f"[ERROR] Failed to load font: {font_path}")
        else:
            loaded_fonts = QFontDatabase.applicationFontFamilies(font_id)
            print(f"[INFO] Loaded font: {loaded_fonts[0]}")

        flags_button_style = """
                QPushButton {
                    width: 30px;
                    height: 30px;
                    border: 1px solid;
                    border-radius: 5px;
                    border-color: transparent;
                }  
                QPushButton#close_btn {
                    border-to-right-radius: 8px;
                }
                QPushButton#close_btn::hover {
                    background-color: #bf1f1f;
                    border-color: #bf1f1f;
                }
                QPushButton::hover {
                    background-color: #dedede;
                    border-color: #dedede;
                }
                """

        self.search_stop_btn_style = """
                QPushButton {
                    width: 35px;
                    height: 35px;
                    border: 1px solid;
                    border-radius: 15px;
                    border-color: #e8e8e8;
                    background-color: #e8e8e8;
                
                }
                
                QPushButton::hover {
                    background-color: #dedede;
                    border-color: #dedede;
                }
                
                QPushButton#clear_text_btn {
                    width: 31px;
                    height: 31px;
                    background-color: transparent;
                    border: 1px solid;
                    border-color: transparent;
                    
                }
                
                QPushButton#clear_text_btn::hover {
                    border-color: #dedede;
                    border-radius: 7px;
                    background-color: #dedede;
                    
                }
                """

        self.result_btn_style = """
                QPushButton {
                    width: 295px;
                    height: 35px;
                    
                    border: 1px solid;
                    border-radius: 8px;
                    font-weight: 400;    
                    
                    background-color: #e8e8e8;
                    border-color: #6736f7;
                    color: #6736f7;
                    
                    margin: 5px;
                }
                
                QPushButton::hover {
                    background-color: #5b40ad;
                    color: #e8e8e8;
                    border-color: #e8e8e8;
                    
                }
                QPushButton::pressed {
                    background-color: #3702b3;
                    border-color: #e8e8e8;
                    color: #e8e8e8
                
                }
                
                """

        # set the Main Window
        self.setWindowIcon(QIcon('images/icon.ico'))
        self.setWindowTitle(f'Username Searcher v{_version_}')
        self.setFixedSize(440, 520)
        self.setStyleSheet("""
        background-color:  #e8e8e8;
             
        QScrollBar:vertical {
            margin: 5px;
         }
         """)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # create close and minimize buttons
        close_button = QPushButton(self)
        close_button.setIcon(QIcon('resources/Assets/close_icon.png'))
        close_button.setGeometry(400, 10, 30, 30)
        close_button.setStyleSheet(flags_button_style)
        close_button.setObjectName('close_btn')
        close_button.setCursor(Qt.PointingHandCursor)
        close_button.clicked.connect(lambda: sys.exit())
        # minimize button
        minimize_button = QPushButton(self)
        minimize_button.setIcon(QIcon('resources/Assets/minimize_icon.png'))
        minimize_button.setGeometry(365, 10, 30, 30)
        minimize_button.setStyleSheet(flags_button_style)
        minimize_button.setCursor(Qt.PointingHandCursor)
        minimize_button.clicked.connect(lambda: self.showMinimized())

        # create about PushButton
        about_button = QPushButton(self)
        about_button.setIcon(QIcon('resources/Assets/about.png'))
        about_button.setIconSize(QSize(30, 30))
        about_button.move(10, 10)
        about_button.setCursor(Qt.PointingHandCursor)
        about_button.clicked.connect(lambda: about_window.show())
        about_button.setStyleSheet(flags_button_style)

        # create a scroll area
        self.vbox = QVBoxLayout(self)

        self.scroll_area = QScrollArea(self)
        self.scroll_area.move(55, 160)
        self.scroll_area.setStyleSheet("""
         QScrollArea {
            width: 380px;
            height: 400px;
            border: none;
         }
        """)

        self.scroll_area.setLayout(self.vbox)
        self.scroll_area.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # hide the scroll area widget
        self.scroll_area.hide()

        # start the main method
        # check if there is internet connection
        if not is_connected():
            self.not_connected(None)
        else:
            self._main_(None)

    def mousePressEvent(self, event) -> None:
        """ This method will handle the """
        self.old_Pos = event.globalPos()

    def mouseMoveEvent(self, event) -> None:
        """ This method will handle the mouse movement"""

        delta = QPoint(event.globalPos() - self.old_Pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_Pos = event.globalPos()

    def keyPressEvent(self, event) -> None:
        """ this method will get keyboard strokes"""

        if event.key() == Qt.Key_Escape:
            self._stop_search()

        if event.key() == Qt.Key_Return or event.key() == Qt.Key_Enter:
            if self.is_username_valid():
                self._start_search()

    @staticmethod
    def clear_widgets(widgets) -> None:
        """ this method will clear all widgets when switching between windows"""

        if widgets is None:
            return

        try:
            for widget in widgets:
                widget.hide()
        except TypeError:
            widgets.hide()

    @staticmethod
    def open_url(url) -> None:
        """ This method to open urls get the url from the search results dict"""
        webbrowser.open(url)

    def try_connect(self, widgets_to_clear) -> None:
        """ this method will try to re-connect when there is no internet connection"""

        # clear widgets
        self.clear_widgets(widgets_to_clear)

        # set loading animation
        self._start_loading_animation(195, 180, 50, 50)

        # start a loop for 1 sec
        loop = QEventLoop()
        QTimer.singleShot(1000, loop.quit)
        loop.exec_()

        # check internet connection
        if not is_connected():
            self.not_connected(self.animation_label)
        else:
            self._main_(self.animation_label)

    def _main_(self, widgets_to_clear) -> None:
        """ this is the main window """

        # clear widgets
        self.clear_widgets(widgets_to_clear)

        # create a search field
        self.search_field = QLineEdit(self)
        self.search_field.move(40, 70)
        self.search_field.setFont(QFont('Sans-serif', 14))
        self.search_field.textChanged.connect(self.search_field_text_changed)
        self.search_field.setStyleSheet("""
        
        QLineEdit {
            width: 300px;
            height: 40px;
            display: inline;
            
            border: 2px solid;
            border-radius: 5px;
            border-color: #683cb0;
            background-color: #e8e8e8;
            
            padding: 2px;
            padding-left: 60px;
            font-weight: 400;
            
        }
        
        """)

        # create search button
        self.search_btn = QPushButton(self)
        self.search_btn.setIcon(QIcon('resources/Assets/search_icon.png'))
        self.search_btn.setIconSize(QSize(30, 30))
        self.search_btn.move(45, 75)
        self.search_btn.setCursor(Qt.PointingHandCursor)
        self.search_btn.clicked.connect(self._start_search)
        self.search_btn.setStyleSheet(self.search_stop_btn_style)

        # create unvalid username label
        self.message_lbl = QLabel(self)
        self.message_lbl.move(45, 140)
        self.message_lbl.setFont(QFont('Arial', 11))
        self.message_lbl.setStyleSheet('font-weight: 400;')
        self.message_lbl.hide()

        # create stop search button
        self.stop_search_btn = QPushButton(self)
        self.stop_search_btn.setIcon(QIcon('resources/Assets/stop_process_icon.png'))
        self.stop_search_btn.setIconSize(QSize(30, 30))
        self.stop_search_btn.move(45, 75)
        self.stop_search_btn.setCursor(Qt.PointingHandCursor)
        self.stop_search_btn.clicked.connect(self._stop_search)
        self.stop_search_btn.setStyleSheet(self.search_stop_btn_style)
        # hide stop search button by default
        self.stop_search_btn.hide()

        # create clear text button
        self.clear_txt_btn = QPushButton(self)
        self.clear_txt_btn.setIcon(QIcon('resources/Assets/clear_icon.png'))
        self.clear_txt_btn.setIconSize(QSize(27, 27))
        self.clear_txt_btn.move(360, 78)
        self.clear_txt_btn.setCursor(Qt.PointingHandCursor)
        self.clear_txt_btn.clicked.connect(self._reset)
        self.clear_txt_btn.setObjectName('clear_text_btn')
        self.clear_txt_btn.setStyleSheet(self.search_stop_btn_style)
        # hide it
        self.clear_txt_btn.hide()

        # create animation and main page labels
        self.main_logo_lbl = QLabel(self)
        self.main_logo_lbl.setGeometry(165, 170, 125, 140)
        self.main_logo_lbl.setStyleSheet('border: none;')

        # load gif animation
        self.main_logo = QPixmap('resources/Assets/search_icon.png')
        self.main_logo.scaled(QSize(80, 80))
        # self.main_animation.setScaledSize(QSize(110, 110))
        self.main_logo_lbl.setPixmap(self.main_logo)
        # self.main_animation.start()

        self.main_lbl = QLabel('Search for username across Social Networks'
                               '\n        Results will appear here as you type.', self)
        self.main_lbl.setFont(QFont('Cairo', 11))
        self.main_lbl.setStyleSheet('color: #683cb0;\n'
                                    'font-weight: 500;')
        self.main_lbl.move(60, 310)

        self.main_description = QLabel(self)
        self.main_description.move(55, 440)
        self.main_description.setText('For search Press [Enter].\n'
                                      'To cancel or stop the search Press [ESC].')
        self.main_description.setFont(QFont('Cairo', 10))
        self.main_description.setStyleSheet('color: #8a8a8a;')
        self.main_description.adjustSize()

    def display_message(self, msg: str) -> None:
        """ this method will appear a message of search status"""

        self.message_lbl.setText(msg)
        self.message_lbl.setStyleSheet('color: #5e34eb;\n'
                                       'font-weight: 4000;')
        self.message_lbl.adjustSize()
        self.message_lbl.show()

    def _reset(self) -> None:
        """ This method will reset the search"""

        self.search_field.clear()
        self.scroll_area.hide()
        self.message_lbl.hide()
        self.show_main()

    def search_field_text_changed(self) -> None:
        """ This method will handle the text field manipulation"""

        if self.search_field.text() != '':
            self.clear_txt_btn.show()
        else:
            self.clear_txt_btn.hide()

    def hide_main(self) -> None:
        """ this method will hide only the main labels and the description"""
        self.main_lbl.hide()
        self.main_description.hide()
        self.main_logo_lbl.hide()
        # self.main_animation.stop()

    def show_main(self) -> None:
        """ this method will appear again the main stuff"""
        self.main_lbl.show()
        self.main_description.show()
        self.main_logo_lbl.show()
        # self.main_animation.start()

    def _start_loading_animation(self, x, y, x_size, y_size) -> None:

        # create loading animation
        self.animation_label = QLabel(self)
        self.animation_label.resize(100, 100)
        self.animation_label.move(x, y)
        self.animation_label.setStyleSheet('border: none;')

        # loading the GIF
        self.loading_animation = QMovie('resources/Assets/loading.gif')
        self.loading_animation.setScaledSize(QSize(x_size, y_size))
        self.animation_label.setMovie(self.loading_animation)
        self.loading_animation.start()
        self.animation_label.show()

    def _stop_loading_animation(self) -> None:
        self.loading_animation.stop()
        self.animation_label.hide()

    def _stop_search(self) -> None:
        """ this method will break the search process"""

        try:
            self.worker.stop_search()
            self.stop_search_btn.hide()
            self.search_btn.show()
            self._stop_loading_animation()

        except AttributeError:
            pass

    def is_username_valid(self) -> bool:
        """Verify if the input username is valid."""

        username = self.search_field.text().strip()

        if not username:
            self.display_unvalid_username_msg('Enter a username!')
            return False

        special_symbols = {'&', '=', ',', '+', '>', '<', '-', "'"}
        for symbol in special_symbols:
            if symbol in username:
                self.display_unvalid_username_msg(f"Username cannot contain '{symbol}'")
                return False

        return True

    def display_unvalid_username_msg(self, msg) -> None:
        """ this method will display message for username when entering a wrong string"""

        self.message_lbl.setText(msg)
        self.message_lbl.setStyleSheet('color: #d91811;')
        self.message_lbl.adjustSize()
        self.message_lbl.show()

    def on_search_finish(self) -> None:
        """ this method display the search results to the user"""

        search_end_t = perf_counter()

        self._stop_loading_animation()
        self.stop_search_btn.hide()
        self.search_btn.show()

        # display results
        self.form_layout = QFormLayout(self)
        self.group_box = QGroupBox(self)

        for name, url in self.search_results.items():
            widget = QPushButton(name, self)
            widget.setStyleSheet(self.result_btn_style)
            widget.setFont(QFont('Cairo', 14))
            widget.setCursor(Qt.PointingHandCursor)

            widget.clicked.connect(partial(self.open_url, url))
            self.form_layout.addWidget(widget)

        self.group_box.setLayout(self.form_layout)
        self.group_box.setStyleSheet('border: none;')
        self.scroll_area.setWidget(self.group_box)
        self.scroll_area.show()
        # display search has been finished message
        self.display_message(f'Finished in {round(search_end_t - self.search_start_t, 2)} s.')

    def update_search_results(self, results: dict):
        """ this method will update the search results from thread"""
        # clear dictionary results
        self.search_results.clear()
        self.search_results.update(results)

    def _start_search(self):
        """ this method is for start the search"""

        # check search field if it is valid
        if not self.is_username_valid():
            return

        # display searching message
        self.display_message(f"Searching For '{self.search_field.text()}' ...")
        # hide unvalid username label and the main stuff
        self.hide_main()

        # first clear all widgets and variables from previous search
        if self.scroll_area is not None:
            self.scroll_area.hide()

        # set loading animation
        self._start_loading_animation(210, 260, 35, 35)

        self.search_start_t = perf_counter()

        # show stop button instead search button
        self.search_btn.hide()
        self.stop_search_btn.show()

        # create the search object and thread to prevent widgets freeze
        self.my_thread = QThread()
        # create a worker 'long-running task'
        self.worker = Worker(self.search_field.text())
        # move worker to thread
        self.worker.moveToThread(self.my_thread)
        # connect signals and slots
        self.my_thread.started.connect(self.worker.run)
        # set finished connects to thread
        self.worker.finished.connect(lambda: self.update_search_results(self.worker.search_results))
        self.worker.finished.connect(self.on_search_finish)

        self.worker.finished.connect(self.my_thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.my_thread.finished.connect(self.my_thread.deleteLater)
        # start thread
        self.my_thread.start()

    def not_connected(self, widgets_to_clear):
        """ this method for no internet connection window"""

        # clear widgets
        self.clear_widgets(widgets_to_clear)

        self.no_internet_lbl = QLabel('No Internet Connection !', self)
        self.no_internet_lbl.setFont(QFont('sans-serif', 22))
        self.no_internet_lbl.setStyleSheet('color: #9c9a9a;\n'
                                           'border: none;')
        self.no_internet_lbl.adjustSize()
        self.no_internet_lbl.move(65, 100)

        # create no internet logo
        self.no_internet_logo_lbl = QLabel(self)
        self.no_internet_logo_lbl.setStyleSheet('border: none;')
        # loading image
        self.no_internet_logo = QPixmap('resources/Assets/no_internet.png')
        self.no_internet_logo_lbl.setPixmap(self.no_internet_logo)
        self.no_internet_logo_lbl.resize(150, 150)
        self.no_internet_logo_lbl.move(155, 160)

        # create try again button
        self.try_again_button = QPushButton('Try Again', self)
        self.try_again_button.move(160, 350)
        self.try_again_button.setFont(QFont('sans-serif', 16))
        self.try_again_button.adjustSize()
        widgets_to_clear = (self.no_internet_lbl, self.no_internet_logo_lbl, self.try_again_button)
        self.try_again_button.clicked.connect(lambda: self.try_connect(widgets_to_clear))
        self.try_again_button.setCursor(Qt.PointingHandCursor)
        self.try_again_button.setStyleSheet("""
        QPushButton {
            min-width: 100px;
            min-height: 30px;
        
            display: inline-block;
            outline: 0;
            text-align: center;
            border: 1px solid;
            padding: 11px 11px;
  
            color: #202223;
            background-color: #d4d4d4;
            border-radius: 4px;
            font-weight: 400;
            box-shadow: rgba(0, 0, 0, 0.05)
        }
        QPushButton::hover {
            background: #f6f6f7;
            outline: 1px solid transparent;
        }
        
        """)

        # show widgets
        self.no_internet_logo_lbl.show()
        self.no_internet_lbl.show()
        self.try_again_button.show()


class Worker(QObject):
    """
    Worker class for running search algorithms in a separate QThread.

    This class is designed to offload time-consuming search operations
    from the main GUI thread to prevent UI freezing and ensure a responsive interface.

    Typically used with QThread to perform background tasks such as:
    - Username or data enumeration.
    - API calls or web scraping.
    - Long-running computations.

    Signals (optional, if used):
        finished (pyqtSignal): Emitted when the search task is completed.
        progress (pyqtSignal): Emitted to report progress updates.

    Attributes:
        parent (QObject): Optional parent object for this worker instance.

    Methods:
        __init__(self, parent=None):
            Initializes the Worker instance and sets up connections.

        run(self) -> None:
            Executes the search algorithm or background task.

        stop(self) -> None:
            Handles the stop search process event

    """

    finished: pyqtSignal = pyqtSignal()
    search_results: dict = {}

    def __init__(self, username_str: str) -> None:
        super().__init__()
        self.username_str = username_str
        self.search_object = None

    def run(self) -> None:
        """ clear dictionary from the previous search"""
        self.search_results.clear()

        self.search_object = Searcher(self.username_str)
        self.search_results.update(self.search_object.new_search())
        self.finished.emit()

    def stop_search(self) -> None:
        """ This method will handle the stop search"""
        self.search_object.process_killed = True


class AboutWindow(QWidget):
    """
    A QWidget-based window that displays information about the application.

    This window is typically used to show details about the application, such as:
    - Application name and version.
    - Developer or company information.
    - Contact links, credits, and licensing information.

    The window includes:
    - Labels displaying the application's title, developer, version, and copyright.
    - A 'Close' button to hide the window.
    - A 'GitHub' button that opens the application's GitHub repository.

    """

    def __init__(self) -> None:
        super().__init__()

        # Window Setup
        self.setWindowFlags(Qt.WindowStaysOnTopHint | Qt.FramelessWindowHint)
        self.setStyleSheet('background-color: #f5f5f5;')
        self.setWindowTitle('About - Username Searcher')
        self.setWindowIcon(QIcon('images/icon.ico'))
        self.setFixedSize(360, 240)

        # Main Layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Title Section
        title_layout = QHBoxLayout()

        icon_lbl = QLabel(self)
        icon_pixmap = QPixmap('images/icon.ico').scaled(40, 40, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        icon_lbl.setPixmap(icon_pixmap)
        icon_lbl.setFixedSize(40, 40)

        title_text = QLabel('Username Searcher', self)
        title_text.setStyleSheet('color: #222;')
        title_text.setFont(QFont('Segoe UI', 14, QFont.Bold))

        title_layout.addWidget(icon_lbl)
        title_layout.addSpacing(10)
        title_layout.addWidget(title_text)
        title_layout.addStretch()

        # Info Section
        info_layout = QVBoxLayout()
        label_style = 'color: #333; font-family: "Segoe UI"; font-size: 11.5pt;'

        author_lbl = QLabel(f'Author: {_author_}', self)
        author_lbl.setStyleSheet(label_style)

        version_lbl = QLabel(f'Version: {_version_}', self)
        version_lbl.setStyleSheet(label_style)

        release_lbl = QLabel(f'Release Date: {_release_d}', self)
        release_lbl.setStyleSheet(label_style)

        info_layout.addWidget(author_lbl)
        info_layout.addWidget(version_lbl)
        info_layout.addWidget(release_lbl)

        # Spacer
        info_layout.addSpacerItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))

        # Buttons Section
        buttons_layout = QHBoxLayout()

        github_btn = QPushButton('GitHub', self)
        github_btn.setCursor(Qt.PointingHandCursor)
        github_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                background-color: #2ea44f;
                color: white;
                border-radius: 5px;
                font-weight: 600;
                font-family: 'Segoe UI';
                font-size: 10.5pt;
            }
            }
        """)
        github_btn.clicked.connect(lambda: webbrowser.open('https://github.com/aymenbrahimdjelloul/Username-Searcher'))

        close_btn = QPushButton('Close', self)
        close_btn.setCursor(Qt.PointingHandCursor)
        close_btn.setStyleSheet("""
            QPushButton {
                padding: 6px 14px;
                background-color: #e0e0e0;
                color: #333;
                border-radius: 5px;
                font-weight: 600;
                font-family: 'Segoe UI';
                font-size: 10.5pt;
            }
            QPushButton:hover {
                background-color: #cacaca;
            }
        """)
        close_btn.clicked.connect(self.hide)

        buttons_layout.addStretch()
        buttons_layout.addWidget(github_btn)
        buttons_layout.addSpacing(10)
        buttons_layout.addWidget(close_btn)

        # Assemble Layouts
        main_layout.addLayout(title_layout)
        main_layout.addLayout(info_layout)
        main_layout.addLayout(buttons_layout)

        self.old_Pos = None

    # Draggable Window Events
    def mousePressEvent(self, event) -> None:
        """Enables window dragging by capturing mouse press position."""
        self.old_Pos = event.globalPos()

    def mouseMoveEvent(self, event) -> None:
        """Handles the window moving with mouse drag."""
        delta = QPoint(event.globalPos() - self.old_Pos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.old_Pos = event.globalPos()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = App()
    window.show()
    app.exec()
