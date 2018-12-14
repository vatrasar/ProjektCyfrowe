
import pyqtgraph as pg
from scipy.io import wavfile
from PyQt5 import QtCore, QtWidgets
import numpy as np
from scipy import fftpack
from scipy.signal import signaltools
from scipy.signal._arraytools import const_ext
from scipy._lib.six import string_types
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
        self.make_sonogram()

    def make_sonogram(self):

        f, t, amplitudy = self.stft(self.data, self.fs, nperseg=256, noverlap=256 // 2, window='hann')
        self.plot3 = pg.PlotWidget()
        amplitudy = abs(amplitudy)
        amplitudy = 20 * np.log10(amplitudy)
        #tworzenie sonogramu(obrazka)
        pg.setConfigOptions(imageAxisOrder='row-major')
        pg.mkQApp()
        win = pg.GraphicsLayoutWidget()

        img = pg.ImageItem()
        self.plot3.addItem(img)

        hist = pg.HistogramLUTItem()

        hist.setImageItem(img)

        win.addItem(hist)

        win.show()

        hist.setLevels(np.min(amplitudy), np.max(amplitudy))
        hist.gradient.restoreState(
            {'mode': 'rgb',
             'ticks': [(0.5, (0, 182, 188, 255)),
                       (1.0, (246, 111, 0, 255)),
                       (0.0, (75, 0, 113, 255))]})

        img.setImage(amplitudy)

        img.scale(t[-1] / np.size(amplitudy, axis=1),
                  f[-1] / np.size(amplitudy, axis=0))
        self.plot3.setLabel('bottom', "Time", units='s')
        self.plot3.setLabel('left', "Frequency", units='Hz')

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MainWindow"))
        self.menuPlik.setTitle(_translate("MainWindow", "Plik"))
        self.otworz.setText(_translate("MainWindow", "otwórz"))

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


    def stft(self,x, fs=1.0, window='hann', nperseg=None, noverlap=None,
                         nfft=None, axis=-1, boundary=None):

        detrend = 'constant'

        axis = int(axis)


        x = np.asarray(x)

        outdtype = np.result_type(x, np.complex64)


        if x.size == 0:
            return np.empty(x.shape), np.empty(x.shape), np.empty(x.shape)


        if x.ndim > 1:
            if axis != -1:
                x = np.rollaxis(x, axis, len(x.shape))


        if nperseg is not None:  # if specified by user
            nperseg = int(nperseg)
            if nperseg < 1:
                raise ValueError('nperseg must be a positive integer')


        win, nperseg = self.dziel_na_segmenty(window, nperseg,input_length=x.shape[-1])

        if nfft is None:
            nfft = nperseg
        elif nfft < nperseg:
            raise ValueError('nfft must be greater than or equal to nperseg.')
        else:
            nfft = int(nfft)

        if noverlap is None:
            noverlap = nperseg//2
        else:
            noverlap = int(noverlap)
        if noverlap >= nperseg:
            raise ValueError('noverlap must be less than nperseg.')
        # nstep = nperseg - noverlap
        # if boundary is not None:
        #     ext_func =const_ext
        #     x = ext_func(x, nperseg//2, axis=-1)

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
            freqs = fftpack.fftfreq(nfft, 1/fs)
        elif sides == 'onesided':
            freqs = np.fft.rfftfreq(nfft, 1/fs)

        #liczenie fft
        result = self.licz_fft(x, win, self.detrend_func, nperseg, noverlap, nfft, sides)
        #skalowanie
        result *= scale
        #liczenie czasu
        time = np.arange(nperseg/2, x.shape[-1] - nperseg/2 + 1,
                         nperseg - noverlap)/float(fs)

        result = result.astype(outdtype)


        if axis < 0:
            axis -= 1


        result = np.rollaxis(result, -1, axis)

        return freqs, time, result


    def dziel_na_segmenty(self,window, nperseg,input_length):


        if nperseg is None:
            nperseg = 256  # then change to default
        if nperseg > input_length:
            nperseg = input_length
        win = get_window(window, nperseg)

        return win, nperseg

    def licz_fft(self,x, win, detrend_func, nperseg, noverlap, nfft, sides):

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
        result = func(result, n=nfft)

        return result

    def detrend_func(self,d):
        return signaltools.detrend(d, type='constant', axis=-1)





