import sys
from PyQt5.QtWidgets import QMainWindow, QApplication, QInputDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, \
    QLineEdit
from PyQt5.QtCore import Qt


class Challenges(QMainWindow):
    def __init__(self):
        super().__init__()

        # window
        self.setWindowTitle('TasksList')
        self.setMinimumSize(200, 200)  # minimal size of window, чтобы не баловались
        self.resize(300, 300)

        # area
        self.vbox = QVBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.label_active_tasks = QLabel('Active Tasks', self)  # area for active tasks
        self.label_finished_tasks = QLabel('Finished Tasks', self)  # area for completed tasks

        self.initUI()

    def initUI(self):
        self.set_structure()
        self.show()

    def set_structure(self):
        self.create_buttons()  # buttons on window
        self.setLayout(self.vbox)

    def create_buttons(self):
        button_add_task = QPushButton('Add Task', self)  # button "Add Task"
        button_finish_task = QPushButton('Finish Task', self)  # button "Finish Task"
        button_del_task = QPushButton('Delete Task', self)  # button "Delete Task"

        self.hbox1.addWidget(button_add_task)
        # self.vbox.addLayout(self.hbox1)

        self.hbox1.addWidget(button_finish_task)
        # self.vbox.addLayout(self.hbox2)

        self.hbox1.addWidget(button_del_task)
        self.vbox.addLayout(self.hbox1)


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = Challenges()
    sys.exit(app.exec_())
