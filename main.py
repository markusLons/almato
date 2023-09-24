import os
import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QPushButton, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QInputDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMessageBox
import json

import EventManager

# Указываем время начала и конца отчета, а также интервал
start_time = 8
end_time = 22
interval = 10
maxPixelsScroll = 10000

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
        loadAction.triggered.connect(self.load_state)
        fileMenu.addAction(loadAction)

        # Создаем меню "Вид" и добавляем в него действия
        viewMenu = self.menuBar().addMenu('Вид')
        viewMenu.addAction(FullscreenAction)
        viewMenu.addAction(exitFullscreenAction)

        # Создаем меню "Полотно" и добавляем в него действия
        canvasMenu = self.menuBar().addMenu('Полотно')
        addHorizontalLineAction = QAction('Добавить горизонтальную полосу', self)
        addHorizontalLineAction.triggered.connect(self.add_horizontal_line)
        canvasMenu.addAction(addHorizontalLineAction)

        removeHorizontalLineAction = QAction('Удалить горизонтальную полосу', self)
        removeHorizontalLineAction.triggered.connect(self.remove_horizontal_line)
        canvasMenu.addAction(removeHorizontalLineAction)

    def save_state(self):
        widget_coords = [(widget.geometry().x(), widget.geometry().y()) for widget in self.buttons]
        self.state['widgets'] = [{'path': self.current_image_path, 'coords': coords} for coords in widget_coords]
        self.state['num_lines'] = self.num_lines  # Добавляем количество полос

        try:
            # Пытаемся удалить существующий файл
            os.remove('state.json')
        except FileNotFoundError:
            pass  # Если файл не найден, ничего не делаем

        with open('state.json', 'w') as file:
            json.dump(self.state, file)

    def load_state(self):
        try:
            with open('state.json', 'r') as file:
                self.state = json.load(file)

                for widget_data in self.state['widgets']:
                    image_path = widget_data['path']
                    coords = widget_data['coords']
                    button = DraggableButton(image_path, self.scroll_content, self.horizontal_lines)
                    button.setGeometry(coords[0], coords[1], 150, 50)  # Устанавливаем координаты и размеры кнопки
                    self.buttons.append(button)

                if 'num_lines' in self.state:
                    self.num_lines = self.state['num_lines']  # Восстанавливаем количество полос
                    self.horizontal_lines = self.createHorizontalLines()  # Создаем и сохраняем горизонтальные линии


        except Exception as e:
            print(f"An error occurred while loading state: {e}")

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
        return time_scale_layout

    def createHorizontalLines(self):
        for widget in self.horizontal_lines:
            widget.setParent(None)
        self.horizontal_lines.clear()
        
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

    def get_widget(self, image_path, event_time_minutes):
        self.current_image_path = image_path
        button = DraggableButton(image_path, self.scroll_content, self.horizontal_lines, event_time_minutes)
        button.setGeometry(0, 0, 150, 50)
        button.show()
        self.buttons.append(button)

    def add_horizontal_line(self):
        if self.horizontal_lines is None:
            self.horizontal_lines = []  # Initialize it if it's None
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

    def remove_horizontal_line(self):
        index, ok = QInputDialog.getInt(self, 'Введите индекс полосы:', 'Индекс:')
        if ok:
            if 0 <= index < len(self.horizontal_lines):
                line = self.horizontal_lines.pop(index)
                line.setParent(None)
                del line
                for i, line in enumerate(self.horizontal_lines):
                    line.setText(f"Schedule Line {i + 1}")
                self.scroll_area.widget().update()
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

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            button_width = int(self.event_time_minutes / (end_time * 60 - start_time * 60) * maxPixelsScroll)
            self.setFixedSize(button_width, 50)
            for line in self.horizontal_lines:
                if line.geometry().contains(new_pos):
                    new_pos.setY(int(line.geometry().center().y() - self.height() / 2))
                    break
            self.move(new_pos)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = RailroadStationApp()
    window.show()
    sys.exit(app.exec_())