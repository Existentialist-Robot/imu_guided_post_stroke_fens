# interfaces with BLE_float_peripheral

from threading import Thread
import pygatt
import time
import collections
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import struct
# import scipy.fftpack
import numpy as np

class comPlot:
    def __init__(self, comPort = 'COM5', mcuAddress = 'C8:87:39:14:AC:BF', data_len = 100, dataNumBytes = 2):
        self.port = comPort
        self.address = mcuAddress
        self.data_buff_len = data_len
        self.dataNumBytes = dataNumBytes
        self.rawData = bytearray(dataNumBytes)
        self.value = None
        self.data = collections.deque([0] * data_len * 2, maxlen=data_len)
        self.isRun = True
        self.isReceiving = False
        self.thread = None
        self.plotTimer = 0
        self.previousTimer = 0
        # self.samples_per_sec = 100
        self.read_UUID = "C8F88594-2217-0CA6-8F06-A4270B675D69"
        self.write_UUID = "E3ADBF53-950E-DC1D-9B44-076BE52760D6"
        self.interval = 1
        self.curAmp = 0.5
        self.ampTop = 2
        self.prevTime = time.time()
        self.count = 0

        self.adapter = pygatt.BGAPIBackend(serial_port=self.port) #virtual COM port for the BlueGiga dongle
        
        print('Trying to connect to: ' + str(self.port) + ' at ' + str(self.address))
        
        try:
            self.adapter.start()
            self.device = self.adapter.connect(self.address) 
            print(self.device)
            print('Connected!')
        except(pygatt.exceptions.NotConnectedError):
            print('Failed to connect to: ' + str(self.port) + ' at ' + str(self.address))

    def readStart(self):
        self.device.subscribe(self.read_UUID, callback=self.subscribeCallback, indication=False, wait_for_response=True)

    def getcomData(self, frame, lines, lineValueText, lineLabel, timeText):
        currentTimer = time.perf_counter()
        self.plotTimer = int((currentTimer - self.previousTimer) * 1000) # the first reading will be erroneous
        self.previousTimer = currentTimer
        timeText.set_text('Plot Interval = ' + str(self.plotTimer) + 'ms')
        
        # print(self.rawData)

        lines.set_data(range(self.data_buff_len), self.data)
        lineValueText.set_text('[' + lineLabel + '] = ' + str(self.value))

    def subscribeCallback(self, handle, value):
        if self.isReceiving == False:
            time.sleep(2)
            print(handle)
            print(value)
            self.isReceiving = True
            print("self.isReceiving == True")
        else:

            # self.rawData = self.device.char_read(self.read_UUID)
            self.value,  = struct.unpack('f', value)    # use 'h' for a 2 byte integer, 'f' for four
            # print(value)
            self.data.append(self.value)    # we get the latest data point and append it to our array
          
            # if self.count > 200:
            #     print(self.data)
            #     curTime = time.time()
            #     if curTime - self.prevTime > self.interval:
            #         if self.curAmp >= self.ampTop - 0.1:
            #             self.curAmp = 0.5
            #         else:
            #             self.curAmp += 0.1
            #         print(self.curAmp)
            #         send_val = bytearray(struct.pack('>f',self.curAmp))
            #         print(send_val)
            #         send_val = struct.pack('>f',self.curAmp)
            #         print(send_val)
            #         print(type(send_val))
            #         print("length of send_val:", len(send_val))
            #         print([ "0x%02x" % b for b in send_val])
            #         true_val = [b for b in send_val]
            #         print(true_val)
            #         self.device.char_write_long(self.write_UUID, bytearray([0x01]))
            #         # self.device.char_write_long(self.write_UUID, bytearray([0x3f, 0xc0, 0x00, 0x00]))
        self.count += 1  
            

    def close(self):
        self.isRun = False
        # self.thread.join()
        print('Disconnected...')
        # df = pd.DataFrame(self.csvData)
        # df.to_csv('/home/rikisenia/Desktop/data.csv')

def main():
    portName = 'COM5'     # for windows users
    # portName = '/dev/ttyUSB0' # for linux users
    mcuAddress = 'C8:87:39:14:AC:BF' # '0A:54:F1:E2:B3:C1'
    data_buff = 100 # higher data in buffer means higher frequency resolution but lower responsivity AND amplitude
    dataNumBytes = 4        # number of bytes of 1 data point
    s = comPlot(portName, mcuAddress, data_buff, dataNumBytes)   # initializes all required variables
    time.sleep(2)
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