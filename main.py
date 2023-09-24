import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QToolBar, QAction, QPushButton, QWidget, QScrollArea, QVBoxLayout, QHBoxLayout, QLabel, QFrame, QSpacerItem, QSizePolicy, QInputDialog
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QIcon


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

        exitAction = QAction('Выйти', self)
        exitAction.setShortcut('Ctrl+Q')
        exitAction.setStatusTip('Выйти из приложения')
        exitAction.triggered.connect(self.close)

        menubar = self.menuBar()
        fileMenu = menubar.addMenu('Файл')
        fileMenu.addAction(exitAction)

        FullscreenAction = QAction('Полноэкранный режим', self)
        FullscreenAction.setStatusTip('Полноэкранноый режим')
        FullscreenAction.triggered.connect(self.showFullScreen)

        exitFullscreenAction = QAction('Выйти из полноэкранного режима', self)
        exitFullscreenAction.setStatusTip('Выйти из полноэкранного режима')
        exitFullscreenAction.triggered.connect(self.showNormal)

        viewMenu = menubar.addMenu('Вид')
        viewMenu.addAction(exitFullscreenAction)
        viewMenu.addAction(FullscreenAction)

        canvasMenu = menubar.addMenu('Полотно')
        addHorizontalLineAction = QAction('Добавить горизонтальную полосу', self)
        addHorizontalLineAction.triggered.connect(self.add_horizontal_line)
        canvasMenu.addAction(addHorizontalLineAction)

        removeHorizontalLineAction = QAction('Удалить горизонтальную полосу', self)
        removeHorizontalLineAction.triggered.connect(self.remove_horizontal_line)
        canvasMenu.addAction(removeHorizontalLineAction)

        self.tool_bar = QToolBar()
        self.addToolBar(Qt.LeftToolBarArea, self.tool_bar)

        simples = EventManager.get_simple_events()
        for simple in simples:
            image_path = simples[simple]["Image"]
            action_button = QAction(QIcon(image_path), simple, self)
            self.tool_bar.addAction(action_button)

            action_button.triggered.connect(lambda _, path=image_path, time=simples[simple]["Time"]: self.get_widget(path, time))

        # Создаем виджет с прокруткой
        self.scroll_area = QScrollArea(self)
        self.scroll_area.setWidgetResizable(True)  # Разрешаем прокрутку содержимого
        self.setCentralWidget(self.scroll_area)

        # Создаем виджет для содержимого (горизонтальные полосы и временная шкала)
        self.scroll_content = QWidget(self.scroll_area)
        self.scroll_content.setFixedWidth(maxPixelsScroll)
        self.scroll_area.setWidget(self.scroll_content)

        # Устанавливаем вертикальное распределение полос и временной шкалы
        layout = QVBoxLayout()

        # Создаем временную шкалу с интервалом
        time_scale_layout = QHBoxLayout()
        for hour in range(start_time, end_time + 1):
            for minute in range(0, 60, interval):
                time_label = QLabel(f"{hour:02d}:{minute:02d}")
                time_label.setFixedSize(50, 50)  # Уменьшаем размер метки времени
                time_scale_layout.addWidget(time_label)

                # Добавляем вертикальную линию между интервалами (кроме последнего интервала)
                if minute < 60 - interval:
                    line = QFrame(self.scroll_content)
                    line.setFrameShape(QFrame.VLine)
                    line.setFrameShadow(QFrame.Sunken)
                    line.setLineWidth(1)  # Уменьшаем жирность линии
                    time_scale_layout.addWidget(line)

            # Добавляем вертикальную линию между часами (кроме последнего часа)
            if hour < end_time:
                line = QFrame(self.scroll_content)
                line.setFrameShape(QFrame.VLine)
                line.setFrameShadow(QFrame.Sunken)
                time_scale_layout.addWidget(line)

        layout.addLayout(time_scale_layout)

        # Создаем горизонтальные полосы
        self.horizontal_lines = []
        for _ in range(6):
            line = QPushButton("")
            line.setFixedSize(maxPixelsScroll, 50)  # Устанавливаем размер кнопки
            self.horizontal_lines.append(line)
            layout.addWidget(line)

        self.scroll_content.setLayout(layout)

        # Список для хранения созданных кнопок
        self.buttons = []

    def get_widget(self, image_path, event_time_minutes):
        button = DraggableButton(image_path, self.scroll_content, self.horizontal_lines, event_time_minutes)
        # Установите координаты размещения кнопки внутри self.scroll_content
        button.setGeometry(0, 0, 150, 50)
        button.show()
        # Сохраняем ссылку на созданную кнопку
        self.buttons.append(button)

    def add_horizontal_line(self):
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

class DraggableButton(QPushButton):
    def __init__(self, image_path, parent=None, horizontal_lines=None, event_time_minutes=0):
        super().__init__(parent)
        self.setMouseTracking(True)
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(50, 50))

        self.dragging = False
        self.offset = None
        self.horizontal_lines = horizontal_lines  # Передаем список горизонтальных полос
        self.setWindowFlags(Qt.WindowStaysOnTopHint)  # Устанавливаем флаг, чтобы оставаться на переднем плане
        self.event_time_minutes = event_time_minutes

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            print("Тут новое окошко для настроен")
            self.offset = event.pos()

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            # Вычисляем ширину кнопки на основе времени в минутах и максимальной длины скролл-бара
            button_width = int(self.event_time_minutes / (end_time * 60 - start_time * 60) * maxPixelsScroll)
            self.setFixedSize(button_width, 50)
            # Центрирование кнопки только по вертикали относительно горизонтальных полос
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