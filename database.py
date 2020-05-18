from PyQt5.QtSql import QSqlDatabase, QSqlTableModel, QSqlQuery, QSqlRecord
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor


class ColorfullModel(QSqlTableModel):
	def __init__(self, dbcursor=None):
		super(ColorfullModel, self).__init__()
 
	def data(self, QModelIndex, role=None):
		v = QSqlTableModel.data(self, QModelIndex, role)
		if role == Qt.BackgroundRole:
			index = self.index(QModelIndex.row(), 2)
			color = QSqlTableModel.data(self, index, Qt.DisplayRole)
			if color:
				return QColor(color)
		return (v)

def InitDb():
	db = QSqlDatabase.addDatabase("QSQLITE")
	db.setDatabaseName("./db.sqlite")
	db.open()
	noteModel = ColorfullModel()
	noteModel.setTable("notes")
	noteModel.select()
	return noteModel