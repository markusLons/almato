import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QPushButton, QWidget, QScrollArea, \
    QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QInputDialog, QMenu
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import json
from datetime import datetime, timedelta

user_id
import EventManager

# Указываем время начала и конца отчета, а также интервал
start_time = 8
end_time = 22
interval = 10
maxPixelsScroll = 10000
pixel_time_mapping = {}

def get_end_coordinate(button):
    current_x = button.geometry().x()
    button_width = button.width()
    end_x = current_x + button_width
    start_dict = -1
    ens_dict = -1
    before_i = -1
    for i in pixel_time_mapping.keys():
        if i >= start_dict and start_dict == -1:
            start_dict = before_i
        if i > end_x:
            ens_dict = i
            break
        before_i = i
    try:
        pixels_on_min = (ens_dict - start_dict) / ((pixel_time_mapping[ens_dict] - pixel_time_mapping[start_dict]).total_seconds() // 60)
        start_time_button = (current_x - start_dict)//pixels_on_min
        end_time_button = (current_x - start_dict + button_width) // pixels_on_min
    except Exception:
        return ("00", "00")

    return (start_time_button, end_time_button)


class RailroadStationApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Железнодорожная станция")
        self.setGeometry(100, 100, 800, 600)
        self.showFullScreen()

        self.state = {'horizontal_lines': [], 'widgets': []}
        self.current_image_path = None

        self.num_lines = 0
        self.horizontal_lines = []

        self.initUI()

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

    def set_button_position(self, button, start_time_minutes, line_index):
        """
        Устанавливает позицию кнопки на основе времени и индекса линии.

        :param button: Кнопка, для которой устанавливается позиция.
        :param start_time_minutes: Время начала события в минутах с начала дня.
        :param line_index: Индекс линии, на которой должна располагаться кнопка.
        """
        # Установка позиции кнопки на основе времени и индекса линии
        pixel = int(start_time_minutes / ((end_time - start_time) * 60) * maxPixelsScroll)
        line_height = 50 * line_index
        button_width = int((end_time - start_time) * 60 / maxPixelsScroll * button.width())
        button.setGeometry(pixel, line_height, button_width, 50)
        button.line_index = line_index  # Устанавливаем индекс линии
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
        addHorizontalLineAction1.setShortcut('Ctrl+G')
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

    def save_state(self):
        state = {}  # Создаем пустой словарь для сохранения состояния

        # Создаем список для хранения информации о кнопках
        buttons_info = []

        for i, button in enumerate(self.buttons):
            start_time, end_time = get_end_coordinate(button)
            button_info = {
                'index': i,  # Порядковый номер кнопки
                'name': button.text(),  # Название кнопки (предполагается, что текст кнопки содержит имя)
                'start_time': start_time,  # Время начала
                'end_time': end_time,  # Время окончания
                'line_index': button.line_index,  # Номер строки, на которой находится кнопка
                'image_path': self.current_image_path,  # Путь к изображению
            }
            buttons_info.append(button_info)

        state['buttons'] = buttons_info  # Добавляем информацию о кнопках в состояние
        state['num_lines'] = self.num_lines  # Добавляем количество полос

        json_state = json.dumps(state, indent=4, ensure_ascii=False)

        # Теперь вы можете использовать json_state как строку или сохранить ее в переменной
        print("Состояние успешно сохранено:")
        print(json_state)
        # Теперь можно сохранить состояние в файл JSON
        try:
            with open('state.json', 'w') as file:
                json.dump(state, file, indent=4, ensure_ascii=False)
                print("Состояние успешно сохранено в файл 'state.json'")
        except Exception as e:
            print(f"Ошибка при сохранении состояния: {e}")

    def load_state_from_data(self, state_data):
        try:
            # Очищаем текущее состояние
            self.clear_current_state()

            # Восстанавливаем состояние из данных
            self.num_lines = state_data.get('num_lines', 0)
            self.horizontal_lines = self.createHorizontalLines()

            buttons_info = state_data.get('buttons', [])
            for button_info in buttons_info:
                image_path = button_info.get('image_path')
                event_time_minutes = button_info.get('end_time') - button_info.get('start_time')
                button = DraggableButton(image_path, self.scroll_content, self.horizontal_lines, event_time_minutes)
                button.setGeometry(0, 0, 150, 50)
                button.show()
                self.buttons.append(button)
                self.set_button_position(button, button_info.get('start_time'), button_info.get('line_index'))

            self.current_image_path = state_data.get('current_image_path', None)

            QMessageBox.information(self, "Загрузка состояния", "Состояние успешно загружено.")

        except Exception as e:
            QMessageBox.warning(self, "Ошибка загрузки", f"Произошла ошибка при загрузке состояния: {str(e)}")

    def createToolBar(self):
        self.tool_bar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)

        simples = EventManager.get_simple_events()
        for simple in simples:
            image_path = simples[simple]["Image"]
            action_button = QAction(QIcon(image_path), simple, self)
            self.tool_bar.addAction(action_button)
            action_button.triggered.connect(
                lambda _, path=image_path, time=simples[simple]["Time"]: self.get_widget(path, time))

        # Add this line to initialize self.horizontal_lines
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

        for hour in range(start_time, end_time + 1):
            for minute in range(0, 60, interval):
                time_label = QLabel(f"{hour:02d}:{minute:02d}")
                time_label.setFixedSize(50, 50)
                time_scale_layout.addWidget(time_label)

                # Вычисляем пиксель, соответствующий данному времени
                pixel = int(((hour - start_time) * 60 + minute) * maxPixelsScroll / ((end_time - start_time) * 60))

                # Добавляем соответствие пикселя времени в словарь
                pixel_time_mapping[pixel] = datetime.strptime(f"{hour:02d}:{minute:02d}", "%H:%M")

                if minute < 60 - interval:
                    line = QFrame(self.scroll_content)
                    line.setFrameShape(QFrame.VLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setLineWidth(1)
                    time_scale_layout.addWidget(line)
            if hour < end_time:
                line = QFrame(self.scroll_content)
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                time_scale_layout.addWidget(line)

        # Возвращаем словарь и макет временной шкалы
        return time_scale_layout

    def createHorizontalLines(self):
        for widget in self.horizontal_lines:
            widget.setParent(None)
        self.horizontal_lines.clear()
        if self.horizontal_lines is None:
            self.horizontal_lines = []

        self.count_gorisontal_line = self.num_lines
        layout = self.scroll_area.widget().layout()
        for _ in range(self.num_lines):
            line = QPushButton()
            line.setFixedSize(maxPixelsScroll, 50)
            self.horizontal_lines.append(line)
            pass
            layout.addWidget(line)
            spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
            layout.addItem(spacer)
        self.scroll_area.widget().setLayout(layout)
        return self.horizontal_lines

    def get_widget(self, image_path, event_time_minutes):
        self.current_image_path = image_path
        button = DraggableButton(image_path, self.scroll_content, self.horizontal_lines, event_time_minutes)
        button.setGeometry(0, 0, 150, 50)
        button.show()
        self.buttons.append(button)

    def add_horizontal_line(self):
        #if self.horizontal_lines is None:
        #    self.horizontal_lines = []  # Initialize it if it's None
        user_input, ok = QInputDialog.getInt(self, 'Введите количество полос', 'Количество:')
        if ok:
            self.count_gorisontal_line = user_input
            layout = self.scroll_area.widget().layout()
            for _ in range(user_input):
                line = QPushButton()
                line.setFixedSize(maxPixelsScroll, 50)
                self.horizontal_lines.append(line)
                layout.addWidget(line)
                spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
                layout.addItem(spacer)
            self.scroll_area.widget().setLayout(layout)
            self.num_lines += user_input  # Обновляем количество полос

    def add_horizontal_line1(self):
        self.count_gorisontal_line = 1
        layout = self.scroll_area.widget().layout()
        line = QPushButton()
        line.setFixedSize(maxPixelsScroll, 50)
        self.horizontal_lines.append(line)
        layout.addWidget(line)
        spacer = QSpacerItem(0, 0, QSizePolicy.Expanding, QSizePolicy.Minimum)
        layout.addItem(spacer)
        self.scroll_area.widget().setLayout(layout)
        self.num_lines += 1

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


class DraggableButton(QPushButton):
    def __init__(self, image_path, parent=None, horizontal_lines=None, event_time_minutes=0):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(50, 50))
        self.dragging = False
        self.offset = None
        self.horizontal_lines = horizontal_lines
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.event_time_minutes = event_time_minutes
        self.line_index = -1  # Добавляем атрибут line_index

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            button_width = int(self.event_time_minutes / (end_time * 60 - start_time * 60) * maxPixelsScroll)
            self.setFixedSize(button_width, 50)
            for index, line in enumerate(self.horizontal_lines):
                if line.geometry().contains(new_pos):
                    new_pos.setY(int(line.geometry().center().y() - self.height() / 2))
                    self.line_index = index  # Устанавливаем line_index
                    break
            else:
                self.line_index = -1  # Если не найдена линия, сбрасываем line_index
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False



if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RailroadStationApp()
    state_data = json.loads("""{
    "buttons": [
        {
            "index": 0,
            "name": "",
            "start_time": 5.0,
            "end_time": 19.0,
            "line_index": 0,
            "image_path": "Отправление.png"
        }
    ],
    "num_lines": 12
}""")
    window.load_state_from_data(state_data)
    # if len(sys.argv) == 2:
    #     # Если аргументов командной строки 2, то предполагаем, что первый аргумент - это JSON-строка.
    #     json_string = sys.argv[1]
    #
    #     # Попробуйте загрузить JSON-строку и обновить состояние приложения
    #     try:
    #         state_data = json.loads(json_string)
    #         window.load_state_from_data(state_data)
    #     except json.JSONDecodeError as e:
    #         QMessageBox.warning(window, "Ошибка загрузки", f"Ошибка при разборе JSON: {str(e)}")

    window.show()
    sys.exit(app.exec_())
