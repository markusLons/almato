# railroad_station_app.py
import os
import json
import sys

import mysql.connector
from PyQt5.QtWidgets import (
    QMainWindow, QToolBar, QAction, QPushButton, QWidget, QScrollArea, QVBoxLayout,
    QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QInputDialog, QMenu,
    QMessageBox, QApplication,
)
from PyQt5.QtWidgets import QLineEdit
from PyQt5.QtWidgets import QComboBox
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from datetime import datetime

import EventManager
from draggable_button import DraggableButton

pixel_time_mapping = {}


def load_map_data_from_sql(item):
    map_info={}
    try:
        with open('configs/db_config.json', 'r') as config_file:
            config = json.load(config_file)

        connection = mysql.connector.connect(**config)
        cursor = connection.cursor()

        # Загрузка данных о выбранной карте
        query = "SELECT name, map_data, comment, data_create, data_edit, user_id FROM maps WHERE map_id = %s"
        cursor.execute(query, (item,))
        map_data = cursor.fetchone()

        if map_data:
            map_info["name"] = map_data[0]
            map_info["data"] = map_data[1].decode('utf-8')
            map_info["comment"] = map_data[2].decode('utf-8')
            map_info["user_id"] = map_data[5]

        cursor.close()
        connection.close()
        return map_info
    except mysql.connector.Error as err:
        print(err)


