import time
from PyQt5.QtCore import QSize

#import PlotHandler
from PyQt5 import QtWidgets, QtCore, QtGui, Qt
from PyQt5.QtWidgets import QFrame, QWidget, QTableView, QVBoxLayout, QLabel, QPushButton, QFileDialog, QDialog, \
    QLineEdit, QHBoxLayout, QAbstractItemView, QTextEdit
import re
from PyQt5.QtCore import QSize, Qt
from PyQt5 import QtWidgets, QtCore, QtGui
from PyQt5.QtWidgets import QTableView, QVBoxLayout, QPushButton, QWidget
import re
import main as mn

class TableModel(QtCore.QAbstractTableModel):
    def __init__(self, data):
        super(TableModel, self).__init__()
        self._data = data

    def data(self, index, role):
        if role == Qt.DisplayRole:
            return str(self._data[index.row()][index.column()])

    def rowCount(self, index):
        return len(self._data)

    def columnCount(self, index):
        return len(self._data[0])

class DataTableView(QWidget):
    def __init__(self):
        super().__init__()
        self.selected_Ydata = []
        self.selected_Xdata = []
        self.selectedY_rows = None
        self.selectedY_columns = None
        self.selectedY_indexes = None
        self.selectedX_rows = None
        self.selectedX_columns = None
        self.selectedX_indexes = None
        self.setMinimumSize(QSize(800, 600))
        self.setWindowTitle("Data Table Viewer")


        self.selection_label = QLabel("Enter X data selection (e.g., C1(2-5)):", self)
        self.selection_label.resize(250,25)
        self.selection_label.move(10,20)

        PushXData = QPushButton("X Data", self)
        PushXData.clicked.connect(self.updateXData)
        PushXData.resize(60,25)
        PushXData.move(270,45)

        self.selection_edit = QLineEdit(self)
        self.selection_edit.resize(250,25)
        self.selection_edit.move(10,45)

        self.selection_label2 = QLabel("Enter Y data selection (e.g., C2(2-5)):", self)
        self.selection_label2.resize(250,25)
        self.selection_label2.move(10,80)

        PushYData = QPushButton("Y Data", self)
        PushYData.clicked.connect(self.updateYData)
        PushYData.resize(60, 25)
        PushYData.move(270, 105)

        self.selection_edit2 = QLineEdit(self)
        self.selection_edit2.resize(250,25)
        self.selection_edit2.move(10,105)

        FLoadbutton = QPushButton('Load Data From File', self)
        FLoadbutton.clicked.connect(self.LoadDataFromFile)
        FLoadbutton.resize(160, 100)
        FLoadbutton.move(10, 150)

        SendData = QPushButton('Store chosen datasets', self)
        SendData.clicked.connect(self.SelectDataForPlot)
        SendData.resize(160, 100)
        SendData.move(10, 260)
        self.TermLabel = QLabel(" Terminal", self)
        self.TermLabel.resize(100,20)
        self.TermLabel.move(10,360)

        self.Terminal = QTextEdit('', self)
        self.Terminal.resize(350, 250)
        self.Terminal.move(10, 380)
        self.Terminal.setStyleSheet("background-color : #FFFFFF")

        self.table = QTableView()
        self.table.setGeometry(200, 10, 800, 650)
        example_data = [
            [1, 2, 3],
            [4, 5, 6],
            [7, 8, 9],
        ]

        self.update_table(example_data)
        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(layout)
        self.widget.setGeometry(350, 15, 500, 650)

        self.selection_info_label = QLabel("Selected Columns and Rows:", self)
        layout.addWidget(self.selection_info_label)
    def updateXData(self):
        if self.table.model() is not None:
            self.selectedX_indexes = self.table.selectionModel().selectedIndexes()
            self.selectedX_columns = sorted(set(index.column() + 1 for index in self.selectedX_indexes))
            self.selectedX_rows = sorted(set(index.row() + 1 for index in self.selectedX_indexes))

            self.selection_info_label.setText(f"Selected Columns: {self.selectedX_columns}, Rows: {self.selectedX_rows}")
            self.selection_edit.setText(f"C{self.selectedX_columns[0]} - C{self.selectedX_columns[len(self.selectedX_columns) - 1]}"
                                         f"({self.selectedX_rows[0]}-{self.selectedX_rows[len(self.selectedX_rows) - 1]})")
            self.Terminal.append("X dataset successfully collected.")

    def updateYData(self):
        if self.table.model() is not None:
            self.selectedY_indexes = self.table.selectionModel().selectedIndexes()
            self.selectedY_columns = sorted(set(index.column() + 1 for index in self.selectedY_indexes))
            self.selectedY_rows = sorted(set(index.row() + 1 for index in self.selectedY_indexes))

            self.selection_info_label.setText(f"Selected Columns: {self.selectedY_columns}, Rows: {self.selectedY_rows}")
            self.selection_edit2.setText(f"C{self.selectedY_columns[0]} - C{self.selectedY_columns[len(self.selectedY_columns)-1]}"
                                         f"({self.selectedY_rows[0]}-{self.selectedY_rows[len(self.selectedY_rows)-1]})")
            self.Terminal.append("Y dataset successfully collected.")

    def LoadDataFromFile(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(self, "Open File", "", "Text Files (*.txt);;All Files (*)")

        if file_path:
            with open(file_path, 'r') as file:
                content = file.readlines()
            self.Terminal.append(f"Loading data from file: {file_path}")
        data = [re.split('\s+', line)for line in content]
        self.update_table(data)


    def update_table(self, data):
        model = TableModel(data)
        self.table.setModel(model)
        self.Terminal.append("Data table viewer updated.")

    def SelectDataForPlot(self):
        self.selected_Xdata = [float(index.data()) for index in self.selectedX_indexes]
        self.selected_Ydata = [float(index.data()) for index in self.selectedY_indexes]
        self.Terminal.append("Selected data successfully stored for generating plot.")


    def GetDataset(self):
        self.Terminal.append("Data successfully send to the main IBEX window. \n Ready for generating plot.")
        return [self.selected_Xdata, self.selected_Ydata]