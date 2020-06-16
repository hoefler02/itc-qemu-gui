
from PySide2.QtWidgets import QMainWindow, QAction, QGridLayout, QPushButton, QWidget, QErrorMessage, QMessageBox, QLabel
from PySide2.QtCore import QSize, Slot
from PySide2.QtGui import QIcon, QFont
from PySide2.QtCore import QSize, Slot
from PySide2.QtGui import QIcon 

from package.memdumpwindow import MemDumpWindow
from package.registerview import RegisterView
from package.errorwindow import ErrorWindow
from package.qmpwrapper import QMP
from package.preferences import Preferences
from package.memtree import MemTree

from datetime import datetime
import threading
import time

class MainWindow(QMainWindow):

    def __init__(self, app):

        self.app = app
 
        self.qmp = QMP('localhost', 55555)
        self.qmp.start()

        self.qmp.stateChanged.connect(self.handle_pause_button)
        self.paused = False

        super().__init__()
        self.init_ui()

        self.qmp.timeUpdate.connect(self.update_time)
        self.t = TimeThread(self.qmp)
        self.t.start()

        self.window = {}

    def init_ui(self):

        # Window Setup
        self.setWindowTitle("QEMU Control")
        self.setGeometry(100, 100, 400, 300) # x, y, w, h 

        # App Icon
        icon = QIcon('package/icons/nasa.png')
        self.setWindowIcon(icon)

        # User Interface
        self.menu_bar()
        self.grid_layout()

        self.show()

    def menu_bar(self):

        bar = self.menuBar()

        # Menu Bar Actions
        file_ = bar.addMenu("File")
        edit = bar.addMenu("Edit")
        run = bar.addMenu("Run")
        tools = bar.addMenu("Tools")
        help_ = bar.addMenu("Help")

        # File Menu Options
        open_ = QAction("Open Image", self)
        file_.addAction(open_)

        exit_ = QAction("Exit", self)
        exit_.triggered.connect(self.close)
        exit_.setShortcut('Ctrl+W')
        file_.addAction(exit_)

        # Edit Menu Options
        prefs = QAction("Preferences", self, triggered=lambda:self.open_new_window(Preferences(self.app)))
        edit.addAction(prefs)

        # Run Menu Options
        pause = QAction("Pause", self, triggered=lambda:self.qmp.command('stop'))
        run.addAction(pause)

        play = QAction("Play", self, triggered=lambda:self.qmp.command('cont'))
        run.addAction(play)

        step = QAction("Step", self)
        run.addAction(step)

        # Debug Menu Options
        hexdmp = QAction("Memory Dump", self, triggered=lambda:self.open_new_window(MemDumpWindow(self.qmp)))
        tools.addAction(hexdmp)

        asm = QAction("Assembly View", self)
        tools.addAction(asm)

        registers = QAction("Register View", self, triggered=lambda:self.open_new_window(RegisterView(self.qmp)))
        tools.addAction(registers)

        stack = QAction("Stack View", self)
        tools.addAction(stack)

        errors = QAction("Error Log", self, triggered=lambda:self.open_new_window(ErrorWindow(self.qmp)))
        tools.addAction(errors)

        tree = QAction("Memory Tree", self, triggered=lambda:self.open_new_window(MemTree(self.qmp)))
        tools.addAction(tree)

        # Help Menu Options 
        usage = QAction("Usage Guide", self)
        help_.addAction(usage)

    def grid_layout(self):
        
        grid = QGridLayout()
        grid.setSpacing(15)

        self.pause_button = QPushButton(self)
        self.pause_button.setIcon(QIcon('package/icons/icons8-pause-90.png'))
        self.pause_button.clicked.connect(lambda: self.qmp.command('cont') if not self.pause_button.isChecked() else self.qmp.command('stop'))
        self.pause_button.setFixedSize(QSize(50, 50))
        grid.addWidget(self.pause_button, 0, 0) # row, column
        self.pause_button.setCheckable(True)

        # Check if QMP is running initially
        if self.qmp.running == 'paused':
            self.paused = True
            self.pause_button.setChecked(self.paused)

        play_button = QPushButton(self)
        play_button.setIcon(QIcon('package/icons/icons8-play-90.png'))
        play_button.clicked.connect(lambda: (self.pause_button.setChecked(False), self.qmp.command('cont')))
        play_button.setFixedSize(QSize(50, 50))
        grid.addWidget(play_button, 0, 1) # row, column
        
        self.time = QLabel()
        self.time.setFont(QFont('Courier New'))
        grid.addWidget(self.time, 0, 2)

        center = QWidget()
        center.setLayout(grid)
        self.setCentralWidget(center)
    
    def throwError(self):
        msgBox = QMessageBox(self)
        msgBox.setText('Lost Connection to QMP!')
        msgBox.show()


    @Slot(str)
    def handle_pause_button(self, value):
        # Catches signals from QMPWrapper
        # print('revieced: ', value)
        if value == 'running':
            self.paused = False
        elif value == 'paused':
            self.paused = True 
        else:
            self.throwError()

        self.pause_button.setChecked(self.paused)

    def open_new_window(self, new_window):
        self.window[type(new_window).__name__] = new_window # this way the old instance get fully reaped

    def update_time(self, time):
        date = datetime.fromtimestamp(time / 1000000000)
        self.time.setText(f'Time: {date.day - 1:02}:{date.hour:02}:{date.minute:02}:{date.second:02}') # -1 for day because it starts from 1

class TimeThread(threading.Thread):
    def __init__(self, qmp):
        super().__init__()
        self.daemon = True
        self.qmp = qmp

    def run(self):
        while True:
            time.sleep(.5)
            args = {'clock': 'virtual'}
            self.qmp.command('itc-sim-time', args=args)