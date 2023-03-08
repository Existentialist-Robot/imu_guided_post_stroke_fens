from binascii import hexlify
import struct
import time

# import asyncio

import pygame
import math
from OpenGL.GL import *
from OpenGL.GLU import *
from pygame.locals import *

streamType = "BLE" # set to BLE, Serial, or Wifi
useQuat = False   # set true for using quaternions, false for using y,p,r angles

"""
Can initialize the type of data sent back based on the starting bytestring passed to arduino
init_cmd[0] = mode (currently only BLE)
init_cmd[1] = initial time stamp
init_cmd[2] = data to send back (raw = 0, quat = 1, euler = 2)
init_cmd[3] = ?

Data packets recieved - eventually (not currently implmented)
charatistic_1 = timestamp, count
charatistic_3 = yaw, pitch, roll
charatistic_4 = linear accel, , 
charatistic_5 = timestamp


""" 

if(streamType == 'BLE'):
    import pygatt
    data = None
    read_UUID = 'C8F88594-2217-0CA6-8F06-A4270B675D68'
    print('Arduino Nano BLE LED Peripheral Central Service')
    print('Looking for Arduino Nano 33 BLE Sense Peripheral Device...')
    adapter = pygatt.BGAPIBackend(serial_port= 'COM5') #virtual COM port for the BlueGiga dongle
    try:
        adapter.start()
        device = adapter.connect('0A:54:F1:E2:B3:C1') # device = adapter.connect('C8:87:39:14:AC:BF') 
        print(device)        
        print('Connected!')
    except(pygatt.exceptions.NotConnectedError):
        print('Could not find Arduino Nano 33 BLE Sense Peripheral')
    isReceiving = False
elif(streamType == 'Serial'):
    import serial
    ser = serial.Serial('/dev/ttyUSB0', 38400)
elif(streamType == 'Wifi'):
    import socket
    UDP_IP = "0.0.0.0"
    UDP_PORT = 5005
    sock = socket.socket(socket.AF_INET, # Internet
                         socket.SOCK_DGRAM) # UDP
    sock.bind((UDP_IP, UDP_PORT))

def main():
    video_flags = OPENGL | DOUBLEBUF
    pygame.init()
    screen = pygame.display.set_mode((640, 480), video_flags)
    pygame.display.set_caption("PyTeapot IMU orientation visualization")
    resizewin(640, 480)
    init()
    frames = 0
    ticks = pygame.time.get_ticks()
    while 1:
        event = pygame.event.poll()
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            break
        if(useQuat):
            [w, nx, ny, nz] = read_data()
        else:
            [yaw, pitch, roll] = read_data()
        if(useQuat):
            draw(w, nx, ny, nz)
        else:
            draw(1, yaw, pitch, roll)
        pygame.display.flip()
        frames += 1
    print("fps: %d" % ((frames*1000)/(pygame.time.get_ticks()-ticks)))
    if(streamType == 'Serial'):
        ser.close()

def resizewin(width, height):
    """
    For resizing window
    """
    if height == 0:
        height = 1
    glViewport(0, 0, width, height)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(45, 1.0*width/height, 0.1, 100.0)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()

def init():
    glShadeModel(GL_SMOOTH)
    glClearColor(0.0, 0.0, 0.0, 0.0)
    glClearDepth(1.0)
    glEnable(GL_DEPTH_TEST)
    glDepthFunc(GL_LEQUAL)
    glHint(GL_PERSPECTIVE_CORRECTION_HINT, GL_NICEST)

def cleanSerialBegin():
    if(useQuat):
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            w = float(line.split('w')[1])
            nx = float(line.split('a')[1])
            ny = float(line.split('b')[1])
            nz = float(line.split('c')[1])
        except Exception:
            pass
    else:
        try:
            line = ser.readline().decode('UTF-8').replace('\n', '')
            yaw = float(line.split('y')[1])
            pitch = float(line.split('p')[1])
            roll = float(line.split('r')[1])
        except Exception:
            pass

# def subscribeCallback(handle, value): # if using BLE
#     if isReceiving == False:
#         time.sleep(4)
#         print(handle)
#         print(value)
#         isReceiving = True
#         print("self.isReceiving == True")
#     else:
#         value,  = struct.unpack('3f', value)    # use 'h' for a 2 byte integer, 'f' for four
#         # print(value)
#         data.append(value)    # we get the latest data point and append it to our array
#         # print(self.data)


