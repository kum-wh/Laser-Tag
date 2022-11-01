from operator import length_hint
from threading import Timer
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
# from pynq import Overlay
# from pynq import allocate
import numpy as np
import time
from struct import *

queue_ai = queue.Queue() # Relay -> AI (sensor readings: str)
queue_game_state = queue.Queue() # AI -> GameMechanics (greande_hit_or_miss: bool, non_grenade_action: str)
queue_greande_hit_or_miss = queue.Queue() # Viz -> AI (grenade_hit_or_miss: bool)

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
            message_length_in_byte = connection.recv(self.header)

            if message_length_in_byte:
                message_length_in_int = int(message_length_in_byte)
                message = connection.recv(message_length_in_int)
                queue_ai.put(message)
                # print(f"{Fore.GREEN}[MESSAGE RECEIVED] {address}: {message}{Style.RESET_ALL}")

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

        self.grenade_counter = 0
        self.shield_counter = 0
        self.reload_counter = 0
        self.logout_counter = 0
        self.grenade_counter2 = 0
        self.shield_counter2 = 0
        self.reload_counter2 = 0
        self.logout_counter2 = 0

        self.x1 = []
        self.y1 = []
        self.z1 = []
        self.gx1 = []
        self.gy1 = []
        self.gz1 = []

        self.x2 = []
        self.y2 = []
        self.z2 = []
        self.gx2 = []
        self.gy2 = []
        self.gz2 = []

    def ai(self):
        '''
        x_mean = np.mean(self.x1)
        y_mean = np.mean(self.y1)
        z_mean = np.mean(self.z1)
        gx_mean = np.mean(self.gx1)
        gy_mean = np.mean(self.gy1)
        gz_mean = np.mean(self.gz1)
        x_max = np.amax(self.x1)
        y_max = np.amax(self.y1)
        z_max = np.amax(self.z1)
        gx_max = np.amax(self.gx1)
        gy_max = np.amax(self.gy1)
        gz_max = np.amax(self.gz1)
        x_min = np.amin(self.x1)
        y_min = np.amin(self.y1)
        z_min = np.amin(self.z1)
        gx_min = np.amin(self.gx1)
        gy_min = np.amin(self.gy1)
        gz_min = np.amin(self.gz1)

        final = []

        for item in self.x1:
            final.append(item)
        for item in self.y1:
            final.append(item)
        for item in self.z1:
            final.append(item)
        for item in self.gx1:
            final.append(item)
        for item in self.gy1:
            final.append(item)
        for item in self.gz1:
            final.append(item)

        final.append(int(x_mean))
        final.append(int(y_mean))
        final.append(int(z_mean))
        final.append(int(gx_mean))
        final.append(int(gy_mean))
        final.append(int(gz_mean))
        final.append(int(x_max))
        final.append(int(y_max))
        final.append(int(z_max))
        final.append(int(gx_max))
        final.append(int(gy_max))
        final.append(int(gz_max))
        final.append(int(x_min))
        final.append(int(y_min))
        final.append(int(z_min))
        final.append(int(gx_min))
        final.append(int(gy_min))
        final.append(int(gz_min))

        
        input_buffer = allocate(shape=(318,), dtype=np.intc)
        output_buffer = allocate(shape=(1,), dtype=np.intc)

        for i in range(318):
            input_buffer[i] = final[i]

        dma.sendchannel.transfer(input_buffer)
        dma.recvchannel.transfer(output_buffer)
        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(f"REAL AI: {output_buffer[0]}")

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

        # For Testing
        grenade_counter2 = 0
        shield_counter2 = 0
        reload_counter2 = 0
        logout_counter2 = 0
        none_counter2 = 0
        for value in self.x1:
            if value == 0:
                reload_counter2 += 1
            elif value == 1:
                grenade_counter2 += 1
            elif value == 2:
                shield_counter2 += 1
            elif value == 3:
                logout_counter2 += 1
            elif value == 4:
                none_counter2 += 1
        
        if grenade_counter2 > shield_counter2 and grenade_counter2 > reload_counter2 and grenade_counter2 > logout_counter2 and grenade_counter2 > none_counter2:
            return "grenade"
        if shield_counter2 > grenade_counter2 and shield_counter2 > reload_counter2 and shield_counter2 > logout_counter2 and shield_counter2 > none_counter2:
            return "shield"
        if reload_counter2 > grenade_counter2 and reload_counter2 > shield_counter2 and reload_counter2 > logout_counter2 and reload_counter2 > none_counter2:
            return "reload"
        if logout_counter2 > grenade_counter2 and logout_counter2 > shield_counter2 and logout_counter2 > reload_counter2 and logout_counter2 > none_counter2:
            return "logout"
        return "none"


    def ai2(self):
        '''
        x_mean = np.mean(self.x2)
        y_mean = np.mean(self.y2)
        z_mean = np.mean(self.z2)
        gx_mean = np.mean(self.gx2)
        gy_mean = np.mean(self.gy2)
        gz_mean = np.mean(self.gz2)
        x_max = np.amax(self.x2)
        y_max = np.amax(self.y2)
        z_max = np.amax(self.z2)
        gx_max = np.amax(self.gx2)
        gy_max = np.amax(self.gy2)
        gz_max = np.amax(self.gz2)
        x_min = np.amin(self.x2)
        y_min = np.amin(self.y2)
        z_min = np.amin(self.z2)
        gx_min = np.amin(self.gx2)
        gy_min = np.amin(self.gy2)
        gz_min = np.amin(self.gz2)

        final2 = []

        for item in self.x2:
            final2.append(item)
        for item in self.y2:
            final2.append(item)
        for item in self.z2:
            final2.append(item)
        for item in self.gx2:
            final2.append(item)
        for item in self.gy2:
            final2.append(item)
        for item in self.gz2:
            final2.append(item)

        final2.append(int(x_mean))
        final2.append(int(y_mean))
        final2.append(int(z_mean))
        final2.append(int(gx_mean))
        final2.append(int(gy_mean))
        final2.append(int(gz_mean))
        final2.append(int(x_max))
        final2.append(int(y_max))
        final2.append(int(z_max))
        final2.append(int(gx_max))
        final2.append(int(gy_max))
        final2.append(int(gz_max))
        final2.append(int(x_min))
        final2.append(int(y_min))
        final2.append(int(z_min))
        final2.append(int(gx_min))
        final2.append(int(gy_min))
        final2.append(int(gz_min))

        
        input_buffer = allocate(shape=(318,), dtype=np.intc)
        output_buffer = allocate(shape=(1,), dtype=np.intc)

        for i in range(318):
            input_buffer[i] = final2[i]

        dma.sendchannel.transfer(input_buffer)
        dma.recvchannel.transfer(output_buffer)
        dma.sendchannel.wait()
        dma.recvchannel.wait()

        print(f"REAL AI: {output_buffer[0]}")

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

        # For Testing
        grenade_counter2 = 0
        shield_counter2 = 0
        reload_counter2 = 0
        logout_counter2 = 0
        none_counter2 = 0
        for value in self.x2:
            if value == 0:
                reload_counter2 += 1
            elif value == 1:
                grenade_counter2 += 1
            elif value == 2:
                shield_counter2 += 1
            elif value == 3:
                logout_counter2 += 1
            elif value == 4:
                none_counter2 += 1
        
        if grenade_counter2 > shield_counter2 and grenade_counter2 > reload_counter2 and grenade_counter2 > logout_counter2 and grenade_counter2 > none_counter2:
            return "grenade"
        if shield_counter2 > grenade_counter2 and shield_counter2 > reload_counter2 and shield_counter2 > logout_counter2 and shield_counter2 > none_counter2:
            return "shield"
        if reload_counter2 > grenade_counter2 and reload_counter2 > shield_counter2 and reload_counter2 > logout_counter2 and reload_counter2 > none_counter2:
            return "reload"
        if logout_counter2 > grenade_counter2 and logout_counter2 > shield_counter2 and logout_counter2 > reload_counter2 and logout_counter2 > none_counter2:
            return "logout"
        return "none"

    def run(self):
        while True:
            sensor_reading = queue_ai.get()

            # unpacked_sensor_reading = unpack('<b''6h''b''3h',  sensor_reading)
            unpacked_sensor_reading = unpack('<b''b''6h''b''2h''b',  sensor_reading)
            # print(f"AI HAS RECEIVED SENSOR READING {unpacked_sensor_reading}")

            # Updated with Player ID 
            if len(unpacked_sensor_reading) != 12:
                print('Wrong packet received! The length of the packet is ',len(unpacked_sensor_reading))
                continue
            player = unpacked_sensor_reading[1]

            # Added a delay thread for shoot to acocunt for missed shots
            if unpacked_sensor_reading[0] == 71: # GUN 71, VEST 86 or unpacked_sensor_reading[0] == 86
                action = f"{player} shoot" # Thread for each player
                delay_shoot = Timer(0.3, queue_game_state.put, args=(action,))
                delay_shoot.daemon = True
                delay_shoot.start()

            elif unpacked_sensor_reading[0] == 86:
                action = f"{player} hit"
                queue_game_state.put(action)

            elif unpacked_sensor_reading[0] == 87: # IMU 87
                # global imu_time
                # global length
                # imu_time = time.time()

                # Modify the positions as added a new byte to indicate player
                if player == 1:
                    if len(self.x1) != 50:
                        self.x1.append(unpacked_sensor_reading[2]) 
                        self.y1.append(unpacked_sensor_reading[3]) 
                        self.z1.append(unpacked_sensor_reading[4]) 
                        self.gx1.append(unpacked_sensor_reading[5]) 
                        self.gy1.append(unpacked_sensor_reading[6]) 
                        self.gz1.append(unpacked_sensor_reading[7])
                    else:
                        print("Error, sensor data FULL")
                else:
                    if len(self.x2) != 50:
                        self.x2.append(unpacked_sensor_reading[2]) 
                        self.y2.append(unpacked_sensor_reading[3]) 
                        self.z2.append(unpacked_sensor_reading[4]) 
                        self.gx2.append(unpacked_sensor_reading[5]) 
                        self.gy2.append(unpacked_sensor_reading[6]) 
                        self.gz2.append(unpacked_sensor_reading[7])
                    else:
                        print("Error, sensor data FULL")

                if (len(self.x1) == 50):
                    
                    action = self.ai()
                    
                    if action == "grenade":
                        self.grenade_counter += 1
                    elif action == "shield":
                        self.shield_counter += 1
                    elif action == "reload":
                        self.reload_counter += 1
                    elif action == "logout":
                        self.logout_counter += 1

                    self.x1 = self.x1[1:50]
                    self.y1 = self.y1[1:50]
                    self.z1 = self.z1[1:50]
                    self.gx1 = self.gx1[1:50]
                    self.gy1 = self.gy1[1:50]
                    self.gz1 = self.gz1[1:50]

                if (len(self.x2) == 50):
                    
                    action = self.ai2()
                    
                    if action == "grenade":
                        self.grenade_counter2 += 1
                    elif action == "shield":
                        self.shield_counter2 += 1
                    elif action == "reload":
                        self.reload_counter2 += 1
                    elif action == "logout":
                        self.logout_counter2 += 1

                    self.x2 = self.x2[1:50]
                    self.y2 = self.y2[1:50]
                    self.z2 = self.z2[1:50]
                    self.gx2 = self.gx2[1:50]
                    self.gy2 = self.gy2[1:50]
                    self.gz2 = self.gz2[1:59]
                
                if self.grenade_counter > 5:

                    self.grenade_counter = 0
                    self.shield_counter = 0
                    self.reload_counter = 0
                    self.logout_counter = 0
                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()

                    pred_action = f"1 grenade"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action) # grenade
                    '''   
                    # is_hit = queue_greande_hit_or_miss.get()
                        
                    # For Testing
                    is_hit = "t"
                        
                    if is_hit == "t":
                        hit_action = f"2 hit_G"
                        queue_game_state.put(hit_action)
                    '''
                elif self.reload_counter > 5:

                    self.grenade_counter = 0
                    self.shield_counter = 0
                    self.reload_counter = 0
                    self.logout_counter = 0
                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()

                    pred_action = f"1 reload"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)

                elif self.shield_counter > 5:

                    self.grenade_counter = 0
                    self.shield_counter = 0
                    self.reload_counter = 0
                    self.logout_counter = 0
                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()

                    pred_action = f"1 shield"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)
                
                elif self.logout_counter > 5:

                    self.grenade_counter = 0
                    self.shield_counter = 0
                    self.reload_counter = 0
                    self.logout_counter = 0
                    self.x1.clear()
                    self.y1.clear()
                    self.z1.clear()
                    self.gx1.clear()
                    self.gy1.clear()
                    self.gz1.clear()

                    pred_action = f"1 logout"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)

                if self.grenade_counter2 > 5:

                    self.grenade_counter2 = 0
                    self.shield_counter2 = 0
                    self.reload_counter2 = 0
                    self.logout_counter2 = 0
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

                    pred_action = f"2 grenade"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action) # grenade
                    ''' 
                    # is_hit = queue_greande_hit_or_miss.get()
                        
                    # For Testing
                    is_hit = "t"
                        
                    if is_hit == "t":
                        hit_action = f"1 hit_G"
                        queue_game_state.put(hit_action)
                    '''
                elif self.reload_counter2 > 5:

                    self.grenade_counter2 = 0
                    self.shield_counter2 = 0
                    self.reload_counter2 = 0
                    self.logout_counter2 = 0
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

                    pred_action = f"2 reload"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)

                elif self.shield_counter2 > 5:

                    self.grenade_counter2 = 0
                    self.shield_counter2 = 0
                    self.reload_counter2 = 0
                    self.logout_counter2 = 0
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

                    pred_action = f"2 shield"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)
                
                elif self.logout_counter2 > 5:

                    self.grenade_counter2 = 0
                    self.shield_counter2 = 0
                    self.reload_counter2 = 0
                    self.logout_counter2 = 0
                    self.x2.clear()
                    self.y2.clear()
                    self.z2.clear()
                    self.gx2.clear()
                    self.gy2.clear()
                    self.gz2.clear()

                    pred_action = f"2 logout"
                    print(f'{Fore.MAGENTA}[AI CLASSIFICATION] {pred_action}{Style.RESET_ALL}')
                    queue_game_state.put(pred_action)
                

relay = Relay()
ai = AI()
t1 = threading.Thread(target=relay.run, args=())
t2 = threading.Thread(target=ai.run, args=())
t1.start()
t2.start()
t1.join()
t2.join()