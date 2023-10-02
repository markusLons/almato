import subprocess
import sys
import json
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget, QTextEdit, QPushButton, QMessageBox

from report_for_Tonya import ReportWindow

# Глобальная переменная с ID пользователя
USER_ID = "1"  # Замените на нужный вам ID пользователя

class MapsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Карты пользователя')
        self.setGeometry(100, 100, 600, 400)

        layout = QHBoxLayout()

        # Список названий карт
        self.map_list = QListWidget()
        self.map_list.itemClicked.connect(self.load_map_data)
        layout.addWidget(self.map_list)

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

        self.report_button = QPushButton('ЦЗТ')
        self.report_button.clicked.connect(self.open_report_window)
        self.map_info_layout.addWidget(self.report_button)

        layout.addLayout(self.map_info_layout)

        self.load_map_list()

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
                self.map_list.addItem(f"{map_id}: {name}")

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


def main():
    global USER_ID
    if len(sys.argv) != 2:
        print("Usage: python main.py <user_index>")
    else:
        USER_ID = str(sys.argv[1])
    app = QApplication(sys.argv)
    maps_window = MapsWindow()
    maps_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
