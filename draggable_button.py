# draggable_button.py
import json

from PyQt5.QtCore import QSize, Qt, QRect
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QPushButton, QCheckBox
from datetime import datetime, timedelta
import EventManager

from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout


class ButtonInfoDialog(QDialog):
    def __init__(self, button):
        super().__init__()
        self.button = button

        self.setWindowTitle("Информация о кнопке")
        self.layout = QVBoxLayout()

        self.start_time_edit = QLineEdit()
        self.start_time_edit.setText(str(self.button.start_my_time.strftime("%H:%M")))
        self.layout.addWidget(QLabel("Начальное время:"))
        self.layout.addWidget(self.start_time_edit)

        self.duration_edit = QLineEdit()
        self.duration_edit.setText(str(self.button.duration))
        self.layout.addWidget(QLabel("Длительность:"))
        self.layout.addWidget(self.duration_edit)

        self.number_train = QLineEdit()
        self.number_train.setText(str(self.button.train))
        self.layout.addWidget(QLabel("Номер поезда:"))
        self.layout.addWidget(self.number_train)

        self.flag_train = QCheckBox("Показывать номер поезда")
        self.flag_train.setChecked(self.button.train_flag)
        self.layout.addWidget(self.flag_train)

        self.description_edit = QLineEdit()
        self.description_edit.setText(self.button.description)
        self.layout.addWidget(QLabel("Описание:"))
        self.layout.addWidget(self.description_edit)

        self.apply_button = QPushButton("Применить")
        self.apply_button.clicked.connect(self.apply_changes)
        self.layout.addWidget(self.apply_button)

        self.delete_button = QPushButton("Удалить")
        self.delete_button.clicked.connect(self.delete_button_clicked)  # Измените здесь имя слота
        self.layout.addWidget(self.delete_button)

        self.setLayout(self.layout)

    def delete_button_clicked(self):  # Измененное имя метода
        self.button.setParent(None)
        self.button.my_parent.buttons.remove(self.button)
        self.accept()

    def apply_changes(self):
        # Примените изменения к параметрам кнопки
        new_start_time = self.start_time_edit.text()
        new_duration = self.duration_edit.text()
        new_description = self.description_edit.text()
        new_flag_train = self.flag_train.isChecked()
        new_train = self.number_train.text()

        # Обновите параметры кнопки
        if str(self.button.start_my_time.strftime("%H:%M")) or self.button.description != new_description:
            self.button.train = new_train
            self.button.duration = int(new_duration)
            self.button.description = new_description
            start_my_time = datetime.strptime(new_start_time, "%H:%M")
            delta = timedelta(minutes=int(self.button.duration))
            end_my_time = start_my_time + delta
            self.button.start_my_time = start_my_time
            self.button.end_my_time = end_my_time
            self.button.get_coordinates_by_time(start_my_time, end_my_time)
        #######
        if not new_flag_train:
            self.button.hide_train_label()
        self.button.train_flag = new_flag_train
        # Закройте диалоговое окно
        self.accept()

    def delete_button(self):
        # Удалите кнопку из интерфейса
        self.button.deleteLater()
        self.accept()


