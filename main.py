from corpor_truepeople import Copor_TrueSearch
from truepeoplesearh import TruepeopleSearch
from corporationwiki import CorporSearch
from PyQt5.QtCore import QSize
from threading import Thread
from PyQt5 import QtWidgets
import qtawesome as qta
from PyQt5 import uic
import qdarkstyle
import sys
import os

qtCreatorFile = os.path.join(os.getcwd(), 'src', 'main.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class LeadGenerator(QtWidgets.QDialog, Ui_MainWindow):
    checkboxStatus = ""

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self._setup_icons()
        self.make_connections()
        self.corpChkBox.setChecked(True)
        self.t1 = None  # CorporationWiki Search
        self.t2 = None  # Truepoeple Search
        self.t3 = None  # Corporation -> Truepeople Search

        self.pause_handler = None
        self._setProgress(0)

        self.setStyleSheet(
            "QLabel#label {font: bold 20px;}"
            "QGroupBox {font: bold 14px;}"
            "QCheckBox {font: 12px;}"
            "QTextEdit#logTextEdit {font: 15px;}"
        )

    def _set_icon(self, widget: QtWidgets.QWidget, icon_name: str, text: str = None):
        widget.setIcon(qta.icon(icon_name, color='white'))
        self.searchPushBtn.setIconSize(QSize(20, 20))
        if text:
            widget.setText(text)

    def _setup_icons(self):
        self._set_icon(self.resetPushBtn, 'mdi.reload')
        self._set_icon(self.togStatePushBtn, 'mdi.play')
        self._set_icon(self.searchPushBtn, 'mdi.account-search')

    def _handle_chk_box(self, state: bool):
        if state:
            _widgets_by_option = {
                'Truepeoplesearch.com': [
                    self.nameLabel,
                    self.nameLineEdit,
                    self.adrLabel,
                    self.adrLineEdit,
                ],
                'Otherwise': [
                    self.keyLabel,
                    self.keyLineEdit
                ]
            }

            sender = self.sender()
            text = sender.text()
            self.checkboxStatus = text
            print(text, 'Selected')
            _enabled_option = text if text == 'Truepeoplesearch.com' else 'Otherwise'
            for option, widgets in _widgets_by_option.items():
                for widget in widgets:
                    if option == _enabled_option:
                        widget.show()
                    else:
                        widget.hide()
            self.resize(self.width(), self.minimumHeight())

    def _start_task(self):
        sender = self.sender()
        print('{text} Button Clicked'.format(text=sender.text()))

        # Corporationwiki
        searchKey = self.keyLineEdit.text()
        # TruepeopleSearch
        searchName = self.nameLineEdit.text()
        searchAddress = self.adrLineEdit.text()

        self._set_icon(self.togStatePushBtn, 'mdi.stop', 'Stop')

        if self.checkboxStatus == "Corporationwiki.com":
            if searchKey == "":
                QtWidgets.QMessageBox.about(self, "Warning", "Please insert Search Key")
            else:
                print(self.logTextEdit)
                self.t1 = self.do_crawl_corpor(searchKey)

        elif self.checkboxStatus == "Truepeoplesearch.com":
            if searchKey == "" and (searchName == "" and searchAddress == ""):
                QtWidgets.QMessageBox.about(self, "Warning", "Please insert `Name` and `Address`")
            else:
                print(searchName, searchAddress)
                self.t2 = self.do_crawl_truepeople(searchName, searchAddress)

        elif self.checkboxStatus == "Corporationwiki → Truepeoplesearch":
            if searchKey == "":
                QtWidgets.QMessageBox.about(self, "Warning", "Please insert `Search Key`")
            else:
                self.t3 = self.do_crawl_corpor_true(searchKey)

        self._set_icon(self.togStatePushBtn, 'mdi.stop', 'Stop')

    def _reset(self):
        if self.t1:
            self.t1.logcallback.disconnect()
            self.t1.driver.close()
            self.t1.driver.quit()
            self.t1.driver = None

            self.t1 = None

        if self.t2:
            self.t2.logcallback.disconnect()
            self.t2.driver.close()
            self.t2.driver.quit()
            self.t2.driver = None

            self.t2.driver1.close()
            self.t2.driver1.quit()
            self.t2.driver1 = None

            self.t2.driver2.close()
            self.t2.driver2.quit()
            self.t2.driver2 = None

            self.t2 = None

        if self.t3:
            self.t3.logcallback.disconnect()
            self.t3.driver.close()
            self.t3.driver.quit()
            self.t3.driver = None

            self.t3.driver1.close()
            self.t3.driver1.quit()
            self.t3.driver1 = None

            self.t3.driver2.close()
            self.t3.driver2.quit()
            self.t3.driver2 = None

            self.t3.driver3.close()
            self.t3.driver3.quit()
            self.t3.driver3 = None

            self.t3 = None
        self.logTextEdit.append('_____________________Reset Done')

    def _reset_task(self):
        self.logTextEdit.append('_____________________Resetting (Please Wait...)')
        worker = Thread(target=self._reset)
        worker.start()

        sender = self.sender()
        print('{text} Button Clicked'.format(text=sender.text()))
        self._set_icon(self.togStatePushBtn, 'mdi.play', 'Play')
        self._setProgress(0)

        if self.checkboxStatus == "Corporationwiki.com" or self.checkboxStatus == "Corporationwiki → Truepeoplesearch":
            self.keyLineEdit.setText(None)

        elif self.checkboxStatus == "Truepeoplesearch.com":
            self.nameLineEdit.setText(None)
            self.adrLineEdit.setText(None)

    def _toggle_task(self):
        sender = self.sender()
        print('{text} Button Clicked'.format(text=sender.text()))
        if not self.t1 and not self.t2 and not self.t3:
            self.logTextEdit.append('No Task Running')
            return
        if sender.text() == 'Play':
            self.logTextEdit.append('_____________________Resuming Task')
            if self.t1:
                # Resuming Task
                self.t1.paused = False
            elif self.t2:
                self.t2.paused = False
            elif self.t3:
                self.t3.paused = False

            self._set_icon(sender, 'mdi.stop', 'Stop')

        elif sender.text() == 'Stop':
            self._set_icon(sender, 'mdi.play', 'Play')
            self.logTextEdit.append('_____________________Pausing Task')
            if self.t1:
                # Pausing Task
                self.t1.paused = True
            elif self.t2:
                self.t2.paused = True
            elif self.t3:
                self.t3.paused = True

    def _exit_task(self):
        # if self.t1:
        #     self.t1.driver.quit()
        #     self.t1.driver = None
        #     self.t1 = None

        # elif self.t2:
        #     self.t2.driver.quit()
        #     self.t2.driver = None
        #     self.t2.driver1.quit()
        #     self.t2.driver1 = None
        #     self.t2.driver2.quit()
        #     self.t2.driver2 = None
        #     self.t2 = None
        # (Change to fix close crash)
        self.logTextEdit.append('_____________________Closing (Please Wait...)')
        t = Thread(target=self._reset)
        t.setDaemon(True)
        t.start()
        from PyQt5.QtCore import QCoreApplication
        while t.is_alive():
            QCoreApplication.processEvents()
        self.close()


    def _setProgress(self, percent: int):
        self.progressBar.setValue(percent)

    def do_crawl_corpor(self, keyword):
        # print("param name: {}".format(keyword))
        # print("param log callback: {}".format(self.addLogMessage))
        corporSearch = CorporSearch(keyword)
        corporSearch.logcallback.connect(self.addLogMessage)
        corporSearch.start()
        return corporSearch

    def do_crawl_truepeople(self, keyName, keyAddress):
        # print("param name: {}".format(keyName), "param address: {}".format(keyAddress))
        # print("param log callback: {}".format(self.addLogMessage))
        truepeopleSearch = TruepeopleSearch(keyName, keyAddress)
        truepeopleSearch.logcallback.connect(self.addLogMessage)
        truepeopleSearch.start()
        return truepeopleSearch

    def do_crawl_corpor_true(self, keyword):
        corpor_trueSearch = Copor_TrueSearch(keyword)
        corpor_trueSearch.logcallback.connect(self.addLogMessage)
        corpor_trueSearch.start()
        return corpor_trueSearch

    def make_connections(self):
        # Check Boxes
        self.corpChkBox.toggled.connect(self._handle_chk_box)
        self.peopleChkBox.toggled.connect(self._handle_chk_box)
        self.peopleCorpChkBox.toggled.connect(self._handle_chk_box)
        # Push Button
        self.resetPushBtn.clicked.connect(self._reset_task)
        self.searchPushBtn.clicked.connect(self._start_task)
        self.togStatePushBtn.clicked.connect(self._toggle_task)
        # Close Button
        # self.buttonBox.clicked.connect(self._exit_task)
        self.closePushBtn.clicked.connect(self._exit_task)

    def addLogMessage(self, message, status):
        self.logTextEdit.append(message)
        self._setProgress(status)


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = LeadGenerator()
    window.setWindowTitle('Lead Generator')
    window.show()
    sys.exit(app.exec_())
