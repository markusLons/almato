from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenuBar, QMenu, QTableWidget, QTableWidgetItem
from PyQt5.QtGui import QPalette, QColor
import sys


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
        menubar.setStyleSheet("background-color: rgb(0, 0, 100); color: white; font-size: 19px;")

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

        table.setColumnWidth(0, 150)  # Первый столбец
        table.setColumnWidth(1, 150)  # Второй столбец
        table.setColumnWidth(2, 180)  # Третий столбец

        table.show()

    def contextMenuEvent(self, event):
        context_menu = QMenu(self)
        show_summary_action = context_menu.addAction("Показать сводную таблицу")
        show_summary_action.triggered.connect(self.showSummaryTable)
        context_menu.exec_(event.globalPos())

def main():
    app = QApplication(sys.argv)
    report_window = ReportWindow()
    report_window.show()
    sys.exit(app.exec_())

if __name__ == "__main__":
    main()
