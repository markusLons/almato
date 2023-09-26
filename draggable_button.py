# draggable_button.py
import json

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QMenu
from PyQt5.QtGui import QPixmap


class DraggableButton(QPushButton):
    def __init__(self, image_path, parent=None, horizontal_lines=None, event_time_minutes=0, name=""):
        super().__init__(parent)
        self.name = name
        self.load_constants_from_json()
        self.setMouseTracking(True)
        self.setIcon(QIcon(image_path))
        self.setIconSize(QSize(50, 50))
        self.dragging = False
        self.offset = None
        self.horizontal_lines = horizontal_lines
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        self.event_time_minutes = event_time_minutes
        self.line_index = -1

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()
    def load_constants_from_json(self):
        try:
            # Открываем файл mapConstant.json и читаем константы
            with open('mapConstant.json', 'r') as json_file:
                constants = json.load(json_file)

            # Задаем значения константам
            global user_id, map_id, start_time, end_time, interval, maxPixelsScroll
            user_id = constants["user_id"]
            map_id = constants["map_id"]
            start_time = constants["start_time"]
            end_time = constants["end_time"]
            interval = constants["interval"]
            maxPixelsScroll = constants["maxPixelsScroll"]

        except Exception as e:
            print(f"Ошибка при загрузке констант из JSON: {e}")
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
