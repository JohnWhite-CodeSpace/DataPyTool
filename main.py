import math
import os.path
import threading
import time
import keyboard
import TableViewer as tv
from matplotlib.ticker import MaxNLocator
from PyQt5 import QtCore, QtWidgets, QtGui, Qt
from PyQt5.QtWidgets import QMainWindow, QLabel, QGridLayout, QWidget, QTextEdit, QPushButton, QFileDialog, QDialog, \
    QMenuBar, QMenu, QAction, QProgressBar, QVBoxLayout, QLineEdit, QDesktopWidget
from PyQt5.QtCore import QSize, QTimer, QObject, pyqtSignal, Qt
from PyQt5.QtGui import *
import subprocess
import scipy as sp
import sys
import matplotlib
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg, NavigationToolbar2QT as NavigationToolbar
from matplotlib.figure import Figure
matplotlib.use('Qt5Agg')
import numpy as np

class MplCanvas(FigureCanvasQTAgg):

    def __init__(self, parents = None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot()
        super(MplCanvas, self).__init__(self.fig)

class KeyHelper(QtCore.QObject):
    keyPressed = QtCore.pyqtSignal(QtCore.Qt.Key)

    def __init__(self, window):
        super().__init__(window)
        self._window = window

        self.window.installEventFilter(self)

    @property
    def window(self):
        return self._window

    def eventFilter(self, obj, event):
        if obj is self.window and event.type() == QtCore.QEvent.KeyPress:
            self.keyPressed.emit(event.key())
        return super().eventFilter(obj, event)
class MainWindow(QMainWindow):
    update_progress_signal = pyqtSignal(int, int)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.sorted_dir = None
        self.windows = None
        self.DataX = None
        self.DataY = None
        self.minValue = 0
        self.maxValue = 0
        self.setMinimumSize(QSize(1000, 1000))
        self.setWindowTitle("Simple Data Analizer")
        self.update_progress_signal.connect(self.update_progress)
        Plotbutton = QPushButton('Simple Data Analizer', self)
        Plotbutton.clicked.connect(self.InitDataPlotting)
        Plotbutton.resize(160, 80)
        Plotbutton.move(10, 30)

        PlotData = QPushButton('Plot Data', self)
        PlotData.clicked.connect(self.HandlePlot1)
        PlotData.resize(160, 80)
        PlotData.move(10, 110)

        PolDegLabel = QLabel('Enter Polynomial Degree:', self)
        PolDegLabel.resize(160,20)
        PolDegLabel.move(10,190)

        self.EnterPolyDeg = QLineEdit(self)
        self.EnterPolyDeg.resize(160,30)
        self.EnterPolyDeg.move(10,220)

        RangeLabel = QLabel('Enter Range for polynomial fit', self)
        RangeLabel.resize(160,20)
        RangeLabel.move(10,250)

        L1 = QLabel('Fit range:', self)
        L1.resize(60,20)
        L1.move(10,280)

        self.PolyDegMin = QLineEdit(self)
        self.PolyDegMin.resize(40, 20)
        self.PolyDegMin.move(65, 280)
        self.PolyDegMin.textChanged.connect(lambda: self.onTextChanged(self.PolyDegMin,1))

        DeriveButton = QPushButton('Derive function', self)
        DeriveButton.clicked.connect(self.CalculateDerivativeForPlot)
        DeriveButton.resize(160, 80)
        DeriveButton.move(10, 430)

        L3 = QLabel('From val1:', self)
        L3.resize(60, 20)
        L3.move(10, 302)

        self.ShowPolyDegMin = QLineEdit(self)
        self.ShowPolyDegMin.resize(60, 20)
        self.ShowPolyDegMin.move(65, 302)

        L2 = QLabel('to: ', self)
        L2.resize(30, 20)
        L2.move(110, 280)

        L4 = QLabel('to val2:', self)
        L4.resize(40, 20)
        L4.move(10, 324)

        self.PolyDegMax = QLineEdit(self)
        self.PolyDegMax.resize(40, 20)
        self.PolyDegMax.move(130, 280)
        self.PolyDegMax.textChanged.connect(lambda: self.onTextChanged(self.PolyDegMax,2))

        self.ShowPolyDegMax = QLineEdit(self)
        self.ShowPolyDegMax.resize(60, 20)
        self.ShowPolyDegMax.move(65, 324)

        PlotData = QPushButton('Fit best polynomial', self)
        PlotData.clicked.connect(self.PolyFit)
        PlotData.resize(160, 80)
        PlotData.move(10, 350)

        TermLabel = QLabel('Terminal', self)
        TermLabel.resize(200, 30)
        TermLabel.move(10, 690)

        self.Terminal = QTextEdit('', self)
        self.Terminal.resize(980, 230)
        self.Terminal.move(10, 720)
        self.Terminal.setStyleSheet("background-color : #FFFFFF")
        self.Create_MenuBar()

        self.sc = MplCanvas(self, width=8, height=6, dpi=70)
        self.sc.axes.scatter([0,1,2,3,4], [10,1,20,3,40])

        toolbar = NavigationToolbar(self.sc,self)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(toolbar)
        layout.addWidget(self.sc)

        self.widget = QtWidgets.QWidget(self)
        self.widget.setLayout(layout)
        self.widget.setGeometry(250, 15, 750, 600)

        self.ProgressBar = QProgressBar(self)
        self.ProgressBar.resize(980,15)
        self.ProgressBar.move(10,980)

        self.Progress = QLabel("Plotting progress", self)
        self.Progress.resize(800, 30)
        self.Progress.move(10, 950)

        L5 = QLabel("Label to x axis", self)
        L5.resize(120,20)
        L5.move(300,610)

        self.XLabel = QLineEdit(self)
        self.XLabel.resize(200, 20)
        self.XLabel.move(300, 630)
        self.XLabel.textChanged.connect(self.SetXLabel)

        L6 = QLabel("Label to y axis", self)
        L6.resize(120,20)
        L6.move(530,610)

        self.YLabel= QLineEdit(self)
        self.YLabel.resize(200, 20)
        self.YLabel.move(530, 630)
        self.YLabel.textChanged.connect(self.SetYLabel)

        L7 = QLabel("Title to plot:", self)
        L7.resize(100,20)
        L7.move(760,610)

        self.PlotTitle = QLineEdit(self)
        self.PlotTitle.resize(200, 20)
        self.PlotTitle.move(760, 630)
        self.PlotTitle.textChanged.connect(self.SetPlotTitle)


    def Create_MenuBar(self):
        menubar = QMenuBar(self)
        self.setMenuBar(menubar)
        fileMenu = menubar.addMenu("&File")
        fitem1 = fileMenu.addAction("Open file in terminal")
        fitem2 = fileMenu.addAction("Reload interface")
        plotMenu = menubar.addMenu("&Plot")
        plot1action = QAction("&XY Plot",self)
        plot1action.triggered.connect(self.HandlePlot1)
        self.pitem1 = plotMenu.addAction(plot1action)
        helpMenu = menubar.addMenu("&Help")
        SbSaction = QAction("Side by side view", self)
        SbSaction.triggered.connect(self.SideBySide)
        self.hitem1 = helpMenu.addAction(SbSaction)
        hitem2 = helpMenu.addAction("Open Manual")
        hitem3 = helpMenu.addAction("Open Documentation")

    def HandlePlot1(self):
        if self.windows is not None:
            Datax, Datay = self.windows.GetDataset()
            self.sc.axes.cla()
            self.sc.axes.scatter(Datax, Datay,2)
            self.sc.axes.autoscale()
            # ysmoothed = sp.ndimage.gaussian_filter1d(Datay,sigma=1)
            # self.sc.axes.plot(Datax, ysmoothed, color='red')
            self.sc.draw()
            self.Terminal.append(f"Min values: (x,y) = ({min(Datax)}, {min(Datay)})")
            self.Terminal.append(f"Max values: (x,y) = ({max(Datax)}, {max(Datay)})")
        else:
            self.Terminal.append("First open Table Viewer and choose data for plotting.")

    def PolyFit(self):
        try:
            deg = int(self.EnterPolyDeg.text())
            print(deg)
        except ValueError:
            self.Terminal("Invalid data type provided in Polynomial degree text field.")
            return

        if self.windows is not None:
            Datax, Datay = self.windows.GetDataset()
            self.sc.axes.cla()
            self.sc.axes.scatter(Datax, Datay, 2, label="Experimental data")

            self.sc.axes.autoscale()
            if deg is not None:
                if self.minValue!=0 and self.maxValue!=0 and self.minValue < self.maxValue < len(Datax):
                    ModDatax = Datax[self.minValue:self.maxValue]
                    ModDatax = np.sort(ModDatax)  # Ensure Datax is sorted
                    stacked_x = np.vstack([ModDatax, ModDatax - 1, ModDatax + 1]).T
                    coeffs = np.polyfit(stacked_x[:, 0], Datay[self.minValue: self.maxValue], deg)
                    R = Datax[Datay.index(min(Datay))]
                    coeffs[3] = coeffs[3] + +min(Datay)
                    print(f"{coeffs}")
                    x2 = np.arange(min(ModDatax) - 1, max(ModDatax) + 1, 0.01)
                    y2 = np.polyval(coeffs, x2)-min(Datay)
                else:
                    Datax, Datay = self.windows.GetDataset()
                    Datax = np.sort(Datax)
                    stacked_x = np.vstack([Datax, Datax - 1, Datax + 1]).T
                    coeffs = np.polyfit(stacked_x[:, 0], Datay, deg)
                    coeffs[3] = coeffs[3] + min(Datay)
                    print(f"{coeffs}")
                    x2 = np.arange(min(Datax) - 1, max(Datax) + 1, 0.01)
                    y2 = np.polyval(coeffs, x2) - min(Datay)
                self.sc.axes.plot(x2, y2, label=f"Polynomial fit (degree: {deg})", color="red")

                self.sc.axes.autoscale()
                self.sc.axes.legend()
                equation = f"Polynomial Equation: "
                for i in range(deg, -1, -1):
                    coefficient = coeffs[deg - i]
                    if i == deg:
                        equation += f"{coefficient:.2f}x^{i}"
                    elif i == 0:
                        equation += f" {'+' if coefficient >= 0 else '-'} {abs(coefficient):.2f}"
                    else:
                        equation += f" {'+' if coefficient >= 0 else '-'} {abs(coefficient):.2f}x^{i}"

                self.Terminal.append(equation)
                self.Terminal.append(f"Min values: (x,y) = ({min(Datax)},{min(Datay)})")
                self.Terminal.append(f"Max values: (x,y) = ({max(Datax)},{max(Datay)})")
                self.sc.draw()

            else:
                self.Terminal.append("Enter polynomial degree value first.")
        else:
            self.Terminal.append("First open Table Viewer and choose data for plotting.")


    def refresh_text_box(self, response):
        time.sleep(0.1)  # Some delay to avoid immediate GUI updates
        self.Terminal.append(response)

    def update_progress(self, value, PBnum):
        if PBnum ==1:
            self.ProgressBar.setValue(value)
        elif PBnum ==2:
            self.ProgressBar2.setValue(value)


    def InitDataPlotting(self):
        if self.windows is None:
            self.windows = tv.DataTableView()
        self.windows.show()

    def CalculateDerivativeForPlot(self):
        Datax, Datay = self.windows.GetDataset()

        try:
            DDatay = np.gradient(Datay,Datax)/Datay[len(Datay)-1]
        except ValueError:
            pass
        self.Terminal.append(f"Nominal Voltage: Unom = {sp.integrate.simpson(Datax, Datay)}")
        self.sc.axes.plot(Datax[:len(Datay)], DDatay, label=f"Derivative function plot", color="green")
        self.sc.draw()

    def onTextChanged(self, sender, num):
        if self.windows is not None:
            Datax, Datay = self.windows.GetDataset()
            try:
                number = int(sender.text())
                if num==1 and number<len(Datax):
                    self.ShowPolyDegMin.setText(f"{Datax[number]}")
                    self.minValue = number
                if num==2 and number<len(Datax):
                    self.ShowPolyDegMax.setText(f"{Datax[number]}")
                    self.maxValue = number

            except ValueError:
                print("Invalid input. Please enter a number.")

    def SideBySide(self):
        self.resize_windows()

    def SetXLabel(self):
        if self.XLabel.text()is not None:
            print(self.XLabel.text())
            self.sc.figure.supxlabel(self.XLabel.text())
            self.sc.draw()

    def SetYLabel(self):
        if self.YLabel.text()is not None:
            print(self.YLabel.text())
            self.sc.figure.supylabel(self.YLabel.text())
            self.sc.draw()

    def SetPlotTitle(self):
        if self.PlotTitle.text()is not None:
            print(self.PlotTitle.text())
            self.sc.figure.suptitle(self.PlotTitle.text())
            self.sc.draw()


    def handle_key_pressed(self, key):
        if key in (QtCore.Qt.Key_1, QtCore.Qt.Key_Return):
            self.SideBySide()

    def resize_windows(self):
        desktop = QDesktopWidget().screenGeometry()
        window_width = desktop.width() // 2
        window_height = desktop.height()
        if self.windows is not None:
            self.setGeometry(0, 40, window_width - 5, window_height)
            self.windows.setGeometry(window_width+50, 40, window_width-50 , window_height)
        else:
            self.setGeometry(0,40, window_width - 100, window_height)




def refresh_text_box(self, MYSTRING):
    self.Terminal.append('started appending %s' % MYSTRING)  # append string
    app.QApplication.processEvents()  # update gui for pyqt


if __name__ == "__main__":

    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    helper = KeyHelper(main_window.windowHandle())
    helper.keyPressed.connect(main_window.handle_key_pressed)
    sys.exit(app.exec_())