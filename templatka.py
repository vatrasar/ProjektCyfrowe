
import pyqtgraph as pg
from scipy.io import wavfile
from PyQt5 import QtCore, QtWidgets
import numpy as np
from scipy import fftpack
from scipy.signal import signaltools
from scipy.signal.windows import get_window


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
        self.file_name=path

    def setupUi(self, MainWindow,path_to_data):

        self.overlap = 0.5
        self.nperseg = 256
        self.window = 'hann'

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
        self.menubar.setGeometry(QtCore.QRect(0, 0, 723, 22))
        self.menubar.setObjectName("menubar")
        self.menuPlik = QtWidgets.QMenu(self.menubar)
        self.menuPlik.setObjectName("menuPlik")
        self.overlap40 = QtWidgets.QMenu(self.menubar)
        self.overlap40.setObjectName("overlap40")
        self.menusegmenty = QtWidgets.QMenu(self.menubar)
        self.menusegmenty.setObjectName("menusegmenty")
        self.menuOdtw_rz = QtWidgets.QMenu(self.menubar)
        self.menuOdtw_rz.setObjectName("menuOdtw_rz")
        self.menuOkna = QtWidgets.QMenu(self.menubar)
        self.menuOkna.setObjectName("menuOkna")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)
        self.otworz_plik = QtWidgets.QAction(MainWindow)
        self.otworz_plik.setObjectName("actionotw_rz")
        self.overlap_10 = QtWidgets.QAction(MainWindow)
        self.overlap_10.setObjectName("overlap_10")
        self.overlap20 = QtWidgets.QAction(MainWindow)
        self.overlap20.setObjectName("overlap20")
        self.overlap30 = QtWidgets.QAction(MainWindow)
        self.overlap30.setObjectName("overlap30")
        self.action40 = QtWidgets.QAction(MainWindow)
        self.action40.setObjectName("action40")
        self.overlap50 = QtWidgets.QAction(MainWindow)
        self.overlap50.setObjectName("overlap50")
        self.segment_256 = QtWidgets.QAction(MainWindow)
        self.segment_256.setObjectName("segment_256")
        self.segment_512 = QtWidgets.QAction(MainWindow)
        self.segment_512.setObjectName("segment_512")
        self.segment_1024 = QtWidgets.QAction(MainWindow)
        self.segment_1024.setObjectName("segment_1024")

        self.segment_32 = QtWidgets.QAction(MainWindow)
        self.segment_32.setObjectName("segment_32")

        self.actiontriang = QtWidgets.QAction(MainWindow)
        self.actiontriang.setObjectName("actiontriang")
        self.actionblackman = QtWidgets.QAction(MainWindow)
        self.actionblackman.setObjectName("actionblackman")
        self.actionhamming = QtWidgets.QAction(MainWindow)
        self.actionhamming.setObjectName("actionhamming")
        self.actionhann = QtWidgets.QAction(MainWindow)
        self.actionhann.setObjectName("actionhann")
        self.actionflattop = QtWidgets.QAction(MainWindow)
        self.actionflattop.setObjectName("actionflattop")
        self.actionparzen = QtWidgets.QAction(MainWindow)
        self.actionparzen.setObjectName("actionparzen")
        self.calosc_odtworz = QtWidgets.QAction(MainWindow)
        self.calosc_odtworz.setObjectName("calosc_odtworz")
        self.przedzial = QtWidgets.QAction(MainWindow)
        self.przedzial.setObjectName("przedzial")
        self.menuPlik.addAction(self.otworz_plik)
        self.overlap40.addAction(self.overlap_10)
        self.overlap40.addAction(self.overlap20)
        self.overlap40.addAction(self.action40)
        self.overlap40.addAction(self.overlap50)
        self.menusegmenty.addAction(self.segment_32)
        self.menusegmenty.addAction(self.segment_256)
        self.menusegmenty.addAction(self.segment_512)

        self.menusegmenty.addAction(self.segment_1024)

        self.menuOkna.addAction(self.actiontriang)
        self.menuOkna.addAction(self.actionblackman)
        self.menuOkna.addAction(self.actionhamming)
        self.menuOkna.addAction(self.actionhann)
        self.menuOkna.addAction(self.actionflattop)
        self.menuOkna.addAction(self.actionparzen)
        self.menubar.addAction(self.menuPlik.menuAction())
        self.menubar.addAction(self.overlap40.menuAction())
        self.menubar.addAction(self.menusegmenty.menuAction())
        self.menubar.addAction(self.menuOkna.menuAction())
        self.menuOdtw_rz.addAction(self.calosc_odtworz)
        self.menuOdtw_rz.addAction(self.przedzial)
        self.menubar.addAction(self.menuOdtw_rz.menuAction())

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
        self.make_sonogram()

    def make_sonogram(self):

        f, t, amplitudy = self.stft(self.data, self.fs, nperseg=self.nperseg, noverlap=abs(self.nperseg*self.overlap), window=self.window)
        self.plot3 = pg.PlotWidget()
        amplitudy = abs(amplitudy)
        amplitudy = 20 * np.log10(amplitudy)
        #tworzenie sonogramu(obrazka)
        pg.setConfigOptions(imageAxisOrder='row-major')
        pg.mkQApp()
        win = pg.GraphicsLayoutWidget()

        self.img = pg.ImageItem()
        self.plot3.addItem(self.img)

        hist = pg.HistogramLUTItem()

        hist.setImageItem(self.img)

        win.addItem(hist)

        win.show()

        hist.setLevels(np.min(amplitudy), np.max(amplitudy))
        hist.gradient.restoreState(
            {'mode': 'rgb',
             'ticks': [(0.5, (0, 182, 188, 255)),
                       (1.0, (246, 111, 0, 255)),
                       (0.0, (75, 0, 113, 255))]})

        self.img.setImage(amplitudy)
        self.img.scale(t[-1] / np.size(amplitudy, axis=1),
                  f[-1] / np.size(amplitudy, axis=0))
        self.plot3.setLabel('bottom', "Time", units='s')
        self.plot3.setLabel('left', "Frequency", units='Hz')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Piorun"))
        self.menuPlik.setTitle(_translate("MainWindow", "Plik"))
        self.overlap40.setTitle(_translate("MainWindow", "Długość zakładki"))
        self.menusegmenty.setTitle(_translate("MainWindow", "Długość próbki"))
        self.menuOkna.setTitle(_translate("MainWindow", "Okna"))
        self.otworz_plik.setText(_translate("MainWindow", "otwórz"))
        self.overlap_10.setText(_translate("MainWindow", "10"))
        self.overlap20.setText(_translate("MainWindow", "20"))
        self.overlap30.setText(_translate("MainWindow", "30"))
        self.action40.setText(_translate("MainWindow", "40"))
        self.overlap50.setText(_translate("MainWindow", "50"))
        self.segment_256.setText(_translate("MainWindow", "256"))
        self.segment_512.setText(_translate("MainWindow", "512"))
        self.segment_1024.setText(_translate("MainWindow", "1024"))

        self.segment_32.setText(_translate("MainWindow", "32"))

        self.actiontriang.setText(_translate("MainWindow", "triang"))
        self.actionblackman.setText(_translate("MainWindow", "blackman"))
        self.actionhamming.setText(_translate("MainWindow", "hamming"))
        self.actionhann.setText(_translate("MainWindow", "hann"))
        self.actionflattop.setText(_translate("MainWindow", "flattop"))
        self.actionparzen.setText(_translate("MainWindow", "parzen"))
        self.calosc_odtworz.setText(_translate("MainWindow", "Całość"))
        self.przedzial.setText(_translate("MainWindow", "Przedział"))
        self.menuOdtw_rz.setTitle(_translate("MainWindow", "Odtwórz"))




    def update_state(self,new_path,MainWindow):
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


    def stft(self,x, fs=1.0, window='hann', nperseg=256, noverlap=None):

        x = np.asarray(x)

        outdtype = np.result_type(x, np.complex64)


        if x.size == 0:
            return np.empty(x.shape), np.empty(x.shape), np.empty(x.shape)

        if nperseg is not None:  # jeśli dane przez użytkownika
            nperseg = int(nperseg)
            if nperseg < 1:
                raise ValueError('nperseg must be a positive integer')


        win, nperseg = self.dziel_na_segmenty(window, nperseg,input_length=x.shape[-1])



        if noverlap is None:
            noverlap = nperseg//2
        else:
            noverlap = int(noverlap)


        if np.result_type(win,np.complex64) != outdtype:
            win = win.astype(outdtype)



        scale = 1.0 / win.sum()**2



        scale = np.sqrt(scale)


        if np.iscomplexobj(x):
            sides = 'twosided'
        else:
            sides = 'onesided'

        #liczenie częstotliwości
        if sides == 'twosided':
            freqs = fftpack.fftfreq(nperseg, 1/fs)
        elif sides == 'onesided':
            freqs = np.fft.rfftfreq(nperseg, 1/fs)

        #liczenie fft
        result = self.licz_fft(x, win, self.detrend_func, nperseg, noverlap, sides)
        #skalowanie
        result *= scale
        #liczenie czasu
        time = np.arange(nperseg/2, x.shape[-1] - nperseg/2 + 1,
                         nperseg - noverlap)/float(fs)

        result = result.astype(outdtype)





        result = np.rollaxis(result, -1, -2)

        return freqs, time, result


    def dziel_na_segmenty(self,window, nperseg,input_length):



        if nperseg > input_length:
            nperseg = input_length
        win = get_window(window, nperseg)

        return win, nperseg

    def licz_fft(self,x, win, detrend_func, nperseg, noverlap, sides):

        # Created strided array of data segments
        if nperseg == 1 and noverlap == 0:
            result = x[..., np.newaxis]
        else:
            step = nperseg - noverlap
            shape = x.shape[:-1]+((x.shape[-1]-noverlap)//step, nperseg)
            strides = x.strides[:-1]+(step*x.strides[-1], x.strides[-1])
            result = np.lib.stride_tricks.as_strided(x, shape=shape,
                                                     strides=strides)

        # Detrend each data segment individually
        result = detrend_func(result)

        # Apply window by multiplication
        result = win * result

        # Perform the fft. Acts on last axis by default. Zero-pads automatically
        if sides == 'twosided':
            func = fftpack.fft
        else:
            result = result.real
            func = np.fft.rfft
        result = func(result, n=nperseg)

        return result

    def detrend_func(self,d):
        return signaltools.detrend(d, type='constant', axis=-1)





