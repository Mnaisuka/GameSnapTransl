import json
import sys
import time
from PyQt5.QtWidgets import QDialog, QInputDialog
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5 import uic
from funcs import *
from popup import *
from ctypes.wintypes import MSG
import threading

class CustomSignal(QObject):
    box = pyqtSignal(str, object)


class HomeWin(QDialog):
    def __init__(self):
        super(HomeWin, self).__init__()
        uic.loadUi("./home.ui", self)

        self.popup = None

        self.setWindowOpacity(0.9)
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.move(240, 800)  # 显示位置

        font = QFont()
        font.setFamily("微软雅黑")
        font.setPointSize(11)
        self.textEdit.setFont(font)

        self.groupBox.setVisible(False)

        self.signal = CustomSignal()
        self.signal.box.connect(self.signal_cb)
        threading.Thread(target=self.dP).start()

    def dP(self):
        prefix = "请求中"
        while True:
            self.signal.box.emit("dTip", prefix + ".")
            time.sleep(0.5)
            self.signal.box.emit("dTip", prefix+"..")
            time.sleep(0.5)
            self.signal.box.emit("dTip", prefix + "...")
            time.sleep(0.5)

    def nativeEvent(self, eventType, msg):
        message = MSG.from_address(msg.__int__())
        if message.message == 786:
            if message.wParam == 112:
                ...
            elif message.wParam == 113:
                if self.popup == None:
                    self.popup = popup(self.chatgpt)
                    self.popup.show()
                else:
                    if self.popup.isVisible():
                        self.popup.savePos = self.popup.pos()
                        self.popup.hide()
                    else:
                        self.popup.move(self.popup.savePos)  
                        self.popup.show()
            elif message.wParam == 114:
                left, top, width, height = (45, 418, 450, 238)
                threading.Thread(target=self.ocr_tl, args=(
                    (left, top, left+width, top+height),)).start()
            elif message.wParam == 115:
                threading.Thread(target=self.ocr_tl, args=(None,)).start()
            elif message.wParam == 36:
                self.setVisible(not self.isVisible())
            elif message.wParam == 35:
                os._exit(0)
        return (False, 0)

    def complete(self):
        self.ocr = BaiduApi(Config.baidu_id, Config.baidu_key)
        self.chatgpt = ChatGPT(Config.openai_base, Config.openai_token)
        self.hwnd = int(self.winId())  # 取窗口句柄
        block_focus(self.hwnd)  # 无焦点模式
        bind_hotkey(self.hwnd, [112, 113, 114, 115, 35])  # 注册热键

    def signal_cb(self, type, msg):
        if type == "editBox":
            self.textEdit.setText(msg)
        elif type == "tip":
            self.groupBox.setVisible(msg)
        elif type == "dTip":
            self.label.setText(msg)

    def ocr_tl(self, bobx):
        sta, bin = screenshot(bobx)
        if sta == True:
            self.signal.box.emit("tip", True)
            data = self.ocr.accurate(bin)
            text = None
            for _ in data['words_result']:
                if text == None:
                    text = _['words']
                else:
                    text = text + "\n" + _['words']
            self.ogText = text
            self.signal.box.emit("editBox", text)

            def cb(v):
                self.signal.box.emit("editBox", v)

            text = self.chatgpt.send(Config.openai_prompt, text, cb)

            self.signal.box.emit("editBox", text)

            self.signal.box.emit("tip", False)


class ConfigRead():
    def __init__(self):
        with open('config.json', 'r', encoding='utf-8') as file:
            items = json.load(file)
        for item in items:
            setattr(self, item, items[item])

        search = [
            {
                "name": "openai_base",
                "default": None
            },
            {
                "name": "openai_token",
                "default": None
            },
            {
                "name": "openai_prompt",
                "default": None
            },
            {
                "name": "baidu_id",
                "default": None
            },
            {
                "name": "baidu_key",
                "default": None
            }
        ]

        for item in search:
            if not hasattr(self, item['name']):
                print("缺少参数", item)


Config = ConfigRead()


class ShowMyWin:
    app = QtWidgets.QApplication(sys.argv)
    home = HomeWin()
    home.show()
    home.complete()
    sys.exit(app.exec())


if __name__ == '__main__':
    ShowMyWin()
    