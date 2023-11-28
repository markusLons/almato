from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenuBar, QMenu, QTableWidget, QTableWidgetItem, QMessageBox
from PyQt5.QtGui import QPalette, QColor, QIcon
import sys
import mysql.connector
USER_ID = "2"  # Замените на нужный вам ID пользователя
USER_TYPE = 0  # Замените на тип пользователя (0 или 1)

import json
import pandas as pd
import numpy as np

class Report:
    def __init__(self, data, command):
        self.arrival = 0
        self.departure = 0
        self.data = json.loads(data)  # data приходит в формате str
        self.buttons = self.data['buttons']
        self.train = self.trains()
        self.stay_train = self.count_t()
        self.number_lines = self.data['num_lines']
        self.time_operation = pd.read_excel('trains.xlsx', index_col=None)
        self.command = command
        self.count = 0
        self.detail = self.details()
        self.sum = self.summary()
        self.perfomanc = self.perfomance()

    def trains(self):
        a = [self.buttons[i]['train_number'] for i in range(len(self.buttons))]
        a = np.array(a)
        return np.unique(a)

    def count_t(self):
        t = 0
        for tr in self.train:
            start_time = 0
            end_time = 0
            for obj in self.buttons:

                if obj['train_number'] == tr and (
                        obj['name'].lower().find('прибытие') != -1 or obj['name'].lower().find('прибытия') != -1):
                    start_time = int(obj['start_time'][:2]) * 60 + int(obj['start_time'][3:5])
                    break
            for obj in self.buttons:
                if obj['train_number'] == tr and obj['name'].lower().find('отправление') != -1:
                    end_time = int(obj['end_time'][:2]) * 60 + int(obj['end_time'][3:5])
                    break
            if end_time != 0:
                t = t + (end_time - start_time)
            else:
                t = t + 24 * 60 - start_time
        return t

    def summary(self):
        df = pd.DataFrame({'Команда': [], 'Прибытие поездов': [], 'Отбытие поездов': [], ' ': []})
        df.loc[0, "Команда"] = self.command
        for object in self.buttons:
            if object['name'].lower().find('прибытие') != -1 or object['name'].lower().find('прибытия') != -1:
                self.arrival += 1
        df.loc[0, "Прибытие поездов"] = self.arrival
        df.loc[0, "Отбытие поездов"] = self.departure
        df.loc[0, " "] = self.arrival + self.departure
        return df

    def perfomance(self):
        df = pd.DataFrame({'Номер': [], 'Наименование показателей': [], 'Единица измерения': [], self.command: []})
        stat = ['Количество поездов принятых на станцию', 'Количество поездов отправленных со станции',
                'Простой поезда на станции']
        ed = ['поезд', 'поезд', 'мин.']
        result = [self.arrival, self.departure, self.stay_train]
        for i in range(len(ed)):
            df.loc[i, 'Номер'] = i
            df.loc[i, 'Наименование показателей'] = stat[i]
            df.loc[i, 'Единица измерения'] = ed[i]
            df.loc[i, self.command] = result[i]

        return df

    def details(self):
        i = 1
        df = pd.DataFrame({'Номер': [], 'Операция': [], 'Ошибки': []})
        for obj in self.buttons:
            k = 0
            name = str(obj['name'])

            time = int(obj['end_time'][:2]) * 60 + int(obj['end_time'][3:5]) - (
                        int(obj['start_time'][:2]) * 60 + int(obj['start_time'][3:5]))

            if time != int(self.time_operation.loc[(self.time_operation['операция'] == name), 'время, мин.'].values[0]):
                k = 1
                df.loc[i, 'Номер'] = i
                df.loc[i, 'Операция'] = name
                df.loc[i, 'Ошибки'] = 'Длительность операции не соответствует заявленной'
                i += 1
            else:
                self.count += 0.2
            if obj['name'].lower().find('отправление') != -1 and k == 0:
                self.departure += 1
        return df


class ReportWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('Отчет')

        self.setGeometry(100, 100, 900, 700)

        # Устанавливаем стиль приложения
        self.setApplicationStyle()



        # Create menu bar
        menubar = self.createMenuBar()
        menubar.setGeometry(0, 0, 900, 30)

        summary_menu = menubar.addMenu('Сводная')
        indicators_menu = menubar.addMenu('Показатели')
        account_menu = menubar.addMenu('Счет')
        details_menu = menubar.addMenu('Детализация')
        bindings_menu = menubar.addMenu('Привязки')


    def createMenuBar(self):
        # Create menu bar
        menubar = QMenuBar(self)

        # Apply style sheet to change menu background and text color
        menubar.setStyleSheet("background-color: rgb(255, 89, 13); color: white; font-size: 19px;")

        # Optionally, you can also set the font
        font = menubar.font()
        font.setBold(True)
        menubar.setFont(font)

        return menubar

    def setApplicationStyle(self):

        dark_palette = QPalette()
        dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.WindowText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
        dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ToolTipBase, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.ToolTipText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Text, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
        dark_palette.setColor(QPalette.ButtonText, QColor(255, 255, 255))
        dark_palette.setColor(QPalette.BrightText, QColor(255, 0, 0))
        dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        dark_palette.setColor(QPalette.HighlightedText, QColor(0, 0, 0))
        QApplication.setPalette(dark_palette)

    def showSummaryTable(self):
        table = QTableWidget(self)
        table.setGeometry(100, 100, 600, 400)
        table.setColumnCount(4)
        table.setRowCount(5)

        table.setHorizontalHeaderLabels(["Команда", "Прибытие поездов", "Отправлено поездов", "Всего"])
        maps_id = [1,2,3,4]

        try:
            with open('configs/db_config.json', 'r') as config_file:
                config = json.load(config_file)

            connection = mysql.connector.connect(**config)
            cursor = connection.cursor()

            placeholder = ', '.join(['%s'] * len(maps_id))

            query = f"SELECT map_id, name, data FROM maps_competitions WHERE map_id IN ({placeholder})"

            # Execute the query with the values from maps_is
            cursor.execute(query, tuple(maps_id))

            maps = cursor.fetchall()

            cursor.close()
            connection.close()
        except mysql.connector.Error as err:
            QMessageBox.critical(self, 'Ошибка', f'Ошибка при подключении к базе данных: {err}')


        #k=Report(s, "almato")
        data = []
        for map in maps:
            report = Report(map["data"], map["name"])
            data.append(report.sum)
        data = [
            ["Team A", "10", "5"],
            ["Team B", "8", "7"],
            ["Team C", "12", "9"],
            ["Team D", "15", "10"],
            ["Team E", "9", "8"]
        ]

        for i, row in enumerate(data):
            for j, item in enumerate(row):
                table.setItem(i, j, QTableWidgetItem(item))

        style = "::section {""background-color: black; color: white;}"
        table.horizontalHeader().setStyleSheet(style)

        table.setColumnWidth(0, 150)
        table.setColumnWidth(1, 150)
        table.setColumnWidth(2, 180)

        table.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        show_summary_action = context_menu.addAction("Показать сводную таблицу")
        show_summary_action.triggered.connect(self.showSummaryTable)
        context_menu.exec_(event.globalPos())

def main():
    app = QApplication(sys.argv)
    report_window = ReportWindow()
    icon = QIcon("Икона.jpg")
    app.setWindowIcon(icon)
    report_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
