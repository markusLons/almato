# main.py
import json
import sys
from PyQt5.QtWidgets import QApplication
import railroad_station_app

if __name__ == "__main__":
    print(sys.argv[1])
    railroad_station_app.main(sys.argv[1], sys.argv[2], sys.argv[3])

