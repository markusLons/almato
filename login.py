import subprocess
import sys
import json
import mysql.connector
from PyQt5.QtWidgets import QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit, QPushButton, QMessageBox

class LoginWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.setWindowTitle('Вход')
        self.setGeometry(100, 100, 300, 150)

        layout = QVBoxLayout()

        self.username_label = QLabel('Имя пользователя:')
        self.username_input = QLineEdit()
        layout.addWidget(self.username_label)
        layout.addWidget(self.username_input)

        self.password_label = QLabel('Пароль:')
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_label)
        layout.addWidget(self.password_input)

        self.login_button = QPushButton('Войти')
        self.login_button.clicked.connect(self.login)
        layout.addWidget(self.login_button)

        self.setLayout(layout)

    def login(self):
        username = self.username_input.text()
        password = self.password_input.text()

        # Загрузка данных для подключения из JSON файла
        try:
            with open('db_config.json', 'r') as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            QMessageBox.critical(self, 'Ошибка', 'Файл конфигурации базы данных не найден.')
            return

        try:
            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user = cursor.fetchone()

            if user and user[2] == password:
                # Запуск файла EditMap.py
                subprocess.Popen(["python", "main.py"])
                self.close()  # Закрытие окна входа после успешного входа
            else:
                QMessageBox.critical(self, 'Ошибка', 'Неверное имя пользователя или пароль.')
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')
        finally:
            if connection:
                connection.close()

def main():
    app = QApplication(sys.argv)
    login_window = LoginWindow()
    login_window.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()
