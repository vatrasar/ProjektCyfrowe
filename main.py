from templatka import Ui_MainWindow
from PyQt5 import  QtWidgets,QtCore
import sys
from PyQt5.QtWidgets import QApplication,QFileDialog,QDialog,QPushButton,QLabel
import PyQt5
import time
import numpy as np
import pygame
from scipy.io import wavfile
class Gui:
    def updatePlot(self):
        if(time.time()-self.start_time>1):
            item=self.ui.plot2.getPlotItem()
            item.plot(y=self.ui.data,x=self.ui.times)
            self.start_time=time.time()

        self.update_sonogram()



    def update_sonogram(self):
        #aktualizuje przedział
        self.ui.plot2.setXRange(*self.ui.lr.getRegion(), padding=0)
        range = self.ui.lr.getRegion()
       
        sonogram_times = (self.ui.times > range[0]) & (self.ui.times < range[1])
        sonogram_data = self.ui.data[sonogram_times]

        self.ui.plot3.setXRange(*self.ui.lr.getRegion(), padding=0)
        wavfile.write("temp.wav",self.ui.fs,sonogram_data)


    def updateRegion(self):
        pass
    def __init__(self,window):
        self.start_time = time.time()
        self.ui = Ui_MainWindow()
        path, _ = QFileDialog.getOpenFileName()
        self.ui.setupUi(window,path)
        self.ui.lr.sigRegionChanged.connect(self.updatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.updateRegion)
        self.ui.otworz_plik.triggered.connect(self.open)
        self.ui.overlap20.triggered.connect(lambda x:self.set_overlap(0.1))
        self.ui.overlap30.triggered.connect(lambda x:self.set_overlap(0.2))
        self.ui.overlap40.triggered.connect(lambda x:self.set_overlap(0.4))
        self.ui.overlap50.triggered.connect(lambda x:self.set_overlap(0.5))
        self.ui.segment_256.triggered.connect(lambda x:self.set_segments(256))
        self.ui.segment_512.triggered.connect(lambda x:self.set_segments(512))
        self.ui.segment_1024.triggered.connect(lambda x:self.set_segments(1024))
        self.ui.segment_32.triggered.connect(lambda x:self.set_segments(32))
        self.ui.actionblackman.triggered.connect(lambda x: self.set_window("blackman"))
        self.ui.actionflattop.triggered.connect(lambda x: self.set_window("flattop"))
        self.ui.actionhamming.triggered.connect(lambda x: self.set_window("hamming"))
        self.ui.actionhann.triggered.connect(lambda x: self.set_window("hann"))
        self.ui.actionparzen.triggered.connect(lambda x: self.set_window("parzen"))
        self.ui.actiontriang.triggered.connect(lambda x: self.set_window("triang"))
        self.ui.calosc_odtworz.triggered.connect(self.play_whole_file)
        self.ui.przedzial.triggered.connect(self.play_part_of_file)
        self.updatePlot()
        self.window=window
    def set_overlap(self,new_overlap):
        self.ui.overlap=new_overlap
        self.update_state(self.ui.file_name,self.window)

    def set_segments(self, new_segements):
        self.ui.nperseg = new_segements
        self.update_state(self.ui.file_name, self.window)
    def set_window(self,new_window):
        self.ui.window=new_window
        self.update_state(self.ui.file_name,self.window)
    def play_whole_file(self):
        pygame.mixer.music.load(self.ui.file_name)
        pygame.mixer.music.play()
    def play_part_of_file(self):
        pygame.mixer.music.load("temp.wav")
        pygame.mixer.music.play()

    def update_state(self,new_path,window):
        self.ui.update_state(new_path,window)
        self.ui.lr.sigRegionChanged.connect(self.updatePlot)
        self.ui.plot2.sigXRangeChanged.connect(self.updateRegion)
        self.updatePlot()
    def open(self):
        path, _ = QFileDialog.getOpenFileName()
        try:
            self.update_state(path,window)
        except ValueError:
            self.alter()

    def alter(self):
        dialog=QDialog()
        ok_button=QLabel("Nie można wczytać tego pliku.\n Proszę wybrać inny.",dialog)
        # ok_button.move(80,50)
        dialog.resize(200,80)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setWindowTitle("Błąd")
        dialog.exec_()

if __name__ == "__main__":
    try:
        pygame.init()

        app = QApplication(sys.argv)
        window=QtWidgets.QMainWindow()
        gui=Gui(window)
        b=gui.ui.menubar.actions()
        window.show()
        sys.exit(app.exec_())
    except ValueError:
        dialog = QDialog()
        ok_button = QLabel("Nie można wczytać tego pliku.\n Proszę wybrać inny.", dialog)
        # ok_button.move(80,50)
        dialog.resize(200, 80)
        dialog.setWindowModality(QtCore.Qt.ApplicationModal)
        dialog.setWindowTitle("Błąd")
        dialog.exec_()
