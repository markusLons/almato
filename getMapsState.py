import sys
import json
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel, QComboBox, QTextEdit, QPushButton, QMessageBox

# Глобальная переменная с ID пользователя
USER_ID = "1"  # Замените на нужный вам ID пользователя

class MapsWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Карты пользователя')
        self.setGeometry(100, 100, 400, 300)

        layout = QVBoxLayout()

        self.map_label = QLabel('Выберите карту:')
        self.map_combo = QComboBox()
        layout.addWidget(self.map_label)
        layout.addWidget(self.map_combo)

        self.map_data_label = QLabel('Данные карты:')
        self.map_data_display = QTextEdit()
        self.map_data_display.setReadOnly(True)
        layout.addWidget(self.map_data_label)
        layout.addWidget(self.map_data_display)

        self.load_maps()
        self.map_combo.currentIndexChanged.connect(self.load_map_data)

        self.setLayout(layout)

    def load_maps(self):
        try:
            with open('db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка карт, доступных пользователю
            query = "SELECT map_id, name FROM maps WHERE user_id = %s"
            cursor.execute(query, (USER_ID,))
            maps = cursor.fetchall()

            for map_id, name in maps:
                self.map_combo.addItem(f"{map_id}: {name}")

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')

    def load_map_data(self):
        selected_text = self.map_combo.currentText()

        if not selected_text:
            return

        map_id = selected_text.split(':')[0]

        try:
            with open('db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            # Загрузка данных из выбранной карты
            query = "SELECT map_data FROM maps WHERE map_id = %s"
            cursor.execute(query, (map_id,))
            map_data = cursor.fetchone()

            if map_data:
                self.map_data_display.setPlainText(map_data[0])

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')


def main():
    app = QApplication(sys.argv)
    maps_window = MapsWindow()
    maps_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
