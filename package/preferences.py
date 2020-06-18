from PySide2.QtWidgets import QMainWindow, QCheckBox, QWidget
from PySide2.QtGui import QPalette, QColor, QGuiApplication
from PySide2.QtCore import Qt

class Preferences(QWidget):

    def __init__(self, app, default):

        QWidget.__init__(self)

        self.app = app

        self.default = default

        self.init_ui()
        self.show()
    
    def init_ui(self):

        self.setWindowTitle('Preferences')
        self.setGeometry(100, 100, 200, 60)


        self.darkmode = QCheckBox('Dark Mode', self)

        self.app.setStyle("Fusion")

        if QGuiApplication.palette() != self.default:
            self.darkmode.setChecked(True)

        palette = QPalette()
        palette.setColor(QPalette.Window, QColor(25, 25, 25)) # 53 53 53
        palette.setColor(QPalette.WindowText, Qt.white)
        palette.setColor(QPalette.Base, QColor(53, 53, 53)) # 25 25 25
        palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
        palette.setColor(QPalette.ToolTipBase, Qt.white)
        palette.setColor(QPalette.ToolTipText, Qt.white)
        palette.setColor(QPalette.Text, Qt.white)
        palette.setColor(QPalette.Button, QColor(53, 53, 53))
        palette.setColor(QPalette.ButtonText, Qt.white)
        palette.setColor(QPalette.BrightText, Qt.red)
        palette.setColor(QPalette.Link, QColor(42, 130, 218))
        palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
        palette.setColor(QPalette.HighlightedText, Qt.black)

        self.darkmode.toggled.connect(lambda:self.app.setPalette(palette) if self.darkmode.isChecked() else self.app.setPalette(self.default))

        self.darkmode.move(20, 20)
            