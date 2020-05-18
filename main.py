#!/usr/bin/python3
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QHBoxLayout, QVBoxLayout, QPlainTextEdit, QListView, QAbstractItemView, QMainWindow, QStackedLayout, QLabel, QSizePolicy, QSpacerItem, QLineEdit, QFormLayout, QColorDialog, QDialogButtonBox, QMessageBox, QItemDelegate
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QFont, QFontMetrics, QColor


import syntax
import os.path
from database import ColorfullModel, InitDb



class NoteForm(QFormLayout):

	def __init__(self, *args):
		super(NoteForm, self).__init__(*args)
		self.currentColor = None

		self.errorLabel = QLabel()
		self.errorLabel.setStyleSheet("color: #f00;")

		self.addNameField()
		self.addColorField()
		self.addSaveBtn()

	def error(self, value):
		self.errorLabel.setText(value)

	def addNameField(self):
		self.nameInput = QLineEdit()
		self.nameInput.setPlaceholderText("Name")
		self.addRow("Name:", self.nameInput)
		self.addRow("", self.errorLabel)

	def chooseColor(self):
		self.currentColor = QColorDialog.getColor()

	def addColorField(self):
		self.color = QPushButton(text="Choose color")
		self.color.clicked.connect(self.chooseColor)
		self.addRow("Color:", self.color)
		self.addRow("", QLabel())

	def addSaveBtn(self):
		formButtons = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
		formButtons.accepted.connect(self.saveForm)
		formButtons.rejected.connect(self.cancelForm)
		self.addRow(formButtons)

	def cancelForm(self):
		self.resetForm()

	def resetForm(self):
		self.error("")
		self.currentColor = None
		self.nameInput.setText("")
		window.stack.setCurrentIndex(0)

	def saveForm(self):
		self.error("")
		name = self.nameInput.text()
		color: "#000000"
		if name == "":
			self.error("Name is not set")
			return
		if self.currentColor:
			color = self.currentColor.name()

		newRecord = noteModel.record()
		newRecord.setValue("name", name)
		newRecord.setValue("color", color)
		noteModel.insertRecord(-1, newRecord)
		noteModel.select()
		self.resetForm()


class NoteContent(QPlainTextEdit):

	def __init__(self, *args):
		super(NoteContent, self).__init__(*args)
		self.row = None

		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

		self.setupFont()
		
	def setupFont(self):
		tabStop = 4
		fontMetrics = QFontMetrics(font)
		self.setTabStopWidth(tabStop * fontMetrics.width(' '))
		self.setFont(font)

	def disgard(self):
		self.clear()
		self.row = None


	def save(self):
		if self.row is None:
			print("No index set.")
			return

		record = noteModel.record(self.row)
		record.setValue('content', self.toPlainText())

		ok = noteModel.setRecord(self.row, record)
		if ok:
			print("Saved")
		else:
			print(ok)
			print("Something bad happened.")

	def delete(self):
		if self.row is None:
			print("No index set.")
			return

		confirmation = QMessageBox.critical(self.parent(), "Delete row", "Are you sure?", QMessageBox.Yes, QMessageBox.No)
		if confirmation == QMessageBox.Yes:
			noteModel.removeRow(self.row)
			noteModel.submitAll()
			noteModel.select()
			window.stack.setCurrentIndex(0)


class ItemDelegate(QItemDelegate):
	def __init__(self, *args):
		super(ItemDelegate, self).__init__(*args)

	def sizeHint(self, option, index):
		return QSize(option.rect.width(), option.rect.height())


	def paint(self, painter, option, index):
		if not index.isValid():
			return
		
		painter.save()

		titleText = index.data(0)
		color = index.model().data(index, Qt.BackgroundRole)

		textColor = "#000" if color.lightness() > 120 else "#fff"

		painter.setPen(QColor(textColor))
		painter.setFont(font)
		painter.fillRect(option.rect.adjusted(0, 0, -1, -1), color)
		painter.drawText(option.rect, Qt.AlignCenter|Qt.AlignCenter|Qt.TextWordWrap, titleText)
		painter.restore()