class RailroadStationApp(QMainWindow):
    def __init__(self, id): 
        self.pixel_time_mapping = {}
        super().__init__()
        self.data = ""
        self.map_id = id
        if id is not None:
            data = load_map_data_from_sql(id)
            self.user_id = data["user_id"]

            data = json.loads(data["data"])
            self.start_time = data["start_time"]
            self.end_time = data["end_time"]

        self.load_constants_from_json()
        self.setWindowTitle("Железнодорожная станция")
        self.setGeometry(100, 100, 800, 600)
        self.showFullScreen()

        self.state = {'horizontal_lines': [], 'widgets': []}
        self.current_image_path = None

        self.num_lines = 0
        self.horizontal_lines = []
        self.horizontal_line_names = []
        self.initUI()
        self.load_state_from_data(data)
    def load_constants_from_json(self):
        try:
            # Открываем файл mapConstant.json и читаем константы
            with open('configs/mapConstant.json', 'r') as json_file:
                constants = json.load(json_file)

            # Задаем значения константам
            global interval, maxPixelsScroll
            interval = constants["interval"]
            maxPixelsScroll = constants["maxPixelsScroll"]

        except Exception as e:
            print(f"Ошибка при загрузке констант из JSON: {e}")
    def clear_current_state(self):
        """
        Очищает текущее состояние приложения, удаляя все кнопки и линии.
        """
        # Очищаем текущее состояние
        for button in self.buttons:
            button.setParent(None)
            button.deleteLater()
        self.buttons = []
        for line in self.horizontal_lines:
            line.setParent(None)
            line.deleteLater()
        self.horizontal_lines = []
        self.num_lines = 0
        self.current_image_path = None
    def initUI(self):
        self.createMenus()
        self.createToolBar()
        self.createScrollArea()

    def createMenus(self):
        # Создаем действия для меню
        exitAction = QAction('Выйти', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.close)

        FullscreenAction = QAction('Полноэкранный режим', self)
        FullscreenAction.setStatusTip('Полноэкранноый режим')
        FullscreenAction.triggered.connect(self.showFullScreen)

        exitFullscreenAction = QAction('Выйти из полноэкранного режима', self)
        exitFullscreenAction.setStatusTip('Выйти из полноэкранного режима')
        exitFullscreenAction.triggered.connect(self.showNormal)

        # Создаем меню "Файл" и добавляем в него действия
        fileMenu = self.menuBar().addMenu('Файл')
        fileMenu.addAction(exitAction)

        saveAction = QAction('Сохранить', self)
        saveAction.setShortcut('Ctrl+S')
        saveAction.setStatusTip('Сохранить состояние')
        saveAction.triggered.connect(self.save_state)
        fileMenu.addAction(saveAction)

        loadAction = QAction('Загрузить', self)
        loadAction.setShortcut('Ctrl+L')
        loadAction.setStatusTip('Загрузить состояние')
        loadAction.triggered.connect(self.load_state_from_data)
        fileMenu.addAction(loadAction)

        # Создаем меню "Вид" и добавляем в него действия
        viewMenu = self.menuBar().addMenu('Вид')
        viewMenu.addAction(FullscreenAction)
        viewMenu.addAction(exitFullscreenAction)

        # Создаем меню "Полотно" и добавляем в него действия
        canvasMenu = self.menuBar().addMenu('Полотно')

        adddownMenu = QMenu('Добавление', self)

        addHorizontalLineAction1 = QAction('Добавить горизонтальную полосу', self)
        addHorizontalLineAction1.triggered.connect(self.add_horizontal_line1)
        adddownMenu.addAction(addHorizontalLineAction1)

        addHorizontalLineAction = QAction('Добавить горизонтальные полосы', self)
        addHorizontalLineAction.triggered.connect(self.add_horizontal_line)
        adddownMenu.addAction(addHorizontalLineAction)

        canvasMenu.addMenu(adddownMenu)

        dropdownMenu = QMenu('Удаление', self)

        removeHorizontalLineAction = QAction('Удалить горизонтальную полосу по индексу', self)
        removeHorizontalLineAction.triggered.connect(self.remove_horizontal_line_ind)
        dropdownMenu.addAction(removeHorizontalLineAction)

        removeHorizontalLineAction_1 = QAction('Удалить первую горизонтальную полосу', self)
        removeHorizontalLineAction_1.triggered.connect(self.remove_horisontal_line_first)
        dropdownMenu.addAction(removeHorizontalLineAction_1)

        removeHorizontalLineAction_2 = QAction('Удалить последнюю горизонтальную полосу', self)
        removeHorizontalLineAction_2.triggered.connect(self.remove_horisontal_line_last)
        dropdownMenu.addAction(removeHorizontalLineAction_2)

        canvasMenu.addMenu(dropdownMenu)
    def get_map_data(self):
        state = {}  # Создаем пустой словарь для сохранения состояния

        # Создаем список для хранения информации о кнопках
        buttons_info = []

        for i, button in enumerate(self.buttons):
            start_time_button, end_time_button = button.get_coordinate()
            button_info = {
                'index': i,  # Порядковый номер кнопки
                'name': button.simple,  # Название кнопки (предполагается, что текст кнопки содержит имя)
                'start_time': start_time_button.strftime("%H:%M"),  # Время начала
                'end_time': end_time_button.strftime("%H:%M"),  # Время окончания
                'line_index': button.line_index,  # Номер строки, на которой находится кнопка
            }
            buttons_info.append(button_info)

        state['buttons'] = buttons_info  # Добавляем информацию о кнопках в состояние
        state['num_lines'] = self.num_lines  # Добавляем количество полос
        state["start_time"] = self.start_time
        state["end_time"] = self.end_time

        state["horizontal_line_names"] = self.horizontal_line_names

        json_state = json.dumps(state, indent=4, ensure_ascii=False)

        # Теперь вы можете использовать json_state как строку или сохранить ее в переменной
        print("Состояние успешно сохранено:")
        print(json_state)
        return json_state

    def save_state(self):

        # Создаем подключение к базе данных из файла конфигурации
        with open('configs/db_config.json', 'r') as config_file:
            config = json.load(config_file)

        connection = None  # Инициализируем переменные connection и cursor
        cursor = None

        try:
            connection = mysql.connector.connect(**config, connect_timeout=60)
            cursor = connection.cursor()

            if self.map_id == -1:
                # Создаем новую карту
                map_data = self.get_map_data()  # Преобразуем состояние в JSON-строку
                data_create = datetime.now()
                data_edit = data_create
                name = "Новая карта"  # Имя новой карты
                cursor.execute("INSERT INTO maps (user_id, map_data, comment, name, data_create, data_edit) "
                               "VALUES (%s, %s, %s, %s, %s, %s)",
                               (self.user_id, map_data, "", name, data_create, data_edit))
            else:
                # Обновляем существующую карту
                map_data = self.get_map_data()  # Преобразуем состояние в JSON-строку
                data_edit = datetime.now()
                cursor.execute("UPDATE maps SET map_data = %s, data_edit = %s WHERE map_id = %s",
                               (map_data, data_edit, self.map_id))

            # Сохраняем изменения
            connection.commit()
            print("Карта успешно сохранена или обновлена в базе данных.")

        except mysql.connector.Error as err:
            print(f"Ошибка при работе с базой данных: {err}")
        finally:
            if cursor:
                cursor.close()
            if connection and connection.is_connected():
                connection.close()

    def load_state_from_data(self, state_data):
        self.clear_current_state()

        self.num_lines = state_data.get('num_lines', 0)
        self.horizontal_lines = self.createHorizontalLines()

        buttons_info = state_data.get('buttons', [])
        for button_info in buttons_info:
            button = DraggableButton(parent=self,
                                     simple=button_info["name"],
                                     time_now=(button_info.get('start_time'),
                                               button_info.get('end_time')),
                                     pixel_time_mapping=pixel_time_mapping,
                                     line_index= int(button_info.get("line_index"))
                                     )
            button.show()
            self.buttons.append(button)

        self.current_image_path = state_data.get('current_image_path', None)
        QMessageBox.information(self, "Загрузка состояния", "Состояние успешно загружено.")
        for i in self.buttons:
            i.refresh_line()

    def add_horizontal_line(self):

        user_input, ok = QInputDialog.getInt(self, 'Введите количество полос', 'Количество:')
        if ok:
            layout = self.scroll_area.widget().layout()

            for _ in range(self.num_lines):
                line_layout = QHBoxLayout()  # Создаем горизонтальный макет для строки
                line = QPushButton()
                line.setFixedSize(maxPixelsScroll, 50)
                self.horizontal_lines.append(line)

                # Создаем виджет с именем (QLineEdit) и устанавливаем начальное имя
                name_edit = QLineEdit("Имя полосы")  # Замените "Имя полосы" на фактическое имя
                name_edit.setFixedSize(100, 30)  # Установите желаемый размер для виджета с именем
                name_edit.returnPressed.connect(lambda text=name_edit.text(), line=line: self.change_name(text, line))

                line_layout.addWidget(name_edit)  # Добавляем виджет с именем (QLineEdit) в макет строки
                line_layout.addWidget(line)  # Добавляем горизонтальную полосу в макет строки

                # Добавляем строку в общий макет
                layout.addLayout(line_layout)

                spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                layout.addItem(spacer)

            self.scroll_area.widget().setLayout(layout)
            self.num_lines += user_input
            self.horizontal_line_names.append("Имя полосы")
            pass

    def add_horizontal_line1(self):
        self.count_gorisontal_line = 1
        layout = self.scroll_area.widget().layout()
        line_layout = QHBoxLayout()
        line = QPushButton()
        line.setFixedSize(maxPixelsScroll, 50)
        self.horizontal_lines.append(line)

        name_edit = QLineEdit("Имя полосы")
        name_edit.setFixedSize(100, 30)
        name_edit.returnPressed.connect(lambda text=name_edit.text(), line=line: self.change_name(text, line))

        line_layout.addWidget(name_edit)
        line_layout.addWidget(line)

        layout.addLayout(line_layout)

        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        self.num_lines += 1

        # Добавляем пустую строку в массив имен
        self.horizontal_line_names.append("Имя полосы")

    def remove_horizontal_line_ind(self):
        index, ok = QInputDialog.getInt(self, 'Введите индекс полосы:', 'Индекс:')
        if ok:
            if 0 <= index < len(self.horizontal_lines):
                line = self.horizontal_lines.pop(index)
                line.setParent(None)
                del line
                self.num_lines -= 1
                self.scroll_area.widget().update()
            else:
                QMessageBox.warning(self, "Предупреждение", "Несуществующая строка!", QMessageBox.Ok)
    def remove_horisontal_line_first(self):
        if len(self.horizontal_lines)>0:
            line = self.horizontal_lines.pop(0)
            line.setParent(None)
            del line
            self.scroll_area.widget().update()
            self.num_lines -=1
        else:
            QMessageBox.warning(self, "Предупреждение", "Несуществующая строка!", QMessageBox.Ok)

    def remove_horisontal_line_last(self):
        if len(self.horizontal_lines)>0:
            line = self.horizontal_lines.pop(len(self.horizontal_lines)-1)
            line.setParent(None)
            del line
            self.scroll_area.widget().update()
            self.num_lines -= 1
        else:
            QMessageBox.warning(self, "Предупреждение", "Несуществующая строка!", QMessageBox.Ok)

    def createToolBar(self):
        self.tool_bar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)

        # Создайте QComboBox для выбора библиотеки
        self.library_combo = QComboBox()
        self.tool_bar.addWidget(self.library_combo)

        # Добавьте элементы в QComboBox
        self.library_combo.addItem("round_1.json")
        self.library_combo.addItem("round_2.json")

        # Обработчик события изменения выбранной библиотеки
        self.library_combo.currentIndexChanged.connect(self.library_changed)

        # Инициализируйте первоначальную выбранную библиотеку
        self.current_library = "round_1.json"

        simples = EventManager.get_simple_events('configs/round_1.json')
        for simple in simples:
            image_path = "textures/" + simples[simple]["Image"]
            action_button = QAction(QIcon(image_path), simple, self)
            self.tool_bar.addAction(action_button)
            action_button.triggered.connect(
                lambda _, simple=simple: self.get_widget(simple))

        # Add this line to initialize self.horizontal_lines
        self.horizontal_lines = []

    def library_changed(self, index):
        # Обработчик изменения выбранной библиотеки
        library = self.library_combo.currentText()
        if library != self.current_library:
            self.current_library = library
            self.update_toolbar_icons()

    def update_toolbar_icons(self):
        # Обновите иконки на панели инструментов на основе текущей выбранной библиотеки
        self.tool_bar.clear()
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)

        # Создайте QComboBox для выбора библиотеки
        self.library_combo = QComboBox()
        self.tool_bar.addWidget(self.library_combo)


        # Добавьте элементы в QComboBox
        self.library_combo.addItem("round_1.json")
        self.library_combo.addItem("round_2.json")

        # Обработчик события изменения выбранной библиотеки
        self.library_combo.currentIndexChanged.connect(self.library_changed)

        simples = EventManager.get_simple_events(f'configs/{self.current_library}')
        for simple in simples:
            image_path = "textures/" + simples[simple]["Image"]
            action_button = QAction(QIcon(image_path), simple, self)
            self.tool_bar.addAction(action_button)
            action_button.triggered.connect(
                lambda _, simple=simple: self.get_widget(simple))

    def updateToolBar(self):
        self.tool_bar.clear()

        current_library = self.library_combo_box.currentText()

        simples = EventManager.get_simple_events(f'configs/{current_library}')
        for simple in simples:
            image_path = f"textures/{simples[simple]['Image']}"
            action_button = QAction(QIcon(image_path), simple, self)
            self.tool_bar.addAction(action_button)
            action_button.triggered.connect(lambda _, simple=simple: self.get_widget(simple))

        self.horizontal_lines = []
    def createScrollArea(self):
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)
        self.setCentralWidget(self.scroll_area)

        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_content.setFixedWidth(maxPixelsScroll)
        self.scroll_area.setWidget(self.scroll_content)

        layout = QVBoxLayout()
        time_scale_layout = self.createTimeScaleLayout()
        layout.addLayout(time_scale_layout)

        for line in self.horizontal_lines:
            layout.addWidget(line)
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            layout.addItem(spacer)

        self.scroll_content.setLayout(layout)

        self.buttons = []

    def createTimeScaleLayout(self):
        time_scale_layout = QHBoxLayout()

        time_label = QLabel("Время")
        time_label.setFixedSize(100, 50)
        time_scale_layout.addWidget(time_label)

        for hour in range(self.start_time, self.end_time + 1):
            for minute in range(0, 60, interval):
                time_label = QLabel(f"{hour:02d}:{minute:02d}")
                time_label.setFixedSize(50, 50)
                time_scale_layout.addWidget(time_label)


                # Вычисляем пиксель, соответствующий данному времени
                pixel = int(((hour - self.start_time) * 60 + minute) * (maxPixelsScroll) / ((self.end_time - self.start_time) * 60))

                # Добавляем соответствие пикселя времени в словарь
                self.pixel_time_mapping[pixel] = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M")

                if minute < 60 - interval:
                    line = QFrame(self.scroll_content)
                    line.setFrameShape(QFrame.VLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setLineWidth(1)
                    time_scale_layout.addWidget(line)
            if hour < self.end_time:
                line = QFrame(self.scroll_content)
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                time_scale_layout.addWidget(line)
                pass

        # Возвращаем словарь и макет временной шкалы
        return time_scale_layout

    def createHorizontalLines(self):
        layout = self.scroll_area.widget().layout()

        for _ in range(self.num_lines):
            line_layout = QHBoxLayout()  # Создаем горизонтальный макет для строки
            line = QPushButton()
            line.setFixedSize(maxPixelsScroll, 50)
            self.horizontal_lines.append(line)

            # Создаем виджет с именем (QLineEdit) и устанавливаем начальное имя
            name_edit = QLineEdit("Имя полосы")  # Замените "Имя полосы" на фактическое имя
            self.horizontal_line_names.append("Имя полосы")
            name_edit.setFixedSize(100, 30)  # Установите желаемый размер для виджета с именем
            name_edit.returnPressed.connect(lambda text=name_edit.text(), line=line: self.change_name(text, line))

            line_layout.addWidget(name_edit)  # Добавляем виджет с именем (QLineEdit) в макет строки
            line_layout.addWidget(line)  # Добавляем горизонтальную полосу в макет строки

            # Добавляем строку в общий макет
            layout.addLayout(line_layout)

            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            layout.addItem(spacer)

        self.scroll_area.widget().setLayout(layout)
        return self.horizontal_lines

    def change_name(self, new_name, line):
        index = self.horizontal_lines.index(line)
        self.horizontal_lines[index - 1].setText(new_name)
        self.horizontal_line_names.append[index-1]=new_name

    def get_widget(self, simple):
        button = DraggableButton(parent=self, simple=simple)
        button.show()
        self.buttons.append(button)


def main(id):
    app = QApplication(sys.argv)
    window = RailroadStationApp(id)
    window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main(1)

