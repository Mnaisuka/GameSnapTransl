import threading
from PyQt5.QtWidgets import QDialog
from PyQt5 import uic
from PyQt5.QtCore import Qt, pyqtSignal, QObject


class CustomSignal(QObject):
    box = pyqtSignal(str, object)


class popup(QDialog):
    def __init__(self, ai):
        super(popup, self).__init__()
        uic.loadUi("./popup.ui", self)

        self.ai = ai

        self.translButton.clicked.connect(self.onButtonClick)

        self.outputFrame.setAlignment(Qt.AlignCenter)

        self.signal = CustomSignal()
        self.signal.box.connect(self.signal_cb)

    def signal_cb(self, type, msg):
        if type == "output":
            self.outputFrame.setText(msg)

    def onButtonClick(self):
        threading.Thread(target=self.startTransl).start()

    def startTransl(self):
        text = self.inputBox.toPlainText()

        def cb(v):
            self.signal.box.emit("output", "译文:" + v)
        text = self.ai.send("Playing the Translation API,Overwatch,Translation into English", text,
                            cb)  # 使用GPT4模型

        prefix = "译文:" + text

        def cb(v):
            self.signal.box.emit("output", prefix+"\n校正:" + v)
        correction = self.ai.send(
            "Overwatch,Translation into Chinese", text, cb, max_tk=150)  # 使用GPT3模型

        format = f"译文:{text}\n校正:{correction}"
        
        self.signal.box.emit("output", format)