class NotesList(QListView):

	def __init__(self, *args):
		super(NotesList, self).__init__(*args)
		self.setFlow(QListView.LeftToRight)
		self.setViewMode(QListView.IconMode)
		self.setResizeMode(QListView.Adjust)
		self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)

		self.installEventFilter(self)

		self.setItemDelegate(ItemDelegate(self))

		self.setModel(noteModel)
		self.setModelColumn(1)

		self.clicked.connect(self.fetchFile)
		self.setEditTriggers(QAbstractItemView.NoEditTriggers)

	def eventFilter(self, obj, event):
		if obj is self and event.type() == event.Resize:
			currentWidth = self.size().width()
			space = 6
			divider = 3

			if currentWidth > 1200:
				space = 3.1
				divider = 5
			elif currentWidth > 900:
				space = 4.1
				divider = 4
			elif currentWidth < 500:
				space = 9
				divider = 2
			gridsize = self.size() / divider
			# remove from width to account for the scrollbar
			actualWidth = gridsize.width() - space
			gridsize.setWidth(actualWidth)
			gridsize.setHeight(actualWidth)
			self.setGridSize(gridsize)

		return super(NotesList, self).eventFilter(obj, event)


	def fetchFile(self, index):
		row = index.row()
		name = noteModel.record(row).field(1).value()
		content = noteModel.record(row).field(3).value()

		editor.row = row
		editor.setPlainText(content)
		window.editorTitle.setText(name)
		window.stack.setCurrentIndex(1)

	def filter(self, text):
		text = text.strip()
		if len(text) == 0:
			noteModel.setFilter("")
		noteModel.setFilter("name like '%%%s%%'" % text)




class MainWindow(QMainWindow):
	def __init__(self, parent=None):
		super(MainWindow, self).__init__(parent)
		self.setWindowTitle("Notes")
		self.resize(800, 600)
		central_widget = QWidget()
		self.setCentralWidget(central_widget)

		mainLayout = QHBoxLayout(central_widget)
		mainLayout.setContentsMargins(0, 0, 0, 0)

		self.editorTitle = QLabel()

		self.notes_list = QWidget()
		self.notes_view()

		self.editor_widget = QWidget()
		self.editor_view()

		self.form_widget = QWidget()
		self.form_view()


		self.stack = QStackedLayout()
		mainLayout.addLayout(self.stack)

		for w in [self.notes_list, self.editor_widget, self.form_widget]:
			self.stack.addWidget(w)

	def notes_view(self):
		widget = QWidget()
		actionsLayout = QHBoxLayout(widget)
		actionsLayout.setContentsMargins(0, 0, 0, 0)

		notesView = NotesList()

		searchInput = QLineEdit()
		searchInput.setPlaceholderText("Search...")
		searchInput.textChanged.connect(notesView.filter)
		addBtn = QPushButton(text="✚")
		addBtn.clicked.connect(lambda: self.stack.setCurrentIndex(2))
		actionsLayout.addWidget(searchInput)
		actionsLayout.addWidget(addBtn)

		mainLayout = QVBoxLayout(self.notes_list)
		mainLayout.addWidget(widget)
		mainLayout.addWidget(notesView)



	def editor_view(self):
		mainLayout = QVBoxLayout(self.editor_widget)

		verticalSpacer = QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum) 

		widget = QWidget()
		actionsLayout = QHBoxLayout(widget)
		actionsLayout.setContentsMargins(0, 0, 0, 0)

		button = QPushButton(text="❮")
		button.clicked.connect(self.goBack)

		saveBtn = QPushButton(text="Save")
		saveBtn.clicked.connect(editor.save)

		deleteBtn = QPushButton(text="✖")
		deleteBtn.clicked.connect(editor.delete)

		
		self.editorTitle.setText("Title")

		actionsLayout.addWidget(button)
		actionsLayout.addItem(verticalSpacer)
		actionsLayout.addWidget(self.editorTitle)
		actionsLayout.addItem(verticalSpacer)
		actionsLayout.addWidget(deleteBtn)
		actionsLayout.addWidget(saveBtn)
		mainLayout.addWidget(widget)
		mainLayout.addWidget(editor)

	def form_view(self):
		mainLayout = QVBoxLayout(self.form_widget)
		mainLayout.setAlignment(Qt.AlignCenter)

		widget = QWidget()
		widget.setMaximumWidth(350)
		formLayout = NoteForm(widget)
		mainLayout.addWidget(widget)


	def goBack(self):
		editor.disgard()
		self.stack.setCurrentIndex(0)



if __name__ == '__main__':
	app = QApplication([])
	# default font
	font = QFont()
	font.setPointSize(12)

	noteModel = InitDb()


	app.setStyleSheet(open('./custom.qss').read())

	editor = NoteContent()
	highlight = syntax.MardownHighlighter(editor.document())

	window = MainWindow()
	window.show()
	app.exec_()
