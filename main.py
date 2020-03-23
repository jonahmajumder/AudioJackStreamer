from PyQt5 import QtCore, QtWidgets, QtGui, uic
from matplotlib.backends.backend_qt5agg import (
        FigureCanvas, NavigationToolbar2QT as NavigationToolbar)
from matplotlib.figure import Figure
import numpy as np
from scipy.signal import periodogram
from time import time

from stream import Streamer

class AudioStreamGUI(QtWidgets.QMainWindow):
    DATAHISTORY = 5000

    def __init__(self, parent):
        QtWidgets.QDialog.__init__(self)

        self.parent = parent
        # get ui
        self.ui = uic.loadUi('mainwindow.ui')
        self.ui.setWindowTitle('Audio Jack Streamer')

        self.makeFigs()

        screenFrac = [0.6, 0.6]
        self.resizeWindow(screenFrac)

        self.setupStream()

        self.connectCallbacks()

        self.startui()

    def startui(self):

        # when everything is ready
        self.ui.show()
        self.ui.raise_()
        return

    def makeFigs(self):
        self.timeCanvas = FigureCanvas(Figure())
        self.freqCanvas = FigureCanvas(Figure())

        self.timeAxes = self.timeCanvas.figure.add_subplot(111)
        self.freqAxes = self.freqCanvas.figure.add_subplot(111)

        self.timeAxes.set_xlabel('Time (s)')
        self.timeAxes.set_ylabel('Signal (ADC)')
        self.freqAxes.set_xlabel('Freq (Hz)')
        self.freqAxes.set_ylabel('FFT Signal (* / rtHz)')

        self.timeAxes.set_autoscale_on(True)
        # self.freqAxes.set_autoscale_on(True)
        self.freqAxes.set_xlim([0, 2000])

        self.timeLine, = self.timeAxes.plot([], [])

        self.ui.plotContainer.addWidget(self.timeCanvas)
        self.ui.plotContainer.addWidget(self.freqCanvas)

    def connectCallbacks(self):
        self.ui.startButton.clicked.connect(self.startFcn)
        self.ui.stopButton.clicked.connect(self.stopFcn)

        self.ui.updateRate.setValue(self.streamer.DATARATE)
        self.ui.chunkSize.setValue(self.streamer.CHUNK)
        self.ui.updateRate.valueChanged.connect(self.updateRateChangedFcn)

        self.ui.historyLength.setValue(self.DATAHISTORY)
        self.ui.historyLength.valueChanged.connect(self.historyLengthChangedFcn)

    def setupStream(self):
        self.streamer = Streamer()
        self.streamer.dataHandler = self.processData

    def processData(self, data, elapsed):
        # st = time()

        timedata = data
        timeax = np.arange(len(data)) / self.streamer.SAMPLERATE

        olddata = self.timeLine.get_ydata()
        newdata = np.hstack((olddata, timedata))[-self.DATAHISTORY:]

        freqax, freqdata = periodogram(newdata, self.streamer.SAMPLERATE)

        self.timeAxes.clear()
        self.timeLine, = self.timeAxes.plot(newdata)

        self.freqAxes.clear()
        self.freqAxes.plot(freqax, freqdata)

        self.timeCanvas.draw()
        self.freqCanvas.draw()

        self.ui.streamTimer.display(elapsed)

        # print(time() - st)

    def startFcn(self):
        self.ui.stopButton.setEnabled(True)
        self.ui.startButton.setEnabled(False)

        self.streamer.start()

    def stopFcn(self):
        self.ui.startButton.setEnabled(True)
        self.ui.stopButton.setEnabled(False)
        self.streamer.stop()

    def updateRateChangedFcn(self):
        if self.streamer.stream is not None:
            self.streamer.stop()
            self.streamer.DATARATE = self.ui.updateRate.value()
            self.streamer.start()
        else:
            self.streamer.DATARATE = self.ui.updateRate.value()

        self.ui.chunkSize.setValue(int(self.streamer.SAMPLERATE / self.streamer.DATARATE))

    def historyLengthChangedFcn(self):
        self.DATAHISTORY = self.ui.historyLength.value()

    def resizeWindow(self, screenFraction):
        desktop = self.parent.desktop()
        geom = self.ui.geometry()
        geom.setWidth(int(screenFraction[0] * desktop.geometry().width()))
        geom.setHeight(int(screenFraction[1] * desktop.geometry().height()))
        geom.moveCenter(desktop.geometry().center())
        self.ui.setGeometry(geom)

app = QtWidgets.QApplication([])
gui = AudioStreamGUI(app)

if __name__ == '__main__':
    app.exec_()