# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'templatka.ui'
#
# Created by: PyQt5 UI code generator 5.10.1
#
# WARNING! All changes made in this file will be lost!

from PyQt5 import QtCore, QtGui, QtWidgets
from scipy.io import wavfile
import pyqtgraph as pg
from scipy.io import wavfile
from PyQt5 import QtCore, QtGui, QtWidgets
import numpy as np
from scipy import signal

class Ui_MainWindow(object):

    def read_data(self,path:str):

        data: np.ndarray
        samplerate, data = wavfile.read(path)
        self.data=data
        if len(data.shape)==2: #gdy jest stereo to wybieramy sobie jeden kanał
            self.data=self.data[:,0]

        self.sekundy = len(data) / float(samplerate)
        self.times = np.arange(len(data)) / float(samplerate)
        self.fs=samplerate

    def setupUi(self, MainWindow,path_to_data):
        self.read_data(path_to_data)
        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 727)

        self.make_plots()
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setLayoutDirection(QtCore.Qt.LeftToRight)
        self.centralwidget.setObjectName("centralwidget")
        self.verticalLayout = QtWidgets.QVBoxLayout(self.centralwidget)
        self.verticalLayout.setObjectName("verticalLayout")
        self.widgetAmlitudaCzas = self.plot
        self.widgetAmlitudaCzas.setObjectName("widgetAmlitudaCzas")
        self.verticalLayout.addWidget(self.widgetAmlitudaCzas)
        self.widgetWybor = self.plot2
        self.widgetWybor.setObjectName("widgetWybor")
        self.verticalLayout.addWidget(self.widgetWybor)
        self.widgetSpektogram = self.plot3
        self.widgetSpektogram.setObjectName("widgetSpektogram")
        self.verticalLayout.addWidget(self.widgetSpektogram)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 22))
        self.menubar.setObjectName("menubar")
        self.menuPlik = QtWidgets.QMenu(self.menubar)
        self.menuPlik.setObjectName("menuPlik")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.otworz = QtWidgets.QAction(MainWindow)
        self.otworz.setObjectName("otworz")

        self.menuPlik.addAction(self.otworz)
        self.menubar.addAction(self.menuPlik.menuAction())

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        # dodanie tych paskow do wybierania przedzialu
        self.lr = pg.LinearRegionItem([0, self.times[-1]])
        self.lr.setZValue(-10)
        self.plot.addItem(self.lr)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def make_plots(self):
        self.plot = pg.PlotWidget(y=self.data, x=self.times)
        self.plot2 = pg.PlotWidget(y=self.data, x=self.times)
        self.plot3=pg.PlotWidget()
        f, t, Zxx = signal.stft(self.data, self.fs, nperseg=256,noverlap=256//2,window='hann')
        Zxx=abs(Zxx)
        Zxx = 20 * np.log10(Zxx)
        # Interpret image data as row-major instead of col-major
        pg.setConfigOptions(imageAxisOrder='row-major')

        pg.mkQApp()
        win = pg.GraphicsLayoutWidget()
        # A plot area (ViewBox + axes) for displaying the image


        # Item for displaying image data
        img = pg.ImageItem()
        self.plot3.addItem(img)
        # Add a histogram with which to control the gradient of the image
        hist = pg.HistogramLUTItem()
        # Link the histogram to the image
        hist.setImageItem(img)
        # If you don't add the histogram to the window, it stays invisible, but I find it useful.
        win.addItem(hist)
        # Show the window
        win.show()
        # Fit the min and max levels of the histogram to the data available
        hist.setLevels(np.min(Zxx), np.max(Zxx))
        # This gradient is roughly comparable to the gradient used by Matplotlib
        # You can adjust it and then save it using hist.gradient.saveState()
        hist.gradient.restoreState(
            {'mode': 'rgb',
             'ticks': [(0.5, (0, 182, 188, 255)),
                       (1.0, (246, 111, 0, 255)),
                       (0.0, (75, 0, 113, 255))]})
        # Sxx contains the amplitude for each pixel
        img.setImage(Zxx)
        # Scale the X and Y Axis to time and frequency (standard is pixels)
        img.scale(t[-1] / np.size(Zxx, axis=1),
                  f[-1] / np.size(Zxx, axis=0))
        # Limit panning/zooming to the spectrogram

        # Add labels to the axis
        self.plot3.setLabel('bottom', "Time", units='s')
        # If you include the units, Pyqtgraph automatically scales the axis and adjusts the SI prefix (in this case kHz)
        self.plot3.setLabel('left', "Frequency", units='Hz')


    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuPlik.setTitle(_translate("MainWindow", "Plik"))
        self.otworz.setText(_translate("MainWindow", "otwórz"))

    def update_state(self,new_path,MainWindow):

        # item = gui.ui.plot.getPlotItem()
        # item.plot(x=gui.ui.times, y=gui.ui.data)
        # item = gui.ui.plot2.getPlotItem()
        # item.plot(x=gui.ui.times, y=gui.ui.data)
        # item = gui.ui.plot3.getPlotItem()
        # item.plot(x=gui.ui.times, y=gui.ui.data)
        self.plot.close()
        self.plot2.close()
        self.plot3.close()
        self.read_data(new_path)
        self.make_plots()

        self.widgetAmlitudaCzas = self.plot
        self.widgetAmlitudaCzas.setObjectName("widgetAmlitudaCzas")
        self.verticalLayout.addWidget(self.widgetAmlitudaCzas)
        self.widgetWybor = self.plot2
        self.widgetWybor.setObjectName("widgetWybor")
        self.verticalLayout.addWidget(self.widgetWybor)
        self.widgetSpektogram = self.plot3
        self.widgetSpektogram.setObjectName("widgetSpektogram")
        self.verticalLayout.addWidget(self.widgetSpektogram)
        # dodanie tych paskow do wybierania przedzialu
        self.lr = pg.LinearRegionItem([0, self.times[-1]])
        self.lr.setZValue(-10)
        self.plot.addItem(self.lr)
        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)


