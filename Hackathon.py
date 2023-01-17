import sys
from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QInputDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, QLineEdit, QListWidget
from PyQt5.QtCore import Qt
from PyQt5.QtSql import QSqlDatabase, QSqlQuery


class Challenges(QWidget):
    def __init__(self):
        super().__init__()

        # window
        self.setWindowTitle('Tasks List')
        self.setMinimumSize(220, 200)  # minimal size of window, чтобы не баловались
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

        self.window_color = "#5BAF8F"  # color of window
        self.label_color = "#FFC0CB"  # color of label
        # self.setStyleSheet(f"background-color: {self.window_color}")  # how change window color
        self.label_active_tasks.setStyleSheet(f"background-color: {self.label_color}")  # how change label color
        self.active_tasks.setStyleSheet("background-color: #00FFFF")
        self.add_line.setStyleSheet("background-color: #00FFFF;"
                                    "font-family: Bernadette")  # how change font

        self.initUI()

    def initUI(self):
        self.set_structure()
        self.create_db()
        self.show()

    def set_structure(self):
        self.create_add_button()
        self.set_qlistwidgets_and_qlabels()
        self.create_buttons()  # buttons on window

        self.show_active_tasks()
        self.show_finished_tasks()
        self.settings_of_lists_selections()


    def settings_of_lists_selections(self):
        self.active_tasks.setSelectionMode(3)
        self.finished_tasks.setSelectionMode(3)

        self.active_tasks.doubleClicked.connect(self.turn_the_task)
        self.finished_tasks.doubleClicked.connect(self.turn_the_task)

        self.active_tasks.itemSelectionChanged.connect(self.clear_selection)
        self.finished_tasks.itemSelectionChanged.connect(self.clear_selection)

    def set_qlistwidgets_and_qlabels(self):
        self.hbox2.addWidget(self.label_active_tasks)
        self.hbox2.addWidget(self.label_finished_tasks)
        self.vbox.addLayout(self.hbox2)

        self.hbox3.addWidget(self.active_tasks)
        self.hbox3.addWidget(self.finished_tasks)
        self.vbox.addLayout(self.hbox3)

        self.setLayout(self.vbox)


    def create_add_button(self):
        placeholder_text = 'Write here to add a Task'
        self.add_line.setPlaceholderText(placeholder_text)  # Adding translucent (полупрозрачный) text to add_line

        self.add_line.editingFinished.connect(self.add_task)
        self.vbox.addWidget(self.add_line)

    def create_buttons(self):
        self.button_finish_task = QPushButton('Turn', self)  # button "Finish Task"
        self.button_del_task = QPushButton('Delete Task', self)  # button "Delete Task"
        self.button_del_task.clicked.connect(self.turn_the_task)
        self.button_finish_task.clicked.connect(self.turn_the_task)

        self.hbox4.addWidget(self.button_finish_task)
        self.hbox4.addWidget(self.button_del_task)
        self.vbox.addLayout(self.hbox4)

    def clear_selection(self):
        sender = self.sender()
        if sender is self.finished_tasks:
            self.active_tasks.clearSelection()
        else:
            self.finished_tasks.clearSelection()

    def show_active_tasks(self):
        self.query.exec("""SELECT active FROM active_tasks""")
        self.local_list_of_active_tasks = []
        while self.query.next():
            value = self.query.value(0)
            self.active_tasks.addItem(value)
            self.local_list_of_active_tasks.append(value)

    def show_finished_tasks(self):
        self.query.exec("""SELECT finished FROM finished_tasks""")
        self.local_list_of_finished_tasks = []
        while self.query.next():
            value = self.query.value(0)
            self.finished_tasks.addItem(value)
            self.local_list_of_finished_tasks.append(value)

    def add_task(self):
        new_active_task = self.add_line.text()
        self.add_line.clear()
        if new_active_task != '':
            if new_active_task not in self.local_list_of_active_tasks \
                    and new_active_task not in self.local_list_of_finished_tasks:
                self.local_list_of_active_tasks.append(new_active_task)

                self.query.prepare("""INSERT INTO active_tasks (active) VALUES (?)""")
                self.query.addBindValue(new_active_task)
                self.query.exec()

                self.active_tasks.addItem(new_active_task)

    def turn_the_task(self):
        indexes_of_finished_selected_items = self.finished_tasks.selectedIndexes()
        indexes_of_active_selected_items = self.active_tasks.selectedIndexes()
        if len(indexes_of_finished_selected_items) > 0:
            for i in indexes_of_finished_selected_items[-1::-1]:
                item = self.finished_tasks.takeItem(i.row()).text()
                self.active_tasks.addItem(item)
                self.query.prepare("""INSERT INTO active_tasks (active) VALUES (?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_active_tasks.append(item)

                self.query.prepare("""DELETE FROM finished_tasks WHERE finished=(?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_finished_tasks.remove(item)
        if len(indexes_of_active_selected_items) > 0:
            for i in indexes_of_active_selected_items[-1::-1]:
                item = self.active_tasks.takeItem(i.row()).text()
                self.finished_tasks.addItem(item)
                self.query.prepare("""INSERT INTO finished_tasks (finished) VALUES (?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_finished_tasks.append(item)

                self.query.prepare("""DELETE FROM active_tasks WHERE active=(?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_active_tasks.remove(item)

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
    app.setStyle('Fusion')  # Application style, you can use "Windows", "windowsvista" or "Fusion",
    # by default, it is "windowsvista"
    example = Challenges()
    sys.exit(app.exec_())
