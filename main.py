from PyQt5.QtCore import QSize
from PyQt5 import QtWidgets, QtCore, QtGui
import qtawesome as qta
from PyQt5 import uic
import qdarkstyle
import sys
import os
import threading
from worker import do_crawl_corpor


from corporationwiki import CorporSearch

qtCreatorFile = os.path.join(os.path.dirname(__file__), 'src', 'main.ui')
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)


class LeadGenerator(QtWidgets.QDialog, Ui_MainWindow):
    checkboxStatus = ""
    status = 0

    def __init__(self):
        QtWidgets.QDialog.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        self._setup_icons()
        self.make_connections()
        self.corpChkBox.setChecked(True)
        self.t1 = None
        self._setProgress(0)
        
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
                'truepeoplesearch': [
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
            _enabled_option = text if text == 'truepeoplesearch' else 'Otherwise'
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
        
        #Get Search Key
        searchKey = self.keyLineEdit.text()

        if searchKey == "" :
            QtWidgets.QMessageBox.about(self, "Warning", "Please insert Search Key")

        else:
            self._set_icon(self.togStatePushBtn, 'mdi.stop', 'Stop')

            if self.checkboxStatus == "corporationwiki" :
                print(self.logTextEdit)
                self.t1 = threading.Thread(target=do_crawl_corpor, args=(searchKey, self.addLogMessage, ))
                self.t1.start()            
            elif self.checkboxStatus == "truepeoplesearch" :
                # TruepeopleSearch(searchKey)
                print("print")
        
        # self._setProgress(50)

    def _reset_task(self):
        sender = self.sender()
        print('{text} Button Clicked'.format(text=sender.text()))
        self._set_icon(self.togStatePushBtn, 'mdi.play', 'Play')
        self._setProgress(0)

    def _toggle_task(self):
        sender = self.sender()

        if self.t1:
            self.t1.join()

        print('{text} Button Clicked'.format(text=sender.text()))

        if sender.text() == 'Play':
            self._set_icon(sender, 'mdi.stop', 'Stop')
        elif sender.text() == 'Stop':
            self._set_icon(sender, 'mdi.play', 'Play')
            self._setProgress(100)

    def _setProgress(self, percent: int):
        self.progressBar.setValue(percent)

        
    def make_connections(self):
        # Check Boxes
        self.corpChkBox.toggled.connect(self._handle_chk_box)
        self.peopleChkBox.toggled.connect(self._handle_chk_box)
        self.peopleCorpChkBox.toggled.connect(self._handle_chk_box)
        # Push Button
        self.resetPushBtn.clicked.connect(self._reset_task)
        self.searchPushBtn.clicked.connect(self._start_task)
        self.togStatePushBtn.clicked.connect(self._toggle_task)

        # Search Key
        # self.keyLineEdit.textChanged.connect(self._search_key)

    def addLogMessage(self, message):
        self.logTextEdit.append(message)
        print(self.status)

    
        self.status = self.status + 1
        self._setProgress(self.status)
        # self.emit(QtCore.SIGNAL("VALUE"), self.status)
        # self.connect(do_crawl_corpor, QtCore.SIGNAL("VALUE"), self._setProgress)







if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    app.setStyleSheet(qdarkstyle.load_stylesheet_pyqt5())
    window = LeadGenerator()
    window.setWindowTitle('Lead Generator')
    window.show()
    sys.exit(app.exec_())
