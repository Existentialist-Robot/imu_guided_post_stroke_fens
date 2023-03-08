import pygatt
from binascii import hexlify
import struct

import asyncio

# This values was randomly generated - it must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well
read_UUID = '917649A1-D98E-11E5-9EEC-0002A5D5C51B'

READ = False


async def readArduino(device):
    global READ
    
    val = input("Enter 'r' to read :")
    # print(val)

    if ('r' in val):
        bytearray_x = device.char_read(read_UUID)
        print(bytearray_x)
        values = struct.unpack('3f',bytearray_x)
        print(values)
        print(values[0])
        print(values[1])
        print(values[2])
        print(type(values))

async def run():
    global TDCS

    print('Arduino Nano BLE LED Peripheral Central Service')
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')
 
    adapter = pygatt.BGAPIBackend(serial_port= 'COM5') #virtual COM port for the BlueGiga dongle

    try:
        adapter.start()
        device = adapter.connect('0A:54:F1:E2:B3:C1') 
        # device = adapter.connect('C8:87:39:14:AC:BF') 
        print(device)
                    
        print('Connected!')

        while True:
            await readArduino(device)

    except(pygatt.exceptions.NotConnectedError):
        print('Could not find Arduino Nano 33 BLE Sense Peripheral')

         
loop = asyncio.get_event_loop()

try:
    loop.run_until_complete(run())

except KeyboardInterrupt:
    print('\nReceived Keyboard Interrupt')

finally:
    print('Program finished')
