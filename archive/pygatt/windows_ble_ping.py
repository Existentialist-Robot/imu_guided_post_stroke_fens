import pygatt
from binascii import hexlify
import struct
import time

import asyncio

# This values was randomly generated - it must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well

class pingTest:
    def __init__(self):
        self.start_UUID = '9A48ECBA-2E92-082F-C070-9E75AAE428B1'
        self.ping_UUID = 'C8F88594-2217-0CA6-8F06-A4270B675D69'
        self.response_UUID = 'E3ADBF53-950E-DC1D-9B44-076BE52760D6'
        self.mcuAddress = '0A:54:F1:E2:B3:C1'
        self.data = []
        # self.isReceiving = False
        self.times = []
        self.on_value = bytearray([0x01])
        self.off_value = bytearray([0x00])
        self.on = False
        self.count = 0 
        self.start_time = None
        self.last_time = None

        self.adapter = pygatt.BGAPIBackend(serial_port= 'COM5') #virtual COM port for the BlueGiga dongle
        
        try:
            self.adapter.start()
            self.device = self.adapter.connect(self.mcuAddress) # device = adapter.connect('C8:87:39:14:AC:BF') 
            print(self.device)        
            print('Connected!')
        except(pygatt.exceptions.NotConnectedError):
            print('Could not find Arduino Nano 33 BLE Sense Peripheral')

    def startSubscribe(self):
        ("subscribing to ping characteristic\n")
        self.device.subscribe(self.ping_UUID, callback=self.subscribeCallback, indication=False, wait_for_response=True)

    def startPing(self):
        self.device.char_write(self.start_UUID, self.on_value)
        self.start_time = time.time()
        self.last_time = self.start_time
        print("starting Ping sent")

    def subscribeCallback(self, handle, value):
        if(self.count <10000):
            now = time.time()
            try:
                self.device.char_write(self.response_UUID, self.on_value)
            except:
                pass
            time_diff = now - self.last_time
            self.times.append(time_diff)
            self.last_time = now
            self.count+=1
        else:
            print(self.times)
            print(sum(self.times)/len(self.times))
        
def main():
    p = pingTest()
    print("attempting to START subscribing")
    p.startSubscribe()
    print("attempting to START first PING")
    time.sleep(2)
    p.startPing()
    while(True):
        time.sleep(0.001)

if __name__ == '__main__':
    main()
