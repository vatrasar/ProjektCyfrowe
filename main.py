from templatka import Ui_MainWindow
from PyQt5 import QtCore, QtGui, QtWidgets
import sys
from PyQt5.QtWidgets import QApplication, QWidget, QDial, QFileDialog
import time
from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
class Gui:
    def updatePlot(self):
        if(time.time()-self.start_time>2):
            item=self.ui.plot2.getPlotItem()
            item.plot(y=self.ui.data,x=self.ui.times)
            self.start_time=time.time()

        self.ui.plot2.setXRange(*self.ui.lr.getRegion(),padding=0)


    def updateRegion(self):
        pass
    def __init__(self,window):
        self.start_time = time.time()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(window,"dzwieki/bzyk.wav")
        self.ui.lr.sigRegionChanged.connect(self.updatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.updateRegion)
        self.ui.otworz.triggered.connect(self.open)
        self.updatePlot()
        self.window=window

    def update_state(self,new_path,window):
        self.ui.update_state(new_path,window)
        self.ui.lr.sigRegionChanged.connect(self.updatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.updateRegion)
        self.updatePlot()
        f, t, Zxx = signal.stft(self.ui.data, self.ui.fs, nperseg=256,noverlap=256//2,window='hann')
        Zxx=abs(Zxx)
        plt.pcolormesh(t, f, np.abs(Zxx))
        plt.title('STFT Magnitude')
        plt.ylabel('Frequency [Hz]')
        plt.xlabel('Time [sec]')

        plt.show()
    def open(self):
        path, _ = QFileDialog.getOpenFileName()
        self.update_state(path,window)


if __name__ == "__main__":

    app = QApplication(sys.argv)
    window=QtWidgets.QMainWindow()
    gui=Gui(window)
    b=gui.ui.menubar.actions()
    window.show()
    sys.exit(app.exec_())
