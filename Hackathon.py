import sys
from PyQt5.QtWidgets import QMainWindow, QApplication


class Challenges(QMainWindow):
    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = Challenges()
    sys.exit(app.exec_())
