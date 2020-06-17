
from PySide2.QtWidgets import QMainWindow, QAction, QGridLayout, QPushButton, QWidget, QLabel, QLineEdit
from PySide2.QtGui import QIcon, QFont 
from PySide2.QtCore import QSize, Slot


from package.memdumpwindow import MemDumpWindow
from package.registerview import RegisterView

from package.qmpwrapper import QMP
from package.memtree import MemTree

import threading
import time
from datetime import datetime


class MainWindow(QMainWindow):

    def __init__(self):
 
        self.qmp = QMP()
        #self.qmp.start()

        self.qmp.stateChanged.connect(self.handle_pause_button)

        super().__init__()
        self.init_ui()

        self.qmp.timeUpdate.connect(self.update_time)
        self.t = TimeThread(self.qmp)
        

        self.window = []

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
        prefs = QAction("Preferences", self)
        edit.addAction(prefs)

        # Run Menu Options
        pause = QAction("Pause", self, triggered=lambda:self.qmp.command('stop'))
        run.addAction(pause)

        play = QAction("Play", self, triggered=lambda:self.qmp.command('cont'))
        run.addAction(play)

        step = QAction("Step", self)
        run.addAction(step)

        # Debug Menu Options
        hexdmp = QAction("Memory Dump", self, triggered=(lambda: self.open_new_window(MemDumpWindow(self.qmp)) if self.qmp.isSockValid() else None))
        tools.addAction(hexdmp)

        asm = QAction("Assembly View", self)
        tools.addAction(asm)

        registers = QAction("Register View", self, triggered=(lambda: self.open_new_window(RegisterView(self.qmp)) if self.qmp.isSockValid() else None))
        tools.addAction(registers)

        stack = QAction("Stack View", self)
        tools.addAction(stack)

        errors = QAction("Error Log", self)
        tools.addAction(errors)

        tree = QAction("Memory Tree", self, triggered=(lambda: self.open_new_window(MemTree(self.qmp, self)) if self.qmp.isSockValid() else None))
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
        if not self.qmp.running:
            self.pause_button.setChecked(True)

        play_button = QPushButton(self)
        play_button.setIcon(QIcon('package/icons/icons8-play-90.png'))
        play_button.clicked.connect(lambda: (self.pause_button.setChecked(False), self.qmp.command('cont')))
        play_button.setFixedSize(QSize(50, 50))
        grid.addWidget(play_button, 0, 1) # row, column

        
        self.time = QLabel('Time: 00:00:00:00')
        self.time.setFont(QFont('Courier New'))
        grid.addWidget(self.time, 0, 2)

        self.host = QLineEdit()
        grid.addWidget(self.host, 1, 0)

        self.port = QLineEdit()
        grid.addWidget(self.port, 1, 1)

        self.connect = QPushButton("Connect")
        self.connect.clicked.connect(self.qmp_start)
        grid.addWidget(self.connect, 1, 2)

        # Check if QMP is running initially
        if not self.qmp.running:
            self.pause_button.setChecked(True)

        center = QWidget()
        center.setLayout(grid)
        self.setCentralWidget(center)

    @Slot(bool)
    def handle_pause_button(self, value):
        # Catches signals from QMPWrapper
        self.pause_button.setChecked(not value)

    def open_new_window(self, new_window):
        if self.qmp.isSockValid():
            self.window.append(new_window)

    def update_time(self, time):
        date = datetime.fromtimestamp(time / 1000000000)
        self.time.setText(f'Time: {date.day - 1:02}:{date.hour:02}:{date.minute:02}:{date.second:02}') # -1 for day because it starts from 1

    def qmp_start(self):
        self.qmp.reconnect(self.host.text(), int(self.port.text()))
        if not self.qmp.isAlive():
            self.qmp.start()
        if not self.t.isAlive():
            self.t.start()

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