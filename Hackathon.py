import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QInputDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class Challenges(QWidget):
    def __init__(self):
        super().__init__()

        # window
        self.setWindowTitle('Tasks List')
        self.setMinimumSize(200, 200)  # minimal size of window, чтобы не баловались
        self.resize(500, 400)

        # creation of datebase
        self.create_db()

        # area
        self.vbox = QVBoxLayout()
        self.hbox1 = QHBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.hbox4 = QHBoxLayout()
        self.label_active_tasks = QLabel('Active Tasks', self)  # area for active tasks
        self.label_finished_tasks = QLabel('Finished Tasks', self)  # area for completed tasks
        self.active_tasks = QListWidget()
        self.finished_tasks = QListWidget()
        self.add_line = QLineEdit()

        self.initUI()

    def initUI(self):
        self.set_structure()
        self.create_db()
        self.show()

    def set_structure(self):
        self.create_add_button()
        self.set_qlistwidgets_and_qlabels()
        self.show_active_tasks()

        self.create_buttons()  # buttons on window

    def set_qlistwidgets_and_qlabels(self):
        self.hbox2.addWidget(self.label_active_tasks)
        self.hbox2.addWidget(self.label_finished_tasks)
        self.vbox.addLayout(self.hbox2)

        self.hbox3.addWidget(self.active_tasks)
        self.hbox3.addWidget(self.finished_tasks)
        self.vbox.addLayout(self.hbox3)

        self.setLayout(self.vbox)

        self.active_tasks.setSelectionMode(3)
        self.finished_tasks.setSelectionMode(3)

    def create_add_button(self):
        self.add_line.editingFinished.connect(self.add_task)

        self.vbox.addWidget(self.add_line)

    def create_buttons(self):
        button_finish_task = QPushButton('Finish Task', self)  # button "Finish Task"
        button_del_task = QPushButton('Delete Task', self)  # button "Delete Task"

        self.hbox4.addWidget(button_finish_task)
        self.hbox4.addWidget(button_del_task)

        self.vbox.addLayout(self.hbox4)

    def show_active_tasks(self):
        self.query.exec("""SELECT active FROM active_tasks""")
        while self.query.next():
            self.active_tasks.addItem(self.query.value(0))

    def add_task(self):
        new_active_task = self.add_line.text()
        self.add_line.clear()
        if new_active_task != '':
            self.query.prepare("""INSERT INTO active_tasks (active) VALUES (?)""")
            self.query.addBindValue(new_active_task)
            self.query.exec()

            self.active_tasks.addItem(new_active_task)

    def create_db(self):
        self.db = QSqlDatabase.addDatabase("QSQLITE")
        self.db.setDatabaseName("Hackathon_Molecule_group.sqlite")

        if not self.db.open():
            print("Database can't be opened", self.db.lastError())

        self.query = QSqlQuery()
        self.query.exec("""CREATE TABLE IF NOT EXISTS active_tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        active VARCHAR(255) NOT NULL
        )""")

        self.query.exec("""CREATE TABLE IF NOT EXISTS finished_tasks(
        id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL,
        finished VARCHAR(255) NOT NULL
        )""")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    example = Challenges()
    sys.exit(app.exec_())
