import sys
import time
from PyQt5.QtWidgets import QDialog
from PyQt5.QtCore import Qt, pyqtSignal, QObject
from PyQt5.QtGui import QFont
from PyQt5 import QtWidgets
from PyQt5 import uic
from funcs import *
from ctypes.wintypes import MSG
import threading


class CustomSignal(QObject):
    box = pyqtSignal(str, object)


class HomeWin(QDialog):
    def __init__(self):
        super(HomeWin, self).__init__()
        uic.loadUi("./home.ui", self)

        self.setWindowOpacity(0.9)
        self.setAutoFillBackground(False)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.move(240, 800)  # 显示位置

        font = QFont("微软雅黑", 11)
        self.textEdit.setFont(font)

        self.textEdit.setText("")  # 初始编辑框内容
        self.groupBox.setVisible(False)

        self.signal = CustomSignal()
        self.signal.box.connect(self.signal_cb)
        # 子线程更改控件不支持,改用信号传递
        threading.Thread(target=self.dP).start()#提示标签

    def dP(self):
        prefix = "请求中"
        while True:
            self.signal.box.emit("dTip", prefix + ".")
            time.sleep(0.25)
            self.signal.box.emit("dTip", prefix+"..")
            time.sleep(0.25)
            self.signal.box.emit("dTip", prefix + "...")
            time.sleep(0.25)

    def nativeEvent(self, eventType, msg):
        message = MSG.from_address(msg.__int__())
        if message.message == 786:
            if message.wParam == 112:  # F1 - 切换可视状态 [o]
                self.setVisible(not self.isVisible())
            elif message.wParam == 113:  # F2 - 中文翻译为其他语言 []
                ...
            elif message.wParam == 114:  # F3 - 固定区域截图 []
                #bin = null() #固定区域截图
                #threading.Thread(target=self.click_f4,args=(bin,)).start()
                ...
            elif message.wParam == 115:  # F4 - 手动选区截图 [o]
                threading.Thread(target=self.click_f4,args=(None,)).start()
            elif message.wParam == 35:  # End - 退出
                os._exit(0)
        return (False, 0)

    def complete(self):
        self.ocr = BaiduApi("baidu id","baidu key") # 改为自己的
        self.ai = ChatGPT("hosts","token") # 改为自己的
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

    def click_f4(self,img=None):
        if img==None:
            sta, bin = screenshot()
        else:
            sta, bin = (True,img)
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

            def cb(value):
                self.signal.box.emit("editBox", value)

            text = self.ai.send("翻译为简体中文", text, cb)

            self.signal.box.emit("editBox", text)

            self.signal.box.emit("tip", False)


class ShowMyWin:
    app = QtWidgets.QApplication(sys.argv)
    home = HomeWin()
    home.show()
    home.complete()
    sys.exit(app.exec())


if __name__ == '__main__':
    ShowMyWin()