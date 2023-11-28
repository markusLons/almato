import subprocess
import sys
import json
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QTextEdit, \
    QPushButton, QMessageBox, QTabWidget, QTimeEdit

from report_for_Tonya import ReportWindow

# Глобальная переменная с ID пользователя и его типом
USER_ID = "2"  # Замените на нужный вам ID пользователя
USER_TYPE = 0  # Замените на тип пользователя (0 или 1)
from PyQt5.QtWidgets import QDialog, QLabel, QTextEdit, QPushButton

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QComboBox, QSpinBox, QPushButton, QVBoxLayout

class AddUserDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.my_parent = parent
        self.setWindowTitle('Добавить нового поьзователя')

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()

        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()

        self.type_label = QLabel('Тип пользователя (1 - администратор, иначе 0):')
        self.type_input = QLineEdit()

        self.name_label = QLabel('Фамилия Имя:')
        self.name_input = QLineEdit()

        self.create_button = QPushButton('Создать')
        self.create_button.clicked.connect(self.add_user)

        layout = QVBoxLayout()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)
        layout.addWidget(self.type_label)
        layout.addWidget(self.type_input)
        layout.addWidget(self.name_label)
        layout.addWidget(self.name_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def add_user(self):
        # Получите значения, введенные пользователем
        new_user_username = self.username_input.text()
        new_user_password = self.password_input.text()
        new_user_type = self.type_input.text()
        new_user_name = self.name_input.text()

        # Выполните SQL-запрос для вставки новой карты в базу данных, как описано в предыдущем ответе
        # Включите значения начала и конца времени в ваш SQL-запрос
        self.send_user_on_SQL(user_username=new_user_username,
                             user_password=new_user_password,
                             user_type=new_user_type,
                             user_name=new_user_name)
        # Закройте диалоговое окно после создания карты
        self.accept()

    def send_user_on_SQL(self, user_username, user_password, user_type, user_name):
        with open('configs/db_config.json', 'r') as config_file:
            config = json.load(config_file)

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Используйте параметризованный запрос, чтобы избежать SQL-инъекций
        query = """
        INSERT INTO users 
        (username, password, type, name) 
        VALUES 
        (%s, %s, %s, %s)
        """

        # Значения для параметризованного запроса
        values = (user_username, user_password, user_type, user_name)

        try:
            cursor.execute(query, values)
            connection.commit()
            print("Запись успешно добавлена в базу данных")
        except Exception as e:
            print(f"Ошибка при добавлении записи в базу данных: {e}")
        finally:
            cursor.close()
            connection.close()



class CreateMapDialog(QDialog):
    def __init__(self, parent):
        super().__init__()
        self.my_parent = parent
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

        self.start_time_label = QLabel('Начало времени:')  # Новый пункт - Начало времени
        self.start_time_input = QTimeEdit()

        self.end_time_label = QLabel('Конец времени:')  # Новый пункт - Конец времени
        self.end_time_input = QTimeEdit()

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
        layout.addWidget(self.start_time_label)  # Добавляем начало времени
        layout.addWidget(self.start_time_input)
        layout.addWidget(self.end_time_label)  # Добавляем конец времени
        layout.addWidget(self.end_time_input)
        layout.addWidget(self.create_button)
        self.setLayout(layout)

    def send_map_on_SQL(self, map_name, map_comment, map_station_type, map_number_of_tracks, start_time, end_time):
        with open('configs/db_config.json', 'r') as config_file:
            config = json.load(config_file)

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()
        start_time = int(self.start_time_input.time().toString("hh"))  # Получаем часы начала времени
        end_time = int(self.end_time_input.time().toString("hh"))  #
        map_data = json.dumps({
            "buttons": [],
            "num_lines": map_number_of_tracks,
            "start_time": start_time,
            "end_time": end_time
        })

        # Используйте параметризованный запрос, чтобы избежать SQL-инъекций
        query = """
        INSERT INTO maps 
        (user_id, map_data, comment, name) 
        VALUES 
        (%s, %s, %s, %s)
        """

        # Значения для параметризованного запроса
        values = (USER_ID, map_data, map_comment, map_name)

        try:
            cursor.execute(query, values)
            connection.commit()
            print("Запись успешно добавлена в базу данных")
        except Exception as e:
            print(f"Ошибка при добавлении записи в базу данных: {e}")
        finally:
            cursor.close()
            connection.close()
        self.my_parent.update_map_list()

    def create_map(self):
        # Получите значения, введенные пользователем
        new_map_name = self.name_input.text()
        new_map_comment = self.comment_input.text()
        new_map_station_type = self.station_type_combobox.currentText()
        new_map_number_of_tracks = self.number_of_tracks_spinbox.value()

        start_time = self.start_time_input.time().toString("hh:mm:ss")  # Получаем начало времени
        end_time = self.end_time_input.time().toString("hh:mm:ss")  # Получаем конец времени

        # Выполните SQL-запрос для вставки новой карты в базу данных, как описано в предыдущем ответе
        # Включите значения начала и конца времени в ваш SQL-запрос
        self.send_map_on_SQL(map_name=new_map_name, map_comment=new_map_comment,
                             map_number_of_tracks=new_map_number_of_tracks,
                             start_time=start_time, end_time=end_time,
                             map_station_type=new_map_station_type)
        # Закройте диалоговое окно после создания карты
        self.accept()

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

                self.new_user = QPushButton('Добавить нового пользователя')
                self.new_user.clicked.connect(self.add_user)
                self.my_map_info_layout.addWidget(self.new_user)

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

            # Вкладка "Соревнования" (для пользователя с типом 1)
            if USER_TYPE == 1:
                self.all_competitions_tab = QWidget()

                self.tabs.addTab(self.all_competitions_tab, 'Соревнования')

                all_competitions_layout = QHBoxLayout()

                # Список названий всех карт
                self.competitions_list = QListWidget()
                self.competitions_list.itemClicked.connect(self.load_competition_data)
                all_competitions_layout.addWidget(self.competitions_list)

                self.all_competitions_tab.setLayout(all_competitions_layout)
                self.load_all_competitions_list()

        # Дополнительные кнопки для пользователя с типом 1
        if USER_TYPE == 1:
            self.create_map_button = QPushButton('Создать карту')
            self.create_map_button.clicked.connect(self.create_map)
            layout.addWidget(self.create_map_button)

            self.report_button = QPushButton('ЦЗТ')
            self.report_button.clicked.connect(self.open_report_window)

            self.map_info_layout.addWidget(self.report_button) # убрать

        # Загрузка списков карт
        self.load_map_list()
        if USER_TYPE == 1:
            self.load_all_maps_list()
        self.session_code_label = QLabel('Код сессии:')
        self.session_code_input = QLineEdit()
        layout.addWidget(self.session_code_label)
        layout.addWidget(self.session_code_input)

        # Добавляем кнопку подключения
        self.connect_button = QPushButton('Подключиться')
        self.connect_button.clicked.connect(self.connect_to_session)
        layout.addWidget(self.connect_button)
        self.setLayout(layout)

    def open_report_window(self):
        subprocess.run(["python", "report_for_Tonya.py"])
    def connect_to_session(self):
        # Здесь вы можете получить код сессии из self.session_code_input.text()
        session_code = self.session_code_input.text()
        session_code, mapID = session_code.split("*")
        main_command = f"python main.py {mapID} {USER_ID} {session_code}"
        subprocess.Popen(main_command, shell=True)
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

    def load_all_competitions_list(self):
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка списка названий всех соревнований
            query = "SELECT competitions.competition_id, competitions.name, competitions.date FROM competitions"
            cursor.execute(query)
            all_competitions = cursor.fetchall()

            for competition_id, competition_name, competition_date in all_competitions:
                self.competitions_list.addItem(f"{competition_id}: {competition_name} (Дата: {competition_date})")

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

    def load_competition_data(self, item):
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
                main_command = f"python main.py {map_id} {USER_ID} {0}"
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
                main_command = f"python main.py {map_id} {USER_ID} {0}"
                subprocess.Popen(main_command, shell=True)

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def add_user(self):
        add_user_dialog = AddUserDialog(self)

        # Откройте диалоговое окно
        if add_user_dialog.exec_() == QDialog.Accepted:
            print("1")
            # Обновите список карт на текущей вкладке
            #self.load_user_list()

    def create_map(self):
        # Создайте экземпляр диалогового окна для создания новой карты
        create_map_dialog = CreateMapDialog(self)

        # Откройте диалоговое окно
        if create_map_dialog.exec_() == QDialog.Accepted:
            # Обновите список карт на текущей вкладке
            self.load_map_list()
    def update_map_list(self):
        # Очистите список карт
        self.my_map_list.clear()

        # После этого вызовите функцию для загрузки списка карт заново
        self.load_map_list()
    def create_competition(self):
        # Добавьте здесь код для создания нового соревнования
        pass

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