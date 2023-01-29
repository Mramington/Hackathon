import sys
from PyQt5.QtWidgets import QWidget, QApplication, QMessageBox, QVBoxLayout, QHBoxLayout, QPushButton, \
    QLabel, QLineEdit, QListWidget, QSizePolicy, QStyle
from PyQt5.QtSql import QSqlDatabase, QSqlQuery
from PyQt5.QtGui import QIcon
import css


def row_if_index_list(lst):
    answer = []
    for i in lst:
        answer.append(i.row())
    return answer


class Challenges(QWidget):
    def __init__(self):
        super().__init__()

        # window
        self.setWindowTitle('Tasks List')
        self.setMinimumSize(330, 200)  # minimal size of window, чтобы не баловались
        self.resize(500, 400)

        # creation of database
        self.create_db()

        # area
        self.vbox = QVBoxLayout()
        self.vbox1 = QVBoxLayout()
        self.hbox2 = QHBoxLayout()
        self.hbox3 = QHBoxLayout()
        self.hbox4 = QHBoxLayout()
        self.label_active_tasks = QLabel('Active Tasks', self)  # area for active tasks
        self.label_empty = QLabel('', self)
        self.label_finished_tasks = QLabel('Finished Tasks', self)  # area for completed tasks
        self.active_tasks = QListWidget()
        self.finished_tasks = QListWidget()
        self.add_line = QLineEdit()

        self.initUI()

    def initUI(self):
        self.set_structure()
        self.create_db()
        self.design()
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

    def keyPressEvent(self, e):
        key = e.key()
        if key == 16777223:
            self.delete_dialog()
        elif key == 16777220:
            self.turn_the_task()

    def set_qlistwidgets_and_qlabels(self):
        self.hbox2.addWidget(self.label_active_tasks)
        self.hbox2.addWidget(self.label_empty)
        self.hbox2.addWidget(self.label_finished_tasks)
        self.vbox.addLayout(self.hbox2)

        self.hbox3.addWidget(self.active_tasks)

        self.hbox3.addLayout(self.vbox1)

        self.hbox3.addWidget(self.finished_tasks)
        self.vbox.addLayout(self.hbox3)

        self.setLayout(self.vbox)

    def create_add_button(self):
        placeholder_text = 'Add'
        self.add_line.setPlaceholderText(placeholder_text)  # Adding translucent (полупрозрачный) text to add_line

        self.add_line.editingFinished.connect(self.add_task)
        self.vbox.addWidget(self.add_line)

    def create_buttons(self):
        self.button_del_task = QPushButton('Delete', self)  # button "Delete Task"
        self.button_turn_task = QPushButton('Turn', self)  # button "Finish Task"
        self.button_turn_task.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        self.button_del_task.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)

        self.button_turn_task.clicked.connect(self.turn_the_task)
        self.button_del_task.clicked.connect(self.delete_dialog)

        self.vbox1.addWidget(self.button_turn_task)
        self.vbox1.addWidget(self.button_del_task)

    def clear_selection(self):
        sender = self.sender()
        if sender is self.finished_tasks:
            self.active_tasks.clearSelection()
        else:
            self.finished_tasks.clearSelection()

    def show_active_tasks(self):
        self.local_list_of_active_tasks = []
        self.query.exec("""SELECT active FROM active_tasks""")
        while self.query.next():
            value = self.query.value(0)
            self.active_tasks.addItem(value)
            self.local_list_of_active_tasks.append(value)

    def show_finished_tasks(self):
        self.local_list_of_finished_tasks = []
        self.query.exec("""SELECT finished FROM finished_tasks""")
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

    def delete_dialog(self):
        ret = QMessageBox.question(self, 'Warning', "Are you sure?",
                                   QMessageBox.Yes | QMessageBox.No)

        if ret == QMessageBox.Yes:
            print('Button QMessageBox.Yes clicked.')
            self.delete_the_task()
        else:
            print('Button QMessageBox.No clicked.')

    def turn_the_task(self):
        indexes_of_finished_selected_items = self.finished_tasks.selectedIndexes()
        indexes_of_finished_selected_items = row_if_index_list(indexes_of_finished_selected_items)
        indexes_of_finished_selected_items.sort()
        indexes_of_active_selected_items = self.active_tasks.selectedIndexes()
        indexes_of_active_selected_items = row_if_index_list(indexes_of_active_selected_items)
        indexes_of_active_selected_items.sort()
        if len(indexes_of_finished_selected_items) > 0:
            for i in indexes_of_finished_selected_items[-1::-1]:
                item = self.finished_tasks.takeItem(i).text()
                self.active_tasks.addItem(item)
                self.query.prepare("""INSERT INTO active_tasks (active) VALUES (?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_active_tasks.append(item)

                self.delete_from_finished_tasks(item)

        if len(indexes_of_active_selected_items) > 0:
            for i in indexes_of_active_selected_items[-1::-1]:
                item = self.active_tasks.takeItem(i).text()
                self.finished_tasks.addItem(item)
                self.query.prepare("""INSERT INTO finished_tasks (finished) VALUES (?)""")
                self.query.addBindValue(item)
                self.query.exec()
                self.local_list_of_finished_tasks.append(item)
                print("first")

                self.delete_from_active_tasks(item)
                print("second")

    def delete_the_task(self):
        indexes_of_finished_selected_items = self.finished_tasks.selectedIndexes()
        indexes_of_finished_selected_items = row_if_index_list(indexes_of_finished_selected_items)
        indexes_of_finished_selected_items.sort()
        indexes_of_active_selected_items = self.active_tasks.selectedIndexes()
        indexes_of_active_selected_items = row_if_index_list(indexes_of_active_selected_items)
        indexes_of_active_selected_items.sort()
        if len(indexes_of_finished_selected_items) > 0:
            for i in indexes_of_finished_selected_items[-1::-1]:
                item = self.finished_tasks.takeItem(i).text()
                self.delete_from_finished_tasks(item)

        if len(indexes_of_active_selected_items) > 0:
            for i in indexes_of_active_selected_items[-1::-1]:
                item = self.active_tasks.takeItem(i).text()
                self.delete_from_active_tasks(item)

    def delete_from_finished_tasks(self, item):
        self.query.prepare("""DELETE FROM finished_tasks WHERE finished=(?)""")
        self.query.addBindValue(item)
        self.query.exec()
        self.local_list_of_finished_tasks.remove(item)

    def delete_from_active_tasks(self, item):
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

    def design(self):
        self.window_color = "#22222e"  # color of window
        self.label_color = "#fb5b5d"  # color of label
        self.add_color = "#107c10"
        self.list_color = "#414141"
        self.setWindowIcon(QIcon('android.png'))
        self.setStyleSheet(f"background-color: {self.window_color};"
                           "font-size: 16px")  # how change window color
        self.label_active_tasks.setStyleSheet(
            f"background-color: {self.label_color};"
            "border-radius: 5px;"
            f"border: 2px solid {self.label_color};"
            "padding: 1px 1px;"
            "min-height: 15px")  # how change label color
        self.label_empty.setStyleSheet(f"max-width: {self.button_turn_task.frameGeometry().width()//2+5}px;"
                                       f"min-width: {self.button_turn_task.frameGeometry().width()//2+5}px")
        self.label_finished_tasks.setStyleSheet(
            f"background-color: {self.label_color};"
            "border-radius: 5px;"
            f"border: 2px solid {self.label_color};"
            "padding: 1px 1px;"
            "min-height: 15px")
        self.add_line.setStyleSheet(
            "font-family: Bernadette;"
            "border-radius: 5px;"
            f"border: 2px solid {self.label_color};"
            "padding: 1px 1px;"
            "color: white")  # how change font

        self.button_turn_task.setStyleSheet(css.button_turn_task)

        self.button_del_task.setStyleSheet("""QPushButton {
                                               background-color: #fb5b5d;
                                               border: 2px solid;
                                               border-radius: 5px;
                                               border: 2px solid;
                                               padding: 1px 1px;
                                               min-height: 35px;
                                               max-height: 60px;
                                               min-width: 50px;
                                               max-width: 50px
                                               }

                                               QPushButton:hover {
                                               background-color: red;
                                               color: #fff;    
                                               border: 1px solid white;
                                               text-decoration: None;
                                               border: 2px solid;
                                               border-radius: 5px;
                                               border: 2px solid;
                                               padding: 1px 1px;
                                               background-color: grey
                                                }
                                               
                                               QPushButton:hover:pressed {
                                               background-color: #f49354;
                                               color: black;}
                                               QPushButton:focus {
                                               border: 1px solid blue}
                                            }"""
                                           )
        # Active Tasks
        self.active_tasks.setStyleSheet("""QListWidget {background-color: #22222e;
                                        border-radius: 5px;
                                        border: 3px solid #fb5b5d;
                                        padding: 1px 1px;
                                        min-height: 35px;
                                        color: white;}
                                        QListWidget:focus{
                                        border: 1px solid blue}""")
        # self.active_tasks.item().setStyleSheet()
        # Finished Tasks
        self.finished_tasks.setStyleSheet("""QListWidget {background-color: #22222e;
                                          border-radius: 5px;
                                          border: 3px solid #fb5b5d;
                                          padding: 1px 1px;
                                          min-height: 35px;
                                          color: white}
                                          QListWidget:focus{
                                          border: 1px solid blue}""")


if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyleSheet("""
                        QMessageBox {
                            background-color: rgb(51, 51, 51);
                        }
                        QMessageBox QLabel {
                            color: #919197;
                        }
                        QMessageBox QPushButton {
                            color: #919197;
                           background-color: #fb5b5d;
                           border: 2px solid;
                           border-radius: 5px;
                           border: 2px solid #919197;
                           padding: 1px 1px;
                           min-width: 50px;
                           max-width: 50px;
                        }

                        QMessageBox QPushButton:hover {
                           background-color: red;
                           color: #fff;
                           border: 1px solid white;
                           text-decoration: None;
                           border: 2px solid;
                           border-radius: 5px;
                           border: 2px solid white;
                           padding: 1px 1px;
                           background-color: grey;
                        }

                        QMessageBox QPushButton:hover:pressed {
                           background-color: #AAAAAA;
                           color: skyblue;
                           border: 2px solid skyblue
                        }
    """)
    app.setStyle('Fusion')  # Application style, you can use "Windows", "windowsvista" or "Fusion",
    # by default, it is "windowsvista"
    example = Challenges()
    sys.exit(app.exec_())
