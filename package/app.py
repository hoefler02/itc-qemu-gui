from PySide2.QtWidgets import QApplication 
from package.mainwindow import MainWindow

def run():
    app = QApplication()
    window = MainWindow(app)
    app.exec_()
