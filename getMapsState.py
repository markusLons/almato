import subprocess
import sys
import json
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QMessageBox, QTabWidget

from report_for_Tonya import ReportWindow

# Глобальная переменная с ID пользователя и его типом
USER_ID = "2"  # Замените на нужный вам ID пользователя
USER_TYPE = 0  # Замените на тип пользователя (0 или 1)
from PyQt5.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QVBoxLayout

class CreateMapDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle('Создать новую карту')

        # Создайте элементы интерфейса для ввода данных о новой карте
        self.name_label = QLabel('Название карты:')
        self.name_input = QLineEdit()

        self.comment_label = QLabel('Комментарий:')
        self.comment_input = QLineEdit()

        self.station_type_label = QLabel('Тип станции:')
        self.station_type_combobox = QComboBox()
        self.station_type_combobox.addItems(['Тип 1', 'Тип 2', 'Тип 3'])  # Замените на свои значения

        self.number_of_tracks_label = QLabel('Количество путей:')
        self.number_of_tracks_spinbox = QSpinBox()
        self.number_of_tracks_spinbox.setMinimum(1)  # Установите минимальное значение
        self.number_of_tracks_spinbox.setMaximum(100)  # Установите максимальное значение

        self.create_button = QPushButton('Создать')
        self.create_button.clicked.connect(self.create_map)

        # Разместите элементы интерфейса в макете
        layout = QVBoxLayout()
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.comment_label)
        layout.addWidget(self.comment_input)
        layout.addWidget(self.station_type_label)
        layout.addWidget(self.station_type_combobox)
        layout.addWidget(self.number_of_tracks_label)
        layout.addWidget(self.number_of_tracks_spinbox)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def create_map(self):
        # Получите значения, введенные пользователем
        new_map_name = self.name_input.text()
        new_map_comment = self.comment_input.text()
        new_map_station_type = self.station_type_combobox.currentText()
        new_map_number_of_tracks = self.number_of_tracks_spinbox.value()

        # Выполните SQL-запрос для вставки новой карты в базу данных, как описано в предыдущем ответе

        # Закройте диалоговое окно после создания карты
        self.accept()

def get_user_info_and_maps():

    with open('configs/db_config.json', 'r') as config_file:
        config = json.load(config_file)

    connection = mysql.connector.connect(**config)
    cursor = connection.cursor()

    # Загрузка данных о пользователе
    query = "SELECT username, type, name FROM users WHERE id = %s"
    cursor.execute(query, (USER_ID,))
    user = cursor.fetchall()[0]
    global USER_TYPE, name, login
    USER_TYPE = user[1]
    name = user[2]
    login = user[0]

    print(user)

    cursor.close()
    connection.close()

class MapsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Карты пользователя')
        self.setGeometry(100, 100, 600, 400)

        layout = QVBoxLayout()

        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)

        self.user_name_label = QLabel(f'Имя пользователя: {name}')
        layout.addWidget(self.user_name_label)
        self.user_name_label.setText(f'Имя пользователя: {name}')

        # Вкладка "Мои карты" (для пользователя с типом 0)
        if USER_TYPE == 0 or USER_TYPE == 1:
            self.my_maps_tab = QWidget()
            self.tabs.addTab(self.my_maps_tab, 'Мои карты')

            my_maps_layout = QHBoxLayout()

            # Список названий своих карт
            self.my_map_list = QListWidget()
            self.my_map_list.itemClicked.connect(self.load_my_map_data)
            my_maps_layout.addWidget(self.my_map_list)

            # Отображение данных о своей карте и кнопка "Загрузить"
            self.my_map_info_layout = QVBoxLayout()

            self.my_map_name_label = QLabel('Название карты:')
            self.my_map_name_display = QLabel('')
            self.my_map_info_layout.addWidget(self.my_map_name_label)
            self.my_map_info_layout.addWidget(self.my_map_name_display)

            self.my_map_data_label = QLabel('Данные карты:')
            self.my_map_data_display = QTextEdit()
            self.my_map_data_display.setReadOnly(True)
            self.my_map_info_layout.addWidget(self.my_map_data_label)
            self.my_map_info_layout.addWidget(self.my_map_data_display)

            self.my_comment_label = QLabel('Комментарий:')
            self.my_comment_display = QTextEdit()
            self.my_comment_display.setReadOnly(True)
            self.my_map_info_layout.addWidget(self.my_comment_label)
            self.my_map_info_layout.addWidget(self.my_comment_display)

            self.my_created_label = QLabel('Дата создания:')
            self.my_created_display = QLabel('')
            self.my_map_info_layout.addWidget(self.my_created_label)
            self.my_map_info_layout.addWidget(self.my_created_display)

            self.my_updated_label = QLabel('Дата изменения:')
            self.my_updated_display = QLabel('')
            self.my_map_info_layout.addWidget(self.my_updated_label)
            self.my_map_info_layout.addWidget(self.my_updated_display)

            self.load_my_button = QPushButton('Загрузить')
            self.load_my_button.clicked.connect(self.load_my_map_data_and_run_main)
            self.my_map_info_layout.addWidget(self.load_my_button)
            if USER_TYPE == 1:
                self.create_competition_button = QPushButton('Создать соревнование')
                self.create_competition_button.clicked.connect(self.create_competition)
                self.my_map_info_layout.addWidget(self.create_competition_button)
            my_maps_layout.addLayout(self.my_map_info_layout)

            self.my_maps_tab.setLayout(my_maps_layout)


        # Вкладка "Все карты" (для пользователя с типом 1)
        if USER_TYPE == 1:
            self.all_maps_tab = QWidget()
            self.tabs.addTab(self.all_maps_tab, 'Все карты')

            all_maps_layout = QHBoxLayout()

            # Список названий всех карт
            self.map_list = QListWidget()
            self.map_list.itemClicked.connect(self.load_map_data)
            all_maps_layout.addWidget(self.map_list)

            # Отображение данных о карте и кнопка "Загрузить"
            self.map_info_layout = QVBoxLayout()

            self.map_name_label = QLabel('Название карты:')
            self.map_name_display = QLabel('')
            self.map_info_layout.addWidget(self.map_name_label)
            self.map_info_layout.addWidget(self.map_name_display)

            self.map_data_label = QLabel('Данные карты:')
            self.map_data_display = QTextEdit()
            self.map_data_display.setReadOnly(True)
            self.map_info_layout.addWidget(self.map_data_label)
            self.map_info_layout.addWidget(self.map_data_display)

            self.comment_label = QLabel('Комментарий:')
            self.comment_display = QTextEdit()
            self.comment_display.setReadOnly(True)
            self.map_info_layout.addWidget(self.comment_label)
            self.map_info_layout.addWidget(self.comment_display)

            self.created_label = QLabel('Дата создания:')
            self.created_display = QLabel('')
            self.map_info_layout.addWidget(self.created_label)
            self.map_info_layout.addWidget(self.created_display)

            self.updated_label = QLabel('Дата изменения:')
            self.updated_display = QLabel('')
            self.map_info_layout.addWidget(self.updated_label)
            self.map_info_layout.addWidget(self.updated_display)

            self.load_button = QPushButton('Загрузить')
            self.load_button.clicked.connect(self.load_map_data_and_run_main)
            self.map_info_layout.addWidget(self.load_button)

            all_maps_layout.addLayout(self.map_info_layout)

            self.all_maps_tab.setLayout(all_maps_layout)

        # Дополнительные кнопки для пользователя с типом 1
        if USER_TYPE == 1:
            self.create_map_button = QPushButton('Создать карту')
            self.create_map_button.clicked.connect(self.create_map)
            layout.addWidget(self.create_map_button)



        # Загрузка списков карт
        self.load_map_list()
        if USER_TYPE == 1:
            self.load_all_maps_list()

        self.setLayout(layout)

    def open_report_window(self):
        subprocess.run(["python", "report_for_Tonya.py"])

    def load_map_list(self):
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка списка названий карт, доступных пользователю
            query = "SELECT map_id, name FROM maps WHERE user_id = %s"
            cursor.execute(query, (USER_ID,))
            maps = cursor.fetchall()

            for map_id, name in maps:
                self.my_map_list.addItem(f"{map_id}: {name}")

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_all_maps_list(self):
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка списка названий всех карт и их владельцев
            query = "SELECT maps.map_id, maps.name, users.name FROM maps INNER JOIN users ON maps.user_id = users.id"
            cursor.execute(query)
            all_maps = cursor.fetchall()

            for map_id, map_name, user_name in all_maps:
                self.map_list.addItem(f"{map_id}: {map_name} (Владелец: {user_name})")

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_my_map_data(self, item):
        map_id = item.text().split(':')[0]
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка данных о выбранной своей карте
            query = "SELECT name, map_data, comment, data_create, data_edit FROM maps WHERE map_id = %s"
            cursor.execute(query, (map_id,))
            map_data = cursor.fetchone()

            if map_data:
                self.my_map_name_display.setText(map_data[0])
                self.my_map_data_display.setPlainText(map_data[1].decode('utf-8'))
                self.my_comment_display.setPlainText(map_data[2].decode('utf-8'))
                self.my_created_display.setText(str(map_data[3]))
                self.my_updated_display.setText(str(map_data[4]))

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_map_data(self, item):
        map_id = item.text().split(':')[0]
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка данных о выбранной карте
            query = "SELECT name, map_data, comment, data_create, data_edit FROM maps WHERE map_id = %s"
            cursor.execute(query, (map_id,))
            map_data = cursor.fetchone()

            if map_data:
                self.map_name_display.setText(map_data[0])
                self.map_data_display.setPlainText(map_data[1].decode('utf-8'))
                self.comment_display.setPlainText(map_data[2].decode('utf-8'))
                self.created_display.setText(str(map_data[3]))
                self.updated_display.setText(str(map_data[4]))

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_my_map_data_and_run_main(self):
        map_id = self.my_map_list.currentItem().text().split(':')[0]

        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка данных о выбранной своей карте
            query = "SELECT map_data FROM maps WHERE map_id = %s"
            cursor.execute(query, (map_id,))
            map_data = cursor.fetchone()

            if map_data:
                map_data_str = map_data[0].decode('utf-8')

                # Запустить main.py и передать данные в качестве аргумента
                main_command = f"python main.py {map_id}"
                subprocess.Popen(main_command, shell=True)

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_map_data_and_run_main(self):
        map_id = self.map_list.currentItem().text().split(':')[0]

        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка данных о выбранной карте
            query = "SELECT map_data FROM maps WHERE map_id = %s"
            cursor.execute(query, (map_id,))
            map_data = cursor.fetchone()

            if map_data:
                map_data_str = map_data[0].decode('utf-8')

                # Запустить main.py и передать данные в качестве аргумента
                main_command = f"python main.py {map_id}"
                subprocess.Popen(main_command, shell=True)

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def create_map(self):
        # Создайте экземпляр диалогового окна для создания новой карты
        create_map_dialog = CreateMapDialog()

        # Откройте диалоговое окно
        if create_map_dialog.exec_() == QDialog.Accepted:
            # Обновите список карт на текущей вкладке
            self.load_map_list()

    def create_competition(self):
        # Добавьте здесь код для создания нового соревнования
        pass

def main():
    global USER_ID, USER_TYPE
    if len(sys.argv) != 2:
        print("Usage: python main.py <user_index>")
    else:
        USER_ID = str(sys.argv[1])
    app = QApplication(sys.argv)
    get_user_info_and_maps()
    maps_window = MapsWindow()
    maps_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
