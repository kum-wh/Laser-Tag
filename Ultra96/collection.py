from operator import length_hint
import socket
import threading
import queue
import random
from GameState import GameState
import base64
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
import json
import paho.mqtt.client as mqtt 
from colorama import Fore
from colorama import Style
from pynq import Overlay
from pynq import allocate
import numpy as np
import time
from struct import *

imu_time = 0
length = 0

'''
Between Viz and U96:
MQTT

grenade query: str ("g")
grenade_hit_or_miss: str ("t" or "f")
game_state: JSON
'''

queue_ai = queue.Queue() # Relay -> AI (sensor readings: str)

def padd():
    while True:
        if ((time.time() - imu_time > 1) and length != 0):
            #print("INSIDE ELIF")
            for i in range(100 - length):
                queue_ai.put(b'W\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')
            time.sleep(1)

class Relay():
    def __init__(self):
        self.server_ip_address = 'localhost'
        self.listening_port = 4002 # Change to 4002
        self.address = ('', self.listening_port)
        self.header = 64
        self.format = 'utf-8'
        
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(self.address)

    def handle_client(self, connection, address):
        print(f"[NEW CONNECTION] {address} is now connected.")

        while True:
            # if ((time.time() - imu_time > 5) and length != 0):
            #     print("INSIDE ELIF")
            #     for i in range(100 - length):
            #         queue_ai.put(b'W\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00\x00')

            message_length_in_byte = connection.recv(self.header)

            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int)

                queue_ai.put(message)
                print(f"{Fore.GREEN}[MESSAGE RECEIVED] {address}: {message}{Style.RESET_ALL}")

                connection.send("[MESSAGE RECEIVED] Your message is received!".encode(self.format))
            
        
        connection.close() # Do not need to close

    def run(self):
        self.server.listen()
        print(f"[LISTENING] Server is listening on {self.server_ip_address}:{self.listening_port}")

        while True:
            connection, address = self.server.accept()
            thread = threading.Thread(target = self.handle_client, args = (connection, address))
            thread.start()
            print(f"[ACTIVE CONNECTIONS] {threading.active_count() - 1}")
        

class AI():
    def __init__(self):
        self.MAXIMUM_COUNTER = 100
        self.x = []
        self.y = []
        self.z = []
        self.gx = []
        self.gy = []
        self.gz = []
        self.counter = 0

    def ai(self):
        pass

    def run(self):
        while True:
            sensor_reading = queue_ai.get()

            # sensor_reading_in_dict = json.loads(sensor_reading)
            unpacked_sensor_reading = unpack('<b''6h''b''3h',  sensor_reading)
            print(f"AI HAS RECEIVED SENSOR READING {unpacked_sensor_reading}")

            if unpacked_sensor_reading[0] == 87: # IMU 87
                global imu_time
                global length
                imu_time = time.time()

                self.x.append(unpacked_sensor_reading[1]) 
                self.y.append(unpacked_sensor_reading[2]) 
                self.z.append(unpacked_sensor_reading[3]) 
                self.gx.append(unpacked_sensor_reading[4]) 
                self.gy.append(unpacked_sensor_reading[5]) 
                self.gz.append(unpacked_sensor_reading[6])
                
                '''
                if output_buffer[0] == 1:
                    return "grenade"
                elif output_buffer[0] == 2:
                    return "shield"
                elif output_buffer[0] == 3:
                    return "reload"
                elif output_buffer[0] == 4:
                    return "none"
                elif output_buffer[0] == 5:
                    return "logout"   
                '''

                length = len(self.x) #length += 1
                print(f"{length} number of IMU sensor readings are received!")
                print(length == self.MAXIMUM_COUNTER)

                action_num = 5
                if (length == self.MAXIMUM_COUNTER):
                    with open("x.txt","a") as f:
                        f.write(str(self.x) + "\n")
                    with open("y.txt","a") as f:
                        f.write(str(self.y) + "\n")
                    with open("z.txt","a") as f:
                        f.write(str(self.z) + "\n")
                    with open("gx.txt","a") as f:
                        f.write(str(self.gx) + "\n")
                    with open("gy.txt","a") as f:
                        f.write(str(self.gy) + "\n")
                    with open("gz.txt","a") as f:
                        f.write(str(self.gz) + "\n")
                    with open("label.txt","a") as f:
                        f.write(str(action_num) + "\n")

                    self.x.clear()
                    self.y.clear()
                    self.z.clear()
                    self.gx.clear()
                    self.gy.clear()
                    self.gz.clear()

                    length = 0

                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {action_num}{Style.RESET_ALL}')




relay = Relay()
ai = AI()

t1 = threading.Thread(target=relay.run, args=())
t2 = threading.Thread(target=ai.run, args=())
t7 = threading.Thread(target=padd, args=())

t1.start()
t2.start()
t7.start()

t1.join()
t2.join()
t7.join()
