import json
import os

import mysql.connector
from PyQt5.QtWidgets import QMessageBox
import json
import mysql.connector
import threading
import time
from PyQt5.QtWidgets import QMessageBox
class Host:
    def __init__(self, session_id, userID):
        self.userID = userID
        self.session_id = session_id
        self.connection = None
        self.create_connection()

    def create_connection(self):
        # Загрузка данных для подключения из JSON файла
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            QMessageBox.critical(None, 'Ошибка', 'Файл конфигурации базы данных не найден.')
            return

        try:
            self.connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к базе данных: {err}')

    def create_event(self, id_object: int, event: str):
        if not self.connection:
            QMessageBox.warning(None, 'Внимание', 'Подключение к базе данных отсутствует. Вызовите create_connection() сначала.')
            return

        try:
            cursor = self.connection.cursor()
            cursor.execute('''
                INSERT INTO Events (userID, SessionID, ObjectID, OperationType)
                VALUES (%s, %s, %s, %s)
            ''', (self.userID, self.session_id, id_object, event))
            self.connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(None, 'Ошибка', f'Ошибка при создании события: {err}')
class Client:
    def __init__(self, session_id, userID):
        self.userID = userID
        self.session_id = session_id
        self.connection = None
        self.last_event_id = 0  # Последний полученный идентификатор события
        self.create_connection()

        # Запускаем поток для фоновой работы
        self.thread = threading.Thread(target=self.run_background)
        self.thread.daemon = True
        self.thread.start()

    def create_connection(self):
        # Загрузка данных для подключения из JSON файла
        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)
        except FileNotFoundError:
            QMessageBox.critical(None, 'Ошибка', 'Файл конфигурации базы данных не найден.')
            return

        try:
            self.connection = mysql.connector.connect(**config)
        except mysql.connector.Error as err:
            QMessageBox.critical(None, 'Ошибка', f'Ошибка подключения к базе данных: {err}')

    def fetch_events(self):
        if not self.connection:
            return []

        try:
            self.create_connection()
            with self.connection.cursor(dictionary=True) as cursor:
                print("eee")
                cursor = self.connection.cursor(dictionary=True)
                cursor.execute('''
                    SELECT EventID, ObjectID, OperationType
                    FROM Events
                    WHERE  SessionID = %s AND EventID > %s;
                ''', ( self.session_id, 0))

                events = cursor.fetchall()
            return events
        except mysql.connector.Error as err:
            QMessageBox.critical(None, 'Ошибка', f'Ошибка при получении событий: {err}')
            return []

    def process_events(self, events):
        for event in events:
            # Здесь вы можете выполнить нужные действия в зависимости от типа события и объекта

            # Получаем данные о событии
            event_id = event['EventID']
            if event_id <= self.last_event_id:
                continue
            print(f"Received event {event['EventID']}: ObjectID={event['ObjectID']}, OperationType={event['OperationType']}")

            object_id = event['ObjectID']
            operation_type = event['OperationType']

            # Формируем имя файла на основе данных о событии
            file_name = f'event_{event_id}_object_{object_id}_operation_{operation_type.split()[0][:-1].replace("_", "")}!{int(operation_type.split(" ")[1])}!{int(operation_type.split(" ")[2])}.json'

            # Создаем путь к файлу в папке tmp
            file_path = os.path.join('tmp', file_name)

            # Создаем пустой файл
            with open(file_path, 'w') as empty_file:
                pass

            self.last_event_id = max(self.last_event_id, event['EventID'])

    def run_background(self):
        while True:
            events = self.fetch_events()
            if events:
                self.process_events(events)

            # Пауза перед следующей проверкой базы данных
            time.sleep(0.5)
if __name__ == "__main__":
    # Пример использования
    host_instance = Host(session_id="your_session_id")
    host_instance.create_connection()
    host_instance.create_event(id_object=1, event="Move")