class DraggableButton(QPushButton):
    def __init__(self, parent=None, simple=None, line_index=None, time_now=None, pixel_time_mapping=None):
        # Добавить сюда вот parent.scroll_area.widget().layout()
        super().__init__(parent.scroll_content)  # Устанавливаем виджет-родитель
        self.my_parent = parent
        self.pixel_time_mapping = pixel_time_mapping
        simples = EventManager.get_simple_events()
        self.simple = simple
        self.train = 5
        self.train_flag = True
        self.duration = simples[simple]["Time"]
        self.description = simples[simple]["Description"]
        self.load_constants_from_json()
        self.setMouseTracking(True)
        self.start_my_time = ""
        self.end_my_time = ""
        start_time_scroll = self.my_parent.start_time
        end_time_scroll = self.my_parent.end_time

        self.setFixedHeight(49)  # Устанавливает высоту кнопки равной 50 пикселям

        self.time_label = QLabel(parent.scroll_content)  # Создаем QLabel с родительским виджетом
        self.time_label.setAlignment(Qt.AlignCenter)  # Устанавливаем выравнивание текста по центру
        self.show_time_label("")

        self.train_label = QLabel(parent.scroll_content)  # Создаем QLabel с родительским виджетом
        self.train_label.setAlignment(Qt.AlignCenter)  # Устанавливаем выравнивание текста по центру


        self.line_index = line_index

        if self.line_index is not None:
            self.move(self.x(), self.get_middle_y_coordinate_line(self.my_parent.horizontal_lines[line_index]))

        if time_now is None:
            self.start_my_time = datetime.strptime(f"{start_time_scroll}:00", "%H:%M")
            self.end_my_time = datetime.strptime(f"{start_time_scroll}:00", "%H:%M") + timedelta(minutes=self.duration)
            self.get_coordinates_by_time(self.start_my_time, self.end_my_time)
        else:
            self.start_my_time = datetime.strptime(time_now[0], "%H:%M")
            self.end_my_time = datetime.strptime(time_now[1], "%H:%M")
            time_difference = self.end_my_time - self.start_my_time
            self.duration = int(time_difference.total_seconds() / 60)
            self.get_coordinates_by_time(self.start_my_time, self.end_my_time)

        image_path = "textures/" + simples[simple]["Image"]
        self.setStyleSheet(f"QPushButton {{"
                           f"border-image: url('{image_path}') center center;"
                           f"}}")
        #self.setIconSize(self.size())  # Установите размер иконки равным размеру кнопки
        self.dragging = False
        self.offset = None
        self.error = False
        if self.error:
            self.setStyleSheet("background-color: red;")

        # self.horizontal_lines = horizontal_lines
        self.setWindowFlags(Qt.WindowStaysOnTopHint)
        # self.event_time_minutes = event_time_minutes
        self.show_train_label()

    def show_time_label(self, text):
        # Устанавливаем текст и позицию QLabel рядом с кнопкой
        label_width = self.time_label.width()
        label_height = self.time_label.height()
        button_x = self.geometry().x()
        button_y = self.geometry().y()
        label_x = button_x  # 5 - отступ между кнопкой и текстом
        label_y = button_y - 40  # Центрируем текст по вертикали относительно кнопки
        self.time_label.setGeometry(label_x, label_y, label_width, label_height)
        try:
            self.time_label.setText(text[0].strftime("%H:%M"))
        except Exception:
            self.time_label.setText("-")

        self.time_label.show()

    def show_train_label(self):
        if self.train_flag:
            button_x = self.geometry().x()
            button_y = self.geometry().y()
            label_x = button_x - 5  # 5 - отступ между кнопкой и текстом
            label_y = button_y - 40  # Центрируем текст по вертикали относительно кнопки
            self.train_label.setGeometry(label_x, label_y, 10, 40)
            try:
                self.train_label.setText(str(self.train))
            except Exception:
                self.train_label.setText("-")

            self.train_label.show()
        else:
            self.train_label.setText("")
            self.hide_train_label()

    def hide_train_label(self):
        # Скрываем QLabel
        self.time_label.hide()
        self.time_label.setText("")

    def hide_time_label(self):
        # Скрываем QLabel
        self.time_label.hide()

    def open_info_dialog(self):
        dialog = ButtonInfoDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            # Действие после закрытия диалогового окна
            pass

    def refresh_line(self):

        if (self.line_index != -1):
            middle_y = self.my_parent.horizontal_lines[self.line_index].geometry().center().y() - self.height() // 2
            self.move(self.x(), middle_y)
        self.show_train_label()

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
            start_pixel = (start_time - self.my_parent.pixel_time_mapping[
                start_dict]).total_seconds() // 60 + start_dict
            end_pixel = ((end_time - start_time).total_seconds() // 60) * pixels_on_min + start_pixel

            button_width = int(self.duration) * pixels_on_min
            self.setGeometry(int(start_pixel + self.width() // 2), int(self.geometry().y()), int(button_width), int(self.height()))

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
            global start_time_scroll
            start_time_scroll = self.my_parent.pixel_time_mapping[start_dict]
            start_time_global = start_time_scroll + timedelta(minutes=start_time_button)
            end_time_global = start_time_scroll + timedelta(minutes=end_time_button)

            return start_time_global, end_time_global
        except Exception:
            return (datetime.min, datetime.min)

    def mousePressEvent(self, event):
        if event.button() == Qt.RightButton:
            self.open_info_dialog()
        if event.button() == Qt.LeftButton:
            self.dragging = True
            self.offset = event.pos()

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

    def mouseMoveEvent(self, event):
        self.show_train_label()
        if self.dragging:
            self.show_time_label(self.get_coordinate())
            new_pos = self.mapToParent(event.pos() - self.offset)
            for index, line in enumerate(self.my_parent.horizontal_lines):
                if line.geometry().contains(new_pos):
                    new_pos.setY(int(line.geometry().center().y() - self.height() // 2))
                    self.line_index = index
                    print(index)
                    self.my_line = index
                    break
            else:
                self.line_index = -1

            for button in self.my_parent.buttons:
                duration_dt = self.end_my_time - self.start_my_time
                if self.line_index == button.line_index and button != self:
                    print(button.simple, (self.start_my_time - button.end_my_time).total_seconds() // 60,
                          (self.end_my_time - button.start_my_time).total_seconds() // 60)

                    interval_start_to_end = (self.start_my_time - button.end_my_time).total_seconds() // 60
                    interval_end_to_start = (self.end_my_time - button.start_my_time).total_seconds() // 60

                    if -5 <= interval_start_to_end <= 10:
                        # Устанавливаем новую позицию для текущей кнопки
                        new_x = button.geometry().right() + 1

                        new_pos.setX(new_x)
                    elif -5 <= interval_end_to_start <= 10:
                        new_x = button.geometry().left() - self.width()

                        # Устанавливаем новую позицию для текущей кнопки
                        new_pos.setX(new_x)
            self.move(new_pos)

    def nearest_button(self):
        for button in self.my_parent.buttons:
            if button != self:
                left_edge = self.geometry().left()
                right_edge = self.geometry().right()
                button_left_edge = button.geometry().left()
                button_right_edge = button.geometry().right()

                if abs(left_edge - button_right_edge) < 40:
                    # Притягиваем текущую кнопку к кнопке button справа
                    self.move(button_right_edge + 1, self.geometry().top())
                elif abs(right_edge - button_left_edge) < 40:
                    # Притягиваем текущую кнопку к кнопке button слева
                    self.move(button_left_edge - self.width() - 1, self.geometry().top())

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self.dragging = False
            self.hide_time_label()
            self.start_my_time, self.end_my_time = self.get_coordinate()
