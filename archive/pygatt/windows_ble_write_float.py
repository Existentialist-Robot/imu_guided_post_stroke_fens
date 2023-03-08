# works with CallbackLED_debug_recieving_floats_from_PC script

import pygatt
import struct

# This values was randomly generated - it must match between the Central and Peripheral devices
# Any changes you make here must be suitably made in the Arduino program as well
ping_UUID = '19B10001-E8F2-537E-4F6C-D104768A1214'

on_value = struct.pack("f",0.1235)
print("init on_value:")
print(on_value)
off_value = bytearray([0x00])

ping = False

adapter = pygatt.BGAPIBackend(serial_port= 'COM5') #virtual COM port for the BlueGiga dongle

def getValue(on):
    if on:
        return on_value
    else:
        return off_value

try:
    adapter.start()
    device = adapter.connect('0A:54:F1:E2:B3:C1') 
    # device = adapter.connect('C8:87:39:14:AC:BF') 
    print(device)
        
    #Check initial state of circuit
    print('Connected!')
except:
    print("didn't connect")

while True: 
    val = input("Enter 't' to toggle ping circuit :")
    print(val)

    if ('t' in val):
        ping = not ping
        device.char_write(ping_UUID, getValue(ping))
        print("Wrote".format((getValue(ping))))

