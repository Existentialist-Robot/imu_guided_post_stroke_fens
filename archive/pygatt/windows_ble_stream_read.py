from threading import Thread
import pygatt
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
import scipy.fftpack
import numpy as np

class comPlot:
    def __init__(self, comPort = 'COM5', mcuAddress = '0A:54:F1:E2:B3:C1', data_len = 100, dataNumBytes = 2):
        self.port = comPort
        self.address = mcuAddress
        self.data_buff_len = data_len
        self.dataNumBytes = dataNumBytes
        self.rawData = bytearray(dataNumBytes)
        self.data = collections.deque([0] * data_len * 2, maxlen=data_len)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        # self.samples_per_sec = 100
        self.read_UUID = "C8F88594-2217-0CA6-8F06-A4270B675D69"
        # self.write_UUID = "E3ADBF53-950E-DC1D-9B44-076BE52760D6"

        # self.csvData = []

        self.adapter = pygatt.BGAPIBackend(serial_port=self.port) #virtual COM port for the BlueGiga dongle
        
        print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.address))
        
        try:
            self.adapter.start()
            self.device = self.adapter.connect(self.address) 
            print(self.device)
            print('Connected!')

            print('Wrote ')
        except(pygatt.exceptions.NotConnectedError):
            print('Failed to connect to: ' + str(self.port) + ' at ' + str(self.address))

    def readStart(self):
        if self.thread == None:
            self.thread = Thread(target=self.backgroundThread)
            self.thread.start()
            # Block till we start receiving values
            # while self.isReceiving != True:
            time.sleep(1.0)

    def getcomData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000) # the first reading will be erroneous
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        print(self.rawData)
        # value,  = struct.unpack('f', self.rawData)    # use 'h' for a 2 byte integer
        # self.data.append(self.rawData)    # we get the latest data point and append it to our array
        # print(self.data)

        value,  = struct.unpack('f', self.rawData)    # use 'h' for a 2 byte integer, 'f' for four
        # print(value)
        self.data.append(value)    # we get the latest data point and append it to our array
        # print(self.data)
        lines.set_data(range(self.data_buff_len), self.data)
        # lines.set_data()

        lineValueText.set_text('[' + lineLabel + '] = ' + str(value))

    def backgroundThread(self):    # retrieve data
        time.sleep(1.0)  # give some buffer time for retrieving data
        while (self.isRun):
            self.rawData = self.device.char_read(self.read_UUID)
            # self.data.append(self.rawData)    # we get the latest data point and append it to our array

            # print(self.rawData)
            self.isReceiving = True

    def close(self):
        self.isRun = False
        self.thread.join()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')

def main():
    portName = 'COM5'     # for windows users
    # portName = '/dev/ttyUSB0' # for linux users
    mcuAddress = '0A:54:F1:E2:B3:C1'
    data_buff = 20 # higher data in buffer means higher frequency resolution but lower responsivity AND amplitude
    dataNumBytes = 4        # number of bytes of 1 data point
    s = comPlot(portName, mcuAddress, data_buff, dataNumBytes)   # initializes all required variables
    s.readStart()                                               # starts background thread

    # plotting starts below
    pltInterval = 50    # Period at which the plot animation updates [ms]
    xmin = 0
    xmax = data_buff
    ymin = -1
    ymax = 1
    fig = plt.figure()
    ax = plt.axes(xlim=(xmin, xmax), ylim=(ymin, ymax))
    ax.set_title('Arduino BLE Read')
    ax.set_xlabel("Time")
    ax.set_ylabel("Amplitude")

    lineLabel = 'Test'
    timeText = ax.text(0.50, 0.95, '', transform=ax.transAxes)
    lines = ax.plot([], [], label=lineLabel)[0]
    lineValueText = ax.text(0.50, 0.90, '', transform=ax.transAxes)
    anim = animation.FuncAnimation(fig, s.getcomData, fargs=(lines, lineValueText, lineLabel, timeText), interval=pltInterval)    # fargs has to be a tuple

    plt.legend(loc="upper left")
    plt.show()

    s.close()


if __name__ == '__main__':
    main()