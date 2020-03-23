import pyaudio
import numpy as np

class Streamer(): 
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    SAMPLERATE = 40000
    DATARATE = 50 # Hz
    CHUNK = 800

    def __init__(self):
        self.paInstance = pyaudio.PyAudio()
        self.stream = None

        self.dataHandler = self.defaultHandler

        self.firstTimeRecorded = False
        self.streamStartTime = None

    def __del__(self):
        if self.stream is not None:
            self.stop()  

    def dataCallback(self, input_data, frame_count, time_info, flags):
        data = np.frombuffer(input_data, dtype=np.int16)
        adc_time = time_info['input_buffer_adc_time']

        if not self.firstTimeRecorded:
            self.streamStartTime = adc_time
            self.firstTimeRecorded = True

        elapsed = adc_time - self.streamStartTime

        self.dataHandler(data, elapsed)

        return input_data, pyaudio.paContinue

    def defaultHandler(self, data, time):
        print(np.mean(data), time)

    def start(self, block=False):
        self.CHUNK = int(self.SAMPLERATE / self.DATARATE)

        # print('Updating at {0:.2f} Hz'.format(self.SAMPLERATE / self.CHUNK))
        self.firstTimeRecorded = False

        self.stream = self.paInstance.open(format=self.FORMAT,
            channels=self.CHANNELS,
            rate=self.SAMPLERATE,
            input=True,
            stream_callback=self.dataCallback,
            frames_per_buffer=self.CHUNK)

        if block:
            self.waitForInterrupt()

    def stop(self):
        self.stream.close()
        self.stream = None

    def waitForInterrupt(self):
        try:
            while self.stream.is_active():
                pass
        except KeyboardInterrupt:
            self.stop()

if __name__ == '__main__':
    s = Streamer()
    # s.dataHandler = lambda data, time: print(len(data))
    s.start()