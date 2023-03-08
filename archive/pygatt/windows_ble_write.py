import pygatt
from binascii import hexlify
import struct
import asyncio

# This values was randomly generated - it must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well
ping_UUID = '19B10001-E8F2-537E-4F6C-D104768A1214'

# on_value = bytearray([0x01])
# on_value = struct.pack("<f",0.1235)
on_value = bytearray(struct.pack(">f",0.1235))
print("init on_value:")
print(on_value)
off_value = bytearray([0x00])

ping = False

def getValue(on):
    if on:
        return on_value
    else:
        return off_value

async def setCircuit(device):
    global ping

    cur_val = device.char_read(ping_UUID)
    print("cur_val: ".format(cur_val))
    
    val = input("Enter 't' to toggle ping circuit :")
    print(val)

    if ('t' in val):
        ping = not ping
        device.char_write(ping_UUID, getValue(ping))
        print("Wrote".format((getValue(ping))))


async def run():
    global ping

    print('Arduino Nano BLE LED Peripheral Central Service')
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')
 
    adapter = pygatt.BGAPIBackend(serial_port= 'COM5') #virtual COM port for the BlueGiga dongle

    try:
        adapter.start()
        device = adapter.connect('0A:54:F1:E2:B3:C1') 
        # device = adapter.connect('C8:87:39:14:AC:BF') 
        print(device)
            
        #Check initial state of circuit
        print('Connected!')
        val = device.char_read(ping_UUID)
        if (val == on_value):
            print ('CIRCUIT ON')
            ping = True
        else:
            print ('CIRCUIT OFF')
            ping = False

        while True:
            await setCircuit(device)

    except(pygatt.exceptions.NotConnectedError):
        print('Could not find Arduino Nano 33 BLE Sense Peripheral')


                    
loop = asyncio.get_event_loop()
try:
    loop.run_until_complete(run())
except KeyboardInterrupt:
    print('\nReceived Keyboard Interrupt')
finally:
    print('Program finished')
