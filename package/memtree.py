from PySide2.QtWidgets import QVBoxLayout, QHBoxLayout, QWidget, QLineEdit, QLabel, QPushButton, QTreeWidget, QTreeWidgetItem, QHeaderView
from package.qmpwrapper import QMP
from package.constants import constants
from PySide2.QtCore import QSemaphore, QSize
from PySide2.QtGui import QFont

class MemTree(QWidget):

	def __init__(self, qmp):
		super().__init__()
		self.qmp = qmp
		self.qmp.memoryMap.connect(self.update_tree)

		self.tree_sem = QSemaphore(1)
		self.sending_sem = QSemaphore(1) # used to prevent sending too many requests at once

		self.init_ui()
		self.get_map()

	def init_ui(self):

		self.vbox = QVBoxLayout()

		se

		self.refresh = QPushButton('Refresh')
		self.refresh.clicked.connect(lambda:self.get_map())
		self.vbox.addWidget(self.refresh)

		self.tree = QTreeWidget()
		self.tree.itemClicked.connect(self.expand_item)
		self.tree.itemCollapsed.connect(self.collapse_item)
		self.tree.setColumnCount(3)
		self.tree.header().setSectionResizeMode(QHeaderView.ResizeToContents)
		self.tree.header().setStretchLastSection(False)
		self.tree.setHeaderLabels(['Memory Region', 'Start Address', 'End Address'])
		self.vbox.addWidget(self.tree)

		self.setLayout(self.vbox)
		self.setGeometry(100, 100, 600, 325)
		self.setWindowTitle("Memory Tree")
		self.show()

	def expand_item(self, item, column):
		if not item.isExpanded():
			name = '?' + item.text(0)
			parent = item.parent()
			while parent: 
				name = '?' + parent.text(0) + name
				parent = parent.parent()
			self.get_subregion(name)
			item.setExpanded(True)
		else:
			self.collapse_item(item)
			item.setExpanded(False)

	def collapse_item(self, item):
		for i in reversed(range(item.childCount())):
			item.removeChild(item.child(i))

	def get_map(self):
		self.tree.clear()
		self.get_subregion('?')

	def get_subregion(self, name):
		self.qmp.command('mtree', args={'name': name})

	# finds item with name 'name' in self.tree
	# self.tree_sem must be acquired before use
	def find(self, name):
		root = self.tree.invisibleRootItem()
		names = name.split('?')[1:]
		for n in names:
			found = False
			for i in range(root.childCount()):
				child = root.child(i)
				if child.text(0) == n:
					found = True
					root = child
					break
			if not found:
				return None
		return root

	def update_tree(self, value):
		parent = value['parent']
		region = value['memorymap']
		if region != None:
			self.tree_sem.acquire()
			parent_node = self.tree
			if parent != '?':
				parent_node = self.find(parent)
			for r in region:
				node = QTreeWidgetItem(parent_node)
				node.setText(0, r['name'])
				start = r['start']
				end = r['end']
				if start < 0:
					start = start + (1 << constants['bits'])
				if end < 0:
					end = end + (1 << constants['bits'])
				node.setText(1, f'0x{start:016x}')
				node.setText(2, f'0x{end:016x}')
				node.setFont(0, QFont('Courier New'))
				node.setFont(1, QFont('Courier New'))
				node.setFont(2, QFont('Courier New'))

			if type(parent) is QTreeWidgetItem and not parent_node.isExpanded():
					parent_node.setExpanded(True)
			self.tree_sem.release()