def read_data():
    if(streamType == 'BLE'):
        # device.subscribe(read_UUID, callback=subscribeCallback, indication=False, wait_for_response=True)
        data = device.char_read(read_UUID)
        print(data)
        line = struct.unpack('3f', data)    # use 'h' for a 2 byte integer, 'f' for four
    elif(streamType == 'Serial'):
        ser.reset_input_buffer()
        cleanSerialBegin()
        line = ser.readline().decode('UTF-8').replace('\n', '')
        print(line)
    elif(streamType == 'Serial'):
        # Waiting for data from udp port 5005
        data, addr = sock.recvfrom(1024) # buffer size is 1024 bytes
        line = data.decode('UTF-8').replace('\n', '')
        print(line)
                
    # if(useQuat):
    #     w = float(line.split('w')[1])
    #     nx = float(line.split('a')[1])
    #     ny = float(line.split('b')[1])
    #     nz = float(line.split('c')[1])
    #     return [w, nx, ny, nz]
    # else:
    #     yaw = float(line.split('y')[1])
    #     pitch = float(line.split('p')[1])
    #     roll = float(line.split('r')[1])
    #     return [yaw, pitch, roll]

    yaw = line[0]
    pitch = line[1]
    roll = line[2]
    return [yaw, pitch, roll]

def draw(w, nx, ny, nz):
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glTranslatef(0, 0.0, -7.0)

    drawText((-2.6, 1.8, 2), "PyTeapot", 18)
    drawText((-2.6, 1.6, 2), "Module to visualize quaternion or Euler angles data", 16)
    drawText((-2.6, -2, 2), "Press Escape to exit.", 16)

    if(useQuat):
        [yaw, pitch , roll] = quat_to_ypr([w, nx, ny, nz])
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(2 * math.acos(w) * 180.00/math.pi, -1 * nx, nz, ny)
    else:
        yaw = nx
        pitch = ny
        roll = nz
        drawText((-2.6, -1.8, 2), "Yaw: %f, Pitch: %f, Roll: %f" %(yaw, pitch, roll), 16)
        glRotatef(-roll, 0.00, 0.00, 1.00)
        glRotatef(pitch, 1.00, 0.00, 0.00)
        glRotatef(yaw, 0.00, 1.00, 0.00)

    glBegin(GL_QUADS)
    glColor3f(0.0, 1.0, 0.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(1.0, 0.2, 1.0)

    glColor3f(1.0, 0.5, 0.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(1.0, -0.2, -1.0)

    glColor3f(1.0, 0.0, 0.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)

    glColor3f(1.0, 1.0, 0.0)
    glVertex3f(1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, -1.0)

    glColor3f(0.0, 0.0, 1.0)
    glVertex3f(-1.0, 0.2, 1.0)
    glVertex3f(-1.0, 0.2, -1.0)
    glVertex3f(-1.0, -0.2, -1.0)
    glVertex3f(-1.0, -0.2, 1.0)

    glColor3f(1.0, 0.0, 1.0)
    glVertex3f(1.0, 0.2, -1.0)
    glVertex3f(1.0, 0.2, 1.0)
    glVertex3f(1.0, -0.2, 1.0)
    glVertex3f(1.0, -0.2, -1.0)
    glEnd()


def drawText(position, textString, size):
    font = pygame.font.SysFont("Courier", size, True)
    textSurface = font.render(textString, True, (255, 255, 255, 255), (0, 0, 0, 255))
    textData = pygame.image.tostring(textSurface, "RGBA", True)
    glRasterPos3d(*position)
    glDrawPixels(textSurface.get_width(), textSurface.get_height(), GL_RGBA, GL_UNSIGNED_BYTE, textData)

def quat_to_ypr(q):
    yaw   = math.atan2(2.0 * (q[1] * q[2] + q[0] * q[3]), q[0] * q[0] + q[1] * q[1] - q[2] * q[2] - q[3] * q[3])
    pitch = -math.asin(2.0 * (q[1] * q[3] - q[0] * q[2]))
    roll  = math.atan2(2.0 * (q[0] * q[1] + q[2] * q[3]), q[0] * q[0] - q[1] * q[1] - q[2] * q[2] + q[3] * q[3])
    pitch *= 180.0 / math.pi
    yaw   *= 180.0 / math.pi
    yaw   -= -0.13  # Declination at Chandrapur, Maharashtra is - 0 degress 13 min
    roll  *= 180.0 / math.pi
    return [yaw, pitch, roll]


if __name__ == '__main__':
    main()
