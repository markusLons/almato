# draggable_button.py
import json

from PyQt5.QtCore import QSize, Qt, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton
from datetime import datetime, timedelta
import EventManager


class DraggableButton(QPushButton):
    def __init__(self, parent=None, simple = None, line_index = None, time_now = None, pixel_time_mapping = None):
        super().__init__(parent)
        self.my_parent = parent
        self.pixel_time_mapping = pixel_time_mapping
        simples = EventManager.get_simple_events()
        self.simple = simple
        self.duration = simples[simple]["Time"]
        self.description = simples[simple]["Description"]
        self.load_constants_from_json()
        self.setMouseTracking(True)
        self.start_my_time = ""
        self.end_my_time = ""
        self.line_index = line_index

        if self.line_index is not None:
            self.move(self.x(), self.get_middle_y_coordinate_line(self.my_parent.horizontal_lines[line_index]))

        if time_now is None:
            self.setGeometry(0, 0, 150, 50)
            self.start_my_time = datetime.strptime(f"{start_time_scroll}:00", "%H:%M")
        else:
            self.start_my_time = datetime.strptime(time_now[0], "%H:%M")
            self.end_my_time = datetime.strptime(time_now[1], "%H:%M")
            self.get_coordinates_by_time(self.start_my_time, self.end_my_time)

        self.setIcon(QIcon(simples[simple]["Image"]))
        self.setIconSize(QSize(50, 50))
        self.dragging = False
        self.offset = None
        #self.horizontal_lines = horizontal_lines
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        #self.event_time_minutes = event_time_minutes
    def refresh_line(self):
        if(self.line_index != -1):
            middle_y = self.my_parent.horizontal_lines[self.line_index].geometry().center().y()
            self.move(self.x(), middle_y)

    def get_middle_y_coordinate_line(self, line):
        middle_y = line.geometry().center().y()
        return middle_y


    def get_coordinates_by_time(self, start_time, end_time):

        start_dict = -1
        ens_dict = -1
        before_i = -1

        for i, time in self.my_parent.pixel_time_mapping.items():
            if time >= start_time and start_dict == -1:
                start_dict = before_i
            if time > end_time:
                ens_dict = i
                break
            before_i = i

        try:
            pixels_on_min = (ens_dict - start_dict) / (
                    (self.my_parent.pixel_time_mapping[ens_dict] - self.my_parent.pixel_time_mapping[
                        start_dict]).total_seconds() // 60)
            start_pixel = (start_time - self.my_parent.pixel_time_mapping[start_dict] ).total_seconds() //60 +  start_dict
            end_pixel = ((end_time - start_time).total_seconds() // 60) * pixels_on_min + start_pixel

            button_width = end_pixel - start_pixel
            self.setGeometry(start_pixel, self.geometry().y(), button_width, self.height())

        except Exception as e:
            print(f"Ошибка при вычислении координат: {e}")

    def get_coordinate(self):
        current_x = self.geometry().x()
        button_width = self.width()
        end_x = current_x + button_width
        start_dict = -1
        ens_dict = -1
        before_i = -1

        for i in self.my_parent.pixel_time_mapping.keys():
            if i >= start_dict and start_dict == -1:
                start_dict = before_i
            if i > end_x:
                ens_dict = i
                break
            before_i = i

        try:
            pixels_on_min = (ens_dict - start_dict) / (
                    (self.my_parent.pixel_time_mapping[ens_dict] - self.my_parent.pixel_time_mapping[
                        start_dict]).total_seconds() // 60)

            start_time_button = int((current_x - start_dict) // pixels_on_min)
            end_time_button = int((current_x - start_dict + button_width) // pixels_on_min)

            start_time_scroll = self.my_parent.pixel_time_mapping[start_dict]
            start_time_global = start_time_scroll + timedelta(minutes=start_time_button)
            end_time_global = start_time_scroll + timedelta(minutes=end_time_button)

            return start_time_global, end_time_global
        except Exception:
            return (datetime.min, datetime.min)

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
            global user_id, map_id, start_time_scroll, end_time_scroll, interval, maxPixelsScroll
            user_id = constants["user_id"]
            map_id = constants["map_id"]
            start_time_scroll = constants["start_time"]
            end_time_scroll = constants["end_time"]
            interval = constants["interval"]
            maxPixelsScroll = constants["maxPixelsScroll"]

        except Exception as e:
            print(f"Ошибка при загрузке констант из JSON: {e}")

    def mouseMoveEvent(self, event):
        if self.dragging:
            new_pos = self.mapToParent(event.pos() - self.offset)
            for index, line in enumerate(self.my_parent.horizontal_lines):
                if line.geometry().contains(new_pos):
                    new_pos.setY(int(line.geometry().center().y() ))
                    self.line_index = index
                    print(index)
                    self.my_line = index
                    break
            else:
                self.line_index = -1
            self.move(new_pos)
    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